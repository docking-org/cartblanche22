#!/usr/bin/env python3

import csv
import operator
import warnings


class Sink(object):
    def send(self, obj):
        raise NotImplementedError

    def put(self, obj):
        warnings.warn("Using outdated put call in Sink")
        self.send(obj)

    def record(self, obj):
        self.send(obj)
        return obj

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if hasattr(self, '_consumer'):
            self.consumer.close()
        self.close()

    def make_generator(self):
        while True:
            item = yield
            self.send(item)

    @property
    def consumer(self):
        if not hasattr(self, '_consumer'):
            self._consumer = self.make_generator()
            self._consumer.send(None)
        return self._consumer

    def consume(self, source):
        for item in source:
            self.send(item)


class TeeSink(Sink):
    def __init__(self, *sinks, **options):
        filter_first = options.pop('filter_first', True)
        filter_test = options.pop('filter_test', None)
        propagate_close = options.pop('propagate_close', True)

        if filter_first:
            sinks = filter(filter_test, sinks)
        self.sinks = sinks
        self.propagate_close = propagate_close

    def send(self, value):
        return [sink.send(value) for sink in self.sinks]

    def close(self):
        if self.propagate_close:
            for sink in self.sinks:
                sink.close()


class CsvSink(Sink):
    writer = csv.writer

    def __init__(self, sink, *args, **options):
        self._sink = sink
        append_columns = options.pop('append_columns', None)
        if not append_columns:
            append_columns = []
        self._append_columns = append_columns
        header = options.pop('header', None)
        self._writer = self.writer(self._sink, *args, **options)
        if header is not None:
            self._writer.writerow(header)

    def send(self, data):
        row = list(data)
        row += self._append_columns
        self._writer.writerow(row)


class ObjectToCsvSink(CsvSink):
    def __init__(self, sink, names, default_value=None, getter=operator.getitem, *args, **options):
        self._names = names
        self._default_value = default_value
        if getter == 'item':
            self._getter = operator.getitem
        elif getter in ('attr', 'attribute'):
            self._getter = getattr
        else:
            self._getter = getter
        if 'header' not in options:
            options['header'] = names
        super(ObjectItemsToCsvSink, self).__init__(sink, *args, **options)

    def send(self, obj):
        row = []
        for name in self._names:
            try:
                row.append(self._getter(obj, name))
            except KeyError:
                if self._default_value is not None:
                    row.append(self._default_value)
                else:
                    raise
        super(ObjectItemsToCsvSink, self).send(row)


ObjectItemsToCsvSink = ObjectToCsvSink  # Legacy


class DictToCsvSink(CsvSink):
    writer = csv.DictWriter

    def __init__(self, sink, names, default_value=None, getter=operator.getitem, *args, **options):
        self._names = names
        self._default_value = default_value
        if getter == 'item':
            self._getter = operator.getitem
        elif getter in ('attr', 'attribute'):
            self._getter = getattr
        else:
            self._getter = getter
        super(DictToCsvSink, self).__init__(sink, names, *args, **options)
        self._writer.writeheader()

    def send(self, fields):
        row = dict(self._append_columns)
        for name in self._names:
            try:
                row.setdefault(name, fields[name])
            except KeyError:
                if default_value is not None:
                    row.setdefault(self._default_value)
                else:
                    raise
        self._writer.writerow(row)


class FieldsToCsvSink(DictToCsvSink):
    def send(self, **fields):
        super(FieldsToCsvSink, self).send(fields)


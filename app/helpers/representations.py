from collections import (
    OrderedDict,
    namedtuple,
)
from io import StringIO
import datetime
import csv
import gzip
import operator
import os
import pipes


from dicttoxml import dicttoxml
from flask_jsontools import DynamicJSONEncoder

# from zinc.compat import binary_type
# from zinc.extensions.sqlalchemy.utils import limit_query_like_results
from app.helpers.utils import (
    getattr_rs,
    set_defaults,
    is_mapping,
    is_sequence,
)



class DuckTypeJsonEncoder(DynamicJSONEncoder):
    def encode(self, obj):
        super_encode = super(DuckTypeJsonEncoder, self).encode
        try:
            return super_encode(obj)
        except TypeError:
            try:
                return super_encode(self.default(obj))
            except TypeError:
                pass
            raise

    def _is_json_scalar(self, obj):
        return isinstance(obj, (str, int, float)) \
               or obj is (None, True, False)

    def _handle_dict(self, obj):
        val = {}
        for key, value in list(obj.items()):
            attr = self.default(key)
            if not self._is_json_scalar(attr):
                attr = str(key)
            val[attr] = self.default(value)
        return val

    def _handle_default_projection_objects(self, obj):
        cls = type(obj)
        fields = None
        if hasattr(cls, '__structured_view_attrs__'):
            fields = cls.__structured_view_attrs__
        elif hasattr(cls, '__default_view_attrs__'):
            fields = cls.__default_view_attrs__

        if fields is not None:
            proj = {}
            for key in fields:
                value = self.default(getattr(obj, key))
                attr = self.default(key)
                if not self._is_json_scalar(attr):
                    attr = str(key)

                proj[attr] = self.default(value)
            return proj
        else:
            raise TypeError()

    def _handle_special_types(self, obj):
        # Always respect __json__ method
        if hasattr(obj, '__json__'):
            return obj.__json__()

        # Then delegate to scalar values that can be handled internally
        elif self._is_json_scalar(obj):
            return obj

        # Dates can be cast using explicit formats
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat(' ')
        elif isinstance(obj, datetime.date):
            return obj.isoformat()

        # Sequences should be expanded and items handled here or they may raise
        elif is_sequence(obj) or isinstance(obj, set):
            return [self.default(item) for item in obj]

        # Sequences should be expanded and items handled here or they may raise
        elif is_mapping(obj):
            return self._handle_dict(obj)

        raise TypeError("No special type handling for {!r}".format(type(obj)))


    def default(self, obj):
        # Custom formats
        try:
            return self._handle_special_types(obj)
        except TypeError:
            pass

        try:
            return self._handle_default_projection_objects(obj)
        except TypeError:
            pass

        if hasattr(obj, '__str__'):
            try:
                return str(obj)
            except TypeError:
                pass

        return super(DuckTypeJsonEncoder, self).default(obj)


class FormatterError(ValueError):
    pass


class InvalidFormatterOptions(FormatterError):
    pass


def make_list_wrapper(fields, name='result_wrapper'):
    wrapper = namedtuple(name, fields)
    return wrapper


# def expand_lazy_queries(data, wrapper=list, limit=1000):
#     return [(k, limit_query_like_results(v, wrapper=wrapper, max_results=limit)) for k, v in data]


def extract_fields(obj, fields, getter=getattr_rs):
    if is_sequence(obj) and (not fields or len(obj) == len(fields)):
        if fields:
            data = list(zip(fields, obj))
        else:
            data = list(zip(list(range(len(obj))), obj))
    elif is_mapping(obj):
        data = [(key, obj[key]) for key in fields]
    else:
        data = []
        for field in fields:
            try:
                value = getter(obj, field)
            except Exception:
                raise
            item = (field, value)
            data.append(item)

    # # Extract lazy queries
    # data = expand_lazy_queries(data, wrapper=list, limit=1000)

    return OrderedDict(data)



def iterated(formatter):
    return IteratedOutput.construct_wrapped(formatter)


def buffer_consumer(buffer_cls):
    def gen(results, *args, **kwargs):
        buf = buffer_cls(*args, **kwargs)
        it = iter(results)
        for result in it:
            yield buf(result)
        yield buf.close(**kwargs)
    return gen

def string_to_bool(value):
    return value.lower() not in ('no', 'off', 'false', 'none')

DEFAULT_OPTION_CASTS = {
    'header': string_to_bool,
}


def setup_options(raw_options, defaults, casts=DEFAULT_OPTION_CASTS):
    casts = casts or {}
    options = defaults.copy()
    if raw_options:
        for key, value in list(raw_options.items()):
            if key in casts:
                value = casts[key](value)
            options[key] = value
    return options



class BufferedOutput(object):

    def __init__(self, max_calls=1, max_size=None, buffer=None):
        self.buffer = buffer or StringIO()
        self.max_calls = max_calls
        self.max_size = max_size
        self.num_calls = 0

    def should_flush(self):
        if self.num_calls < self.max_calls:
            return False
        elif self.max_size is not None and self.buffer.tell() < self.max_size:
            return False
        else:
            return True

    def reset(self):
        self.num_calls = 0
        self.buffer.truncate(0)

    def flush(self):
        return self.buffer.getvalue()

    def get_current_value(self, force_flush=False):
        if self.should_flush() or force_flush:
            value = self.flush()
            self.reset()
            return value.strip('\x00')
        else:
            return ''

    def buffered_write(self, data):
        self.buffer.write(data)

    def write(self, data, force_flush=False):
        self.num_calls += 1
        self.buffered_write(data)
        return self.get_current_value(force_flush=force_flush)

    def __call__(self, data, single=False):
        return self.write(data, force_flush=single)

    def close(self, **kwargs):
        return self.get_current_value(force_flush=True)

    @classmethod
    def construct_consumer(cls, *args, **kwargs):
        buf = cls(*args, **kwargs)
        def wrapper(results):
            it = iter(results)
            for result in it:
                yield buf(result)
        return wrapper


class GzipCompressedOutput(BufferedOutput):
    def __init__(self, max_calls=10, max_size=None, compression=9):
        super(GzipCompressedOutput, self).__init__(max_calls=max_calls, max_size=max_size)
        self.compressor = gzip.GzipFile(mode='w', fileobj=self.buffer, compresslevel=compression)

    def buffered_write(self, data):
        self.compressor.write(data)

    def flush(self):
        self.compressor.flush()
        return super(GzipCompressedOutput, self).flush()

    def close(self, **kwargs):
        self.compressor.flush()
        self.compressor.close()
        value = self.buffer.getvalue()
        self.reset()
        return value


class IteratedOutput(object):
    def __init__(self, formatter, flush=True, free=True, buffer_first=True):
        self._formatter = formatter
        self.flush = flush
        self.free = free
        self.buffer_first = buffer_first

    def format_single(self, item):
        return self.format(item, single=True)

    def format(self, obj, single=False):
        return self._formatter(obj, single=single)

    def set_error(self, error):
        self._formatter.set_error(error)

    @property
    def error(self):
        return getattr(self._formatter, 'error', None)

    def __call__(self, data, single=False):
        start = getattr(self._formatter, 'open', lambda *args, **kwargs: None)
        finish = getattr(self._formatter, 'close', lambda *args, **kwargs: None)

        try:
            it = iter(data)
        except TypeError:
            if single:
                it = iter([data])
            else:
                raise
        start_result = start(single=single)
        if self.buffer_first:
            try:
                first = next(it)
            except StopIteration:
                if start_result is not None:
                    yield start_result
            else:
                if start_result is not None:
                    yield ''.join([start_result, self.format(first, single=single)])
                else:
                    yield self.format(first, single=single)
        else:
            yield start_result

        for item in it:
            yield self.format(item, single=single)

        end_result = finish(single=single)
        if end_result is not None:
            yield end_result

    def _get(self, item, single=False):
        result = self.format(item, single=single)
        if self.free:
            del item

    @classmethod
    def construct_wrapped(cls, formatter):
        def build(*args, **kwargs):
            return cls(formatter(*args, **kwargs))
        return build


class GzipIterator(IteratedOutput, GzipCompressedOutput):
    def __init__(self, formatter, flush=True, free=True, max_calls=10, max_size=None):
        IteratedOutput.__init__(self, formatter, flush=flush, free=free)
        GzipCompressedOutput.__init__(self, max_calls=max_calls, max_size=max_size)

    def format(self, obj, single=False):
        return self.write(self._formatter(obj, single=single), force_flush=single)


class TextFormatter(object):
    def __init__(self, template="{0}{end}", process=None, params=None):
        self._params = {'end': os.linesep}
        if params:
            self._params.update(**params)
        self._template = template
        self._process = process or (lambda x: [x])
        self.error = None

    @property
    def template(self):
        return self._template

    @property
    def params(self):
        return self._params

    @property
    def process(self):
        return self._process

    def set_error(self, error):
        self.error = error

    def __call__(self, txt):
        return self.template.format(*self.process(txt), **self.params)


class ObjectFormatter(object):
    def __init__(self, fields, extractor=extract_fields):
        self.fields = fields
        self.extractor = extractor
        self.error = None

    def _get_requested_data(self, obj):
        return self.extractor(obj, self.fields)

    def set_error(self, error):
        self.error = error


class PropertyFormatter(ObjectFormatter):
    def __init__(self, fields, extractor=None):
        if len(fields) != 1:
            raise ValueError("PropertyFormatter can only format 1 and only 1 property")
        if extractor is not None:
            raise ValueError("Cannot define extractor for PropertyFormatter")
        extractor = operator.attrgetter(fields[0])
        super(PropertyFormatter, self).__init__(fields, extractor=extractor)

    def _get_requested_data(self, obj):
        return self.extractor(obj)

    def __call__(self, obj):
        return self._get_requested_data(obj)


class CsvOutputBuffer(ObjectFormatter, BufferedOutput):
    OPTIONS = {
        'header': True,
        'joiner': ';',
    }
    CSV_OPTIONS = ('delimiter', 'line_terminator', 'quotechar', 'quoting')

    def __init__(self, fields, options=None, extractor=extract_fields, **buffer_args):
        ObjectFormatter.__init__(self, fields=fields, extractor=extractor)
        BufferedOutput.__init__(self, **buffer_args)
        options = options or {}
        self.options = setup_options(options, self.OPTIONS, casts=DEFAULT_OPTION_CASTS)
        joiner = options.pop('joiner', None)
        if not joiner or joiner == '' or joiner.lower() == 'none':
            joiner = None
        options['joiner'] = joiner
        csv_kwargs = {k:v for k, v in list(self.options.items()) if k in self.CSV_OPTIONS}
        self.writer = csv.DictWriter(self.buffer, fields, **csv_kwargs)
        if self.options.get('header', True):
            self.writer.writeheader()

    def _join_sequences(self, data):
        if 'joiner' in self.options is not None:
            for field, value in list(data.items()):
                if is_mapping(value):
                    value = ['{!s}={!s}'.format(*kv) for kv in list(value.items())]
                if is_sequence(value):
                    value = [str(v) for v in value]
                    value = self.options['joiner'].join(value)
                data[field] = value
        return data

    def _remove_special_chars(self, data):
        for field, value in list(data.items()):
            if isinstance(value, str):
                value = value.replace(self.options['delimiter'], '')
                value = value.replace(self.options['line_terminator'], '')
                value = value or self.options['joiner'] or ' '
                data[field] = value
        return data

    def _get_requested_data(self, obj):
        data = super(CsvOutputBuffer, self)._get_requested_data(obj)
        data = self._join_sequences(data)
        return data

    def buffered_write(self, data):
        fields = self._get_requested_data(data)
        escape = lambda value: value if isinstance(value, str) else str(value)
        fields = {key: escape(value) for key, value in list(fields.items())}
        self.writer.writerow(fields)


class CsvFormatter(CsvOutputBuffer):
    OPTIONS = {}


class TxtFormatter(CsvOutputBuffer):
    OPTIONS = {
        'delimiter': '\t',
        'line_terminator': '\n',
        'quotechar': '',
        'header': False,
        'quoting': csv.QUOTE_NONE,
        'joiner': ' ',
    }

    def _get_requested_data(self, obj):
        data = super(TxtFormatter, self)._get_requested_data(obj)
        data = self._remove_special_chars(data)
        return data


class JsonStreamFormatter(ObjectFormatter):
    def __init__(self, fields, options=None, extractor=extract_fields, delimiter="\n"):
        ObjectFormatter.__init__(self, fields=fields, extractor=extractor)
        self.formatter = "{}"+delimiter
        self.encoder = DuckTypeJsonEncoder()

    def open(self, single=False):
        return ''

    def __call__(self, data, single=False):
        properties = self._get_requested_data(data)
        encoded = self.encoder.encode(properties)
        formatted = self.formatter.format(encoded)
        return formatted

    def close(self, single=False):
        return ''


class JsonFormatter(JsonStreamFormatter):
    def __init__(self, fields, options=None, extractor=extract_fields):
        super(JsonFormatter, self).__init__(fields, extractor, delimiter="")
        options = options or {}
        self.as_object = options.get('wrap', 'array').lower().strip() == 'object'
        self.buffer = None

    def open(self, single=False):
        opening = ''
        if not single:
            opening = '['
        if self.as_object:
            opening = '{"data": ' + opening
        return opening

    def __call__(self, data, single=False):
        rendered = super(JsonFormatter, self).__call__(data, single=single)
        if single:
            return rendered
        previous = self.buffer
        if previous is None:
            self.buffer, chunk = rendered, ""
        else:
            self.buffer, chunk = ",{}".format(rendered), previous
        return chunk

    def close(self, single=False):
        previous = self.buffer
        self.buffer = None
        result = []
        if previous is not None:
            result.append(previous)

        if not single:
            result.append(']')
        if self.as_object:
            if self.error:
                result.append(', "error": {}'.format(self.encoder.encode(self.error)))
            result.append('}')

        return ''.join(result)


class JsonPFormatter(JsonFormatter):
    def __init__(self, fields, options=None, extractor=extract_fields):
        options = options or {}
        super(JsonPFormatter, self).__init__(fields=fields, options=options, extractor=extractor)
        callback = options.get('callback', 'callback')
        if not callback.replace('$', '').replace('_','').replace('.','').isalnum():
            raise InvalidFormatterOptions("Invalid JSONP Callback: {}".format(callback))
        self.callback = callback

    def open(self, single=False):
        data_open = super(JsonPFormatter, self).open(single=single)
        opening = '{}({}'.format(self.callback, data_open)
        return opening

    def close(self, single=False):
        closing = super(JsonPFormatter, self).close(single=single)
        return '{})'.format(closing)


class SinglePropertyFormatter(PropertyFormatter):
    ATTRIBUTE_NAME = None
    ATTRIBUTE_SEARCH = []

    OPTIONS = {'strict': False}
    CASTS = {'strict': string_to_bool}

    def __init__(self, fields, options=None):
        self.options = setup_options(options, self.OPTIONS, self.CASTS)
        if not self.options.get('strict', False):
            fields = [self.ATTRIBUTE_NAME]
        super(SinglePropertyFormatter, self).__init__(fields=fields)

    def _get_requested_data(self, obj):
        if hasattr(obj, self.ATTRIBUTE_NAME):
            data = getattr(obj, self.ATTRIBUTE_NAME) or ''
            return data
        else:
            for related in self.ATTRIBUTE_SEARCH:
                if hasattr(obj, related):
                    return os.linesep.join(getattr(item, self.ATTRIBUTE_NAME) for item in getattr(obj, related) if isinstance(getattr(item, self.ATTRIBUTE_NAME), str))
                else:
                    return ''

    def __call__(self, obj, single=False):
        return self._get_requested_data(obj)



class XmlFormatter(ObjectFormatter):
    OPTIONS = {
        'root': None,
    }

    def __init__(self, fields, options=None, extractor=extract_fields):
        ObjectFormatter.__init__(self, fields=fields, extractor=extractor)
        self.options = setup_options(options, self.OPTIONS, casts=DEFAULT_OPTION_CASTS)
        self.buffer = None

    def get_result_tag_name(self, data):
        return type(data).__name__.lower()

    def get_root_tag_name(self, data):
        root = self.options.get('root')
        if root is None:
            result_tag = self.get_result_tag_name(data)
            root_tag = '{}-list'.format(result_tag)
            self.options['root'] = root_tag
        return self.options['root']

    def format(self, data):
        name = self.get_result_tag_name(data)
        properties = self._get_requested_data(data)
        wrapped = {name: properties}
        return dicttoxml(wrapped, root=False)

    def open(self, single=False):
        return ''

    def __call__(self, data, single=False):
        previous = self.buffer

        if previous is None:
            root = self.get_root_tag_name(data)
            rendered = self.format(data)
            self.buffer = "<{0}>\n{1}".format(root, rendered)
            return ""
        else:
            rendered = self.format(data)
            self.buffer = "\n{}".format(rendered)
            return previous

    def close(self, single=False):
        previous = self.buffer
        self.buffer = None
        if previous is not None:
            root = self.options.get('root', 'results')  # Set previously
            return "{0}\n</{1}>".format(previous, root)
        else:
            return ""


class URIFormatter(object):
    def __init__(self, base=None, **kwargs):
        self.base = base
        self.params = kwargs
        self.params.setdefault('end', os.linesep)

    def get_full_path(self, data):
        if callable(self.base):
            return self.base(data)
        elif self.base is not None:
            return os.path.join(self.base, data)
        else:
            return data

    def __call__(self, path, single=True):
        return "{uri}{end}".format(uri=self.get_full_path(path), **self.params)


class URIDownloaderFormatter(URIFormatter):

    def __init__(self, base=None, divided=True):
        self.divided = divided
        super(URIDownloaderFormatter, self).__init__(base=base)

    def get_path_args(self, data):
        return {
            'dir': pipes.quote(os.path.dirname(data)),
            'uri': pipes.quote(self.get_full_path(data)),
            'rel': pipes.quote(data),
            'base': pipes.quote(os.path.basename(data))
        }


class WgetDownloader(URIDownloaderFormatter):
    def __call__(self, path, single=True):
        params = self.get_path_args(path)
        set_defaults(params, self.params)
        if self.divided:
            return "mkdir -pv {dir} && wget {uri} -O {rel}{end}".format(**params)
        else:
            return "wget {uri} -O {base}{end}".format(**params)


class CurlDownloader(URIDownloaderFormatter):
    def __call__(self, path, single=True):
        params = self.get_path_args(path)
        set_defaults(params, self.params)
        if self.divided:
            return "curl --remote-time --fail --create-dirs -o {rel} {uri}{end}".format(**params)
        else:
            return "curl --remote-time --fail -o {base} {uri}{end}".format(**params)


class PowerShellDownloader(URIDownloaderFormatter):
    def __call__(self, path, single=True):
        params = self.get_path_args(path)
        set_defaults(params, self.params)
        if self.divided:
            return "New-Item -path {dir} -type directory; Invoke-WebRequest {uri} -OutFile {rel}{end}".format(**params)
        else:
            return "Invoke-WebRequest {uri} -OutFile {rel}{end}".format(**params)


OBJECT_EXTENSION_LABELS = OrderedDict([
    ('csv', 'CSV'),
    ('txt', 'Tab-Delimited'),
    ('json', 'JSON'),
    ('xml', 'XML'),
])


BASIC_EXTENSION_TO_MIMETYPE = {
    'csv': 'text/csv',
    'txt': 'text/plain',
    'json': 'application/json',
    'js': 'application/javascript',
    'ldjson': 'application/x-ldjson',
    'xml': 'application/xml',
}


OBJECT_EXTENSION_TO_MIMETYPE = BASIC_EXTENSION_TO_MIMETYPE

URI_EXTENSION_TO_MIMETYPE = {
    'uri': 'text/uri-list',
    'database_index': 'text/x-ucsf-dock-database_index',
    'curl': 'application/x-ucsf-zinc-uri-downloadscript-curl',
    'wget': 'application/x-ucsf-zinc-uri-downloadscript-wget',
    'powershell': 'application/x-ucsf-zinc-uri-downloadscript-powershell',
}

COMPRESSION_EXTENSION_TO_MIMETYPE = {
    'gz': 'multipart/x-gzip',
}


OBJECT_MIMETYPE_TO_FORMATTER = OrderedDict([
    ('application/json', iterated(JsonFormatter)),
    ('text/json', iterated(JsonFormatter)),
    ('application/javascript', iterated(JsonPFormatter)),
    ('application/x-ldjson', iterated(JsonStreamFormatter)),
    ('application/xml', iterated(XmlFormatter)),
    ('text/csv', iterated(CsvFormatter)),
    ('text/plain', iterated(TxtFormatter)),
])

URI_MIMETYPE_TO_FORMATTER = OrderedDict([
    ('text/uri-list', iterated(URIFormatter)),
    ('text/x-ucsf-dock-database_index', iterated(URIFormatter)),
    ('application/x-ucsf-zinc-uri-downloadscript-curl', iterated(CurlDownloader)),
    ('application/x-ucsf-zinc-uri-downloadscript-wget', iterated(WgetDownloader)),
    ('application/x-ucsf-zinc-uri-downloadscript-powershell', iterated(PowerShellDownloader)),
])

COMPRESSION_MIMETYPE_TO_FORMATTER = OrderedDict([
    ('multipart/x-gzip', buffer_consumer(GzipCompressedOutput)),
])


OBJECT_EXTENSION_TO_MIMETYPE_AND_FORMATTER = {ext:(mt,OBJECT_MIMETYPE_TO_FORMATTER[mt])
                                              for ext, mt in list(OBJECT_EXTENSION_TO_MIMETYPE.items())}


def object_formatter(fmt, *args, **kwargs):
    if fmt in OBJECT_EXTENSION_TO_MIMETYPE:
        fmt = OBJECT_EXTENSION_TO_MIMETYPE[fmt]
    fmt_class = OBJECT_MIMETYPE_TO_FORMATTER[fmt]
    formatter = fmt_class(*args, **kwargs)
    return formatter

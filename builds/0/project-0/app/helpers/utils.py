from __future__ import  absolute_import

import bisect
import collections
import itertools
import functools
import logging
import inspect
import operator
import gc
import os
import types
from werkzeug.utils import secure_filename
from werkzeug.datastructures import MultiDict, CombinedMultiDict


try:
    os_O_BINARY = os.O_BINARY
except AttributeError:
    os_O_BINARY = 0


try:
    from functools import memoize
except ImportError:
    def memoize(fn):
        cache = {}
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            key = tuple(args) + tuple(kwargs.items())
            if key not in cache:
                cache[key] = fn(*args, **kwargs)
            return cache[key]
        return wrapper

from flask import current_app


NO_DEFAULT = object()


def labeled_return(*field_names, **kwargs):

    def wrapper(fn):
        typename = kwargs.pop('_typename', None) or '{}_result'.format(fn.__name__)
        verbose = kwargs.pop('_verbose', False)
        rename = kwargs.pop('_rename', False)
        cls = collections.namedtuple(typename, field_names, rename=rename)

        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            result = fn(*args, **kwargs)
            if not isinstance(result, (tuple, cls)):
                result = (result,)
            result = cls(*result)
            return result

        setattr(wrapped, 'labeled_result_class', cls)
        return wrapped

    return wrapper


def is_sequence(arg, allow_mappings=False, allow_strings=False):
    if is_mapping(arg):
        return allow_mappings
    elif isinstance(arg, str):
        return allow_strings
    elif hasattr(arg, '__iter__') or hasattr(arg, '__next__'):
        return hasattr(arg, "__getitem__") or hasattr(arg, '__len__')
    elif inspect.isgenerator(arg):
        return True
    elif inspect.isgeneratorfunction(arg):
        return True
    else:
        return False


def is_mapping(arg):
    return (
        isinstance(arg, dict) or
        (
            hasattr(arg, 'items') and
            hasattr(arg, 'setdefault') and
            hasattr(arg, 'update') and
            hasattr(arg, 'keys') and
            hasattr(arg, 'values')
        )
    )


class HashableDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class HidingDictMixin(object):
    def hiding(self, *keys):
        return type(self)((k,v) for k, v in self.items() if k not in keys)

    def including(self, **items):
        new = type(self)(self)
        new.update(**items)
        return new

    def select(self, *keys):
        return type(self)((k, v) for k, v in self.items() if k in keys)

    def filter(self, fn):
        return type(self)((k, v) for k, v in self.items() if fn(k, v))

    def set_defaults(self, defaults):
        return set_defaults(self, defaults)


class HidingSequence(object):
    def hiding(self, *keys):
        return type(self)(item for item in self if item not in keys)

    def including(self, *items):
        return type(self)(list(self) + list(items))


class HidingDict(HidingDictMixin, dict):
    pass


class HidingList(HidingSequence, list):
    pass


def getitem(obj, key, default=NO_DEFAULT):
    try:
        return operator.getitem(obj, key)
    except (KeyError, IndexError):
        if default is not NO_DEFAULT:
            return default
        else:
            raise


def bind_current_app_setting(key, default=None):
    return lambda: current_app.config.get(key, default)


def chr_range(start, end, step=1):
    """Inclusive range of characters"""
    return list(map(chr, range(ord(start), ord(end) + 1, step)))


def cons(car, cdr):
    return itertools.chain((car,), cdr)


def combined_dict_hack(cls, d):
    cls = cls or type(d)
    if issubclass(cls, CombinedMultiDict):
        wrapper = lambda items: cls([MultiDict(items)])
    else:
        wrapper = cls
    return wrapper


def dict_from_keys(d, ks, multi=True, cls=None):
    cls = combined_dict_hack(cls, d)
    return cls([(k, v) for k, v in get_dict_items(d, multi=multi) if k in ks])


def select_dict_from_defaults(d, defaults, multi=True, cls=None):
    selected = dict_from_keys(d, defaults.keys(), multi=multi, cls=cls)
    with_defaults = set_defaults(selected, defaults)
    return with_defaults


def filter_dict(d, fn, multi=True, cls=None):
    cls = combined_dict_hack(cls, d)
    return cls([(k, v) for k, v in get_dict_items(d, multi=multi) if fn(k, v)])


def remap_dict_from_keys(d, ks, multi=True, cls=None):
    cls = combined_dict_hack(cls, d)
    return cls([(k, d[v]) for k, v in get_dict_items(ks, multi=multi) if v in d])


def set_defaults(d, other=None, **others):
    other = other or {}
    others.update(other)
    for k, v in others.items():
        d.setdefault(k, v)
    return d


def set_defaults_recursive(d, other, max_depth=None):
    next_depth = None if max_depth is None else max_depth - 1
    for k, v in other.items():
        d.setdefault(k, v)
        if isinstance(d[k], dict) and (max_depth is None or next_depth > 0):
            set_defaults_recursive(d[k], v)
    return d


def get_dict_items(items, multi=True):
    if multi and hasattr(items, 'lists'):
        items = items.items(multi=True)
    elif hasattr(items, 'items'):
        items = items.items()
    elif is_sequence(items):
        items = list(items)
    else:
        items = [items]
    return items


def getattr_r(root, path, get=getattr):
    branch = root
    for step in path:
        branch = get(branch, step)
    leaf = branch
    return leaf

def getattr_rs(obj, path, delimiter='.', get=getattr):
    return getattr_r(obj, path.split(delimiter), get=get)


class GetAttrRMixin(object):
    GET_ATTR_RS_DELIMITER = '.'
    GET_ATTR_R_GETTER = getattr

    def __getattr__(self, item):
        items = item.split(self.GET_ATTR_RS_DELIMITER)
        if len(items) > 1:
            return getattr_r(self, items, get=self.GET_ATTR_R_GETTER)
        else:
            raise AttributeError("{!r} object has no attribute {!r}".format(type(self).__name, item))


def slices(*args):
    selectors = []
    for arg in args:
        if isinstance(arg, (list, tuple)):
            selectors.append(slice(*arg))
        else:
            selectors.append(arg)
    return selectors


def selectors(*args):
    return lambda seq: [seq[sel] for sel in slices(*args)]


def box_as_sequence(obj, boxed=(tuple, list, set, types.GeneratorType), sequence=None):
    sequence = sequence or (lambda x: x)
    if isinstance(obj, boxed):
        return sequence(obj)
    else:
        return sequence([obj])


def to_namedtuple(d, __fields=(), __name='namedtuple', __exclude=(), **kwargs):
    d = d.copy()
    d.update(**kwargs)
    if __fields:
        for key in list(d.keys()):
            if key not in __fields:
                del d[key]
    else:
        __fields = d.keys()

    for key in __exclude:
        del d[key]

    new = collections.namedtuple(__name, __fields)(**d)
    return new


def clone_namedtuple(t, __fields=None, __name=None, __exclude=(), **kwargs):
    __name = __name or type(t).__name__
    new = to_namedtuple(t._asdict(), __name=__name, __fields=__fields, __exclude=__exclude, **kwargs)
    return new


class IteratorWrapper(object):
    NO_PEEK = object()

    def __init__(self, source):
        self._source = source
        self._running = None
        self._peek = self.NO_PEEK
        self._it = None
        self._construction_kwargs = {}

    def reconstruct(self, new):
        cls = type(self)
        if hasattr(self._source, 'reconstruct'):
            source = self._source.reconstruct(new)
        else:
            source = new
        return cls(source, **self._construction_kwargs)

    def is_running(self):
        return self._running is not None

    def get_source(self):
        return self._source

    def _start(self):
        if self._it is None:
            source = self.get_source()
            if callable(self._source):
                self._running = source()
            else:
                self._running = source
            self._it = iter(source)

    def ensure_not_empty(self):
        self._start()
        try:
            self._peek = next(self._it)
            return True
        except StopIteration:
            return False

    def __iter__(self):
        self._start()
        if self._peek is not self.NO_PEEK:
            peeked = [self._peek]
            self._peek = self.NO_PEEK
        else:
            peeked = []

        chained = itertools.chain(peeked, self._it)
        it = iter(chained)

        return it

    def update_source(self, source):
        self._source = source
        self._peek = self.NO_PEEK
        self._it = None
        return source

    def __getattr__(self, item):
        return getattr(self.get_source(), item)


class GCIteratorProxy(IteratorWrapper):
    DEFAULT_GC_INTERVAL = 5000

    def __init__(self, source, gc_interval=DEFAULT_GC_INTERVAL, logger=logging):
        super(GCIteratorProxy, self).__init__(source)
        self._gc_interval = gc_interval
        self._seen = 0
        self._logger = logger
        self._collected = 0
        self._construction_kwargs.update(gc_interval=gc_interval, logger=logger)

    def __iter__(self):
        parent_iter = super(GCIteratorProxy, self).__iter__()
        for el in parent_iter:
            yield el
            self._seen += 1
            if self._gc_interval is not None and self._seen % self._gc_interval == 0:
                collected = gc.collect()
                self._collected += collected
                self._logger.debug("Remove {} objects in iterator memory collection ({} total)".format(
                    collected, self._collected))


def iterpeek(it, raise_onempty=True):
    nothing = object()
    first = next(it, nothing)
    if first is nothing:
        if raise_onempty:
            raise StopIteration
        else:
            full_it = None
    else:
        full_it = itertools.chain([first], it)

    return first, full_it


def read_or_default(source, default='', opener=open):
    try:
        if hasattr(source, 'read'):
            return source.read()
        elif isinstance(source, str):
            with opener(source) as f:
                return read_or_default(f, default=default)
        else:
            return read_or_default(str(source), default=default, opener=opener)
    except (IOError, OSError):
        if default is not NO_DEFAULT:
            return default
        else:
            raise


def first_existing_path(*paths, **kwargs):
    for path in paths:
        if os.path.exists(path):
            return path
    else:
        try:
            return kwargs.pop('default')
        except KeyError:
            raise IOError("No paths exist: {!r}".format(paths))


def sorted_index(collection, item, raise_on_not_found=True):
    idx = bisect.bisect_left(collection, item)
    if idx != len(collection) and collection[idx] == item:
        return idx
    elif raise_on_not_found:
        raise IndexError("{!r} not found in sorted collection")
    else:
        return None


# http://stackoverflow.com/questions/22078621/python-how-to-copy-files-fast
def copy_file(source, destination,
              buffer_size = 256 * 1024,
              rflags=os.O_RDONLY | os_O_BINARY,
              wflags=os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os_O_BINARY):
    reader = None
    writer = None

    try:
        reader = os.open(source, rflags)
        mode = os.fstat(reader).st_mode
        writer = os.open(destination, wflags, mode)
        read_chunks = functools.partial(os.read, reader, buffer_size)

        for chunk in iter(read_chunks, ""):
            os.write(writer, chunk)

    finally:
        for handle in (reader, writer):
            if handle is not None:
                try:
                    os.close(handle)
                except Exception:
                    pass


def move_file(source, destination,
              buffer_size=128 * 1024,
              rflags=os.O_RDONLY | os_O_BINARY,
              wflags=os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os_O_BINARY):
    source_device = os.stat(source).st_dev
    destination_device = os.stat(os.path.dirname(destination)).st_dev

    if source_device == destination_device:
        os.rename(source, destination)
    else:
        copy_file(
            source,
            destination,
            buffer_size=buffer_size,
            rflags=rflags,
            wflags=wflags
        )
        os.unlink(source)

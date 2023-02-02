# from __future__ import print_function
#
# from collections import OrderedDict
# from contextlib import closing
# from cStringIO import StringIO
# import itertools
# import json
#
# from dicttoxml import dicttoxml
# from app.helpers.sinks import ObjectToCsvSink
#
# from query_lib import getattr_rs
#
#
# def extract_fields(obj, fields, getter=getattr_rs):
#     return OrderedDict((field, getter(obj, field)) for field in fields)
#
#
# def find_structure(data, depth=2):
#     if data is None:
#         return None
#
#     structure = None
#     if hasattr(data, 'structure'):
#         structure = data.structure
#     if structure is None and hasattr(data, 'substance') and depth > 0:
#         structure = find_structure(data.substance, depth=depth - 1)
#
#     return structure
#
#
# def find_mol(data, depth=2):
#     if data is None:
#         return None
#
#     mol = None
#     if hasattr(data, 'mol3d'):
#         mol = data.mol3d
#     elif hasattr(data, 'mol2d'):
#         mol = data.mol2d
#
#     if mol is None and depth > 0:
#         structure = find_structure(data, depth=depth - 1)
#         mol = find_mol(structure, depth=depth - 1)
#
#     return mol
#
#
# class BufferedOutput(object):
#
#     def __init__(self):
#         self.buffer = StringIO()
#
#     def __call__(self, data):
#         self.buffered_write(data)
#         written = self.buffer.getvalue()
#         self.buffer.truncate(0)
#         return written
#
#     def close(self):
#         pass
#
#
# class IteratedOutput(object):
#     def __init__(self, formatter, flush=True):
#         self.format = formatter
#         self.flush = flush
#
#     def __call__(self, data):
#         yield ""
#         for item in data:
#             yield self.format(item)
#         finish = getattr(self.format, 'close', lambda: None)
#         end_result = finish()
#         if end_result is not None:
#             yield end_result
#
#     @classmethod
#     def construct_wrapped(cls, formatter):
#         def build(*args, **kwargs):
#             return cls(formatter(*args, **kwargs))
#
#         return build
#
#
# class CsvOutputBuffer(BufferedOutput):
#     OPTIONS = {}
#
#     def __init__(self, fields, getter=getattr_rs):
#         super(CsvOutputBuffer, self).__init__()
#         self.options = dict(self.OPTIONS.items())
#         self.options.setdefault('header', fields)
#         self.options.setdefault('getter', getter)
#         self.writer = ObjectToCsvSink(self.buffer, fields, **self.options)
#
#     def buffered_write(self, data):
#         self.writer.send(data)
#
#
# class CsvFormatter(CsvOutputBuffer):
#     OPTIONS = {}
#
#
# class TxtFormatter(CsvOutputBuffer):
#     OPTIONS = {
#         'delimiter': '\t',
#         'line_terminator': '\n',
#     }
#
#
# class JsonStreamFormatter(object):
#     def __init__(self, fields, getter=getattr_rs, delimiter="\n"):
#         self.fields = fields
#         self.getter = getter
#         self.formatter = "{}" + delimiter
#
#     def __call__(self, data):
#         properties = extract_fields(data, self.fields, getter=self.getter)
#         return self.formatter.format(json.dumps(properties))
#
#     def close(self):
#         pass
#
#
# class JsonFormatter(JsonStreamFormatter):
#     def __init__(self, fields, getter=getattr_rs):
#         super(JsonFormatter, self).__init__(fields, getter, delimiter="")
#         self.buffer = None
#
#     def __call__(self, data):
#         previous = self.buffer
#         rendered = super(JsonFormatter, self).__call__(data)
#         if previous is None:
#             self.buffer = "[{}".format(rendered)
#             return ""
#         else:
#             self.buffer = ",{}".format(rendered)
#             return previous
#
#     def close(self):
#         previous = self.buffer
#         self.buffer = None
#         if previous is not None:
#             return "{}]".format(previous)
#         else:
#             return ""
#
#
# class XmlFormatter(object):
#     OPTIONS = {
#         'root_tag': 'results',
#     }
#
#     def __init__(self, fields, getter=getattr_rs):
#         self.options = self.OPTIONS.copy()
#         self.fields = fields
#         self.getter = getter
#         self.buffer = None
#
#     def get_result_tag_name(self, data):
#         return type(data).__name__.lower()
#
#     def format(self, data):
#         name = self.get_result_tag_name(data)
#         properties = extract_fields(data, self.fields, getter=self.getter)
#         wrapped = {name: properties}
#         return dicttoxml(wrapped, root=False)
#
#     def __call__(self, data):
#         previous = self.buffer
#         if previous is None:
#             root = self.options.get('root_tag', 'results')
#             rendered = self.format(data)
#             self.buffer = "<{0}>\n{1}".format(root, rendered)
#             return ""
#         else:
#             rendered = self.format(data)
#             self.buffer = "\n{}".format(rendered)
#             return previous
#
#     def close(self):
#         previous = self.buffer
#         self.buffer = None
#         if previous is not None:
#             root = self.options.get('root_tag', 'results')
#             return "{0}\n</{1}>".format(previous, root)
#         else:
#             return ""
#

# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: dev_observer/api/types/processing.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'dev_observer/api/types/processing.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\'dev_observer/api/types/processing.proto\x12!dev_observer.api.types.processing\x1a\x1fgoogle/protobuf/timestamp.proto\"N\n\x11ProcessingItemKey\x12\x18\n\x0egithub_repo_id\x18\x64 \x01(\tH\x00\x12\x15\n\x0bwebsite_url\x18\x65 \x01(\tH\x00\x42\x08\n\x06\x65ntity\"\xac\x02\n\x0eProcessingItem\x12\x41\n\x03key\x18\x01 \x01(\x0b\x32\x34.dev_observer.api.types.processing.ProcessingItemKey\x12\x38\n\x0fnext_processing\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.TimestampH\x00\x88\x01\x01\x12\x37\n\x0elast_processed\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.TimestampH\x01\x88\x01\x01\x12\x17\n\nlast_error\x18\x04 \x01(\tH\x02\x88\x01\x01\x12\x15\n\rno_processing\x18\x05 \x01(\x08\x42\x12\n\x10_next_processingB\x11\n\x0f_last_processedB\r\n\x0b_last_errorb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'dev_observer.api.types.processing_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_PROCESSINGITEMKEY']._serialized_start=111
  _globals['_PROCESSINGITEMKEY']._serialized_end=189
  _globals['_PROCESSINGITEM']._serialized_start=192
  _globals['_PROCESSINGITEM']._serialized_end=492
# @@protoc_insertion_point(module_scope)

"""Schemas package.

Contains Pydantic schemas used by the Ninja rail. The DRF rail keeps its
serializers under ``apis/drf/v1/`` because they double as binding *and*
validation classes per DRF idioms.

Both rails MUST emit the same JSON shape for a given resource so the
benchmark and the client SDK remain consistent.
"""

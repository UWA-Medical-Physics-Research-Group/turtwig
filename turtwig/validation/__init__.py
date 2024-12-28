"""
Decorators for validating function arguments.
"""

from .datatypes import MaskDict, PatientScan
from .dict import all_same_keys
from .numpy import is_ndim

__all__ = ["all_same_keys", "PatientScan", "MaskDict", "is_ndim"]

"""
Functional utilities.
"""

from .common import iterate_while, side_effect, star, starfilter, starmap
from .decorator import curry
from .dict import merge_with_reduce, rename_key
from .oop import call_method
from .parallel import pmap
from .path import (generate_full_paths, list_files, next_available_path,
                   resolve_path_placeholders)
from .sequence import growby, growby_fs, transform_nth
from .string import capture_placeholders, placeholder_matches

__all__ = [
    "star",
    "call_method",
    "starmap",
    "starfilter",
    "iterate_while",
    "list_files",
    "generate_full_paths",
    "resolve_path_placeholders",
    "growby",
    "growby_fs",
    "capture_placeholders",
    "placeholder_matches",
    "curry",
    "pmap",
    "next_available_path",
    "merge_with_reduce",
    "side_effect",
    "transform_nth",
    "rename_key",
]

"""
Functional utilities.
"""
from .common import star, starmap, starfilter, iterate_while, side_effect
from .dict import merge_with_reduce, rename_key
from .parallel import pmap
from .path import list_files, generate_full_paths, resolve_path_placeholders, next_available_path
from .sequence import growby, growby_accum, transform_nth
from .string import capture_placeholders, placeholder_matches
from .wrappers import curry
from .oop import call_method

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
    "growby_accum",
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

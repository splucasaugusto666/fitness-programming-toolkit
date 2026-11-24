"""Offline strength-training plan validation and data export."""

from .core import (
    DataValidationError,
    Program,
    export_csv,
    iter_csv_rows,
    parse_program,
    read_program,
    summarize_program,
    write_csv,
)

__all__ = [
    "DataValidationError", "Program", "parse_program", "read_program",
    "summarize_program", "iter_csv_rows", "export_csv", "write_csv",
]
__version__ = "0.1.0"

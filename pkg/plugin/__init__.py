"""Public plugin SDK exports."""

from pkg.plugin.handler import HandlerContext, HandlerResult, failure, success
from pkg.plugin.shell import ShellAdapter

__all__ = [
    "HandlerContext",
    "HandlerResult",
    "ShellAdapter",
    "failure",
    "success",
]

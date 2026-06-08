"""noop plugin handler."""

from __future__ import annotations

from pkg.plugin import HandlerContext, success


def ping(ctx: HandlerContext):
    return success(ctx, evidence={"pong": True})

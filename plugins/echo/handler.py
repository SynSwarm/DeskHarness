"""echo plugin handler."""

from __future__ import annotations

from pkg.plugin import HandlerContext, failure, success


def echo(ctx: HandlerContext):
    message = str(ctx.params.get("message") or ctx.params.get("text") or "").strip()
    if not message:
        return failure(ctx, "missing message or text param")
    return success(ctx, evidence={"message": message}, reply_text=message)

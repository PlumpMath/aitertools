async def aiter(aiterable):
    """The async version of the builtin ``iter``."""
    return await aiterable.__aiter__()


_sentinel = object()
async def anext(aiterable, default=_sentinel):
    """The async version of the builtin ``next``."""
    try:
        return await aiterable.__anext__()
    except StopAsyncIteration:
        if default is _sentinel:
            raise
        return default

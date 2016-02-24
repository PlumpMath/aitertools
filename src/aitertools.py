import asyncio
import itertools
import functools
import operator


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


def coroutine_iterator(afunc):
    class _CoroutineIteratorType(type):
        def __repr__(cls):
            return "<class '{module}.{name}'>".format(
                module=cls.__module__, name=cls.__name__)

    class CoroutineIterator(metaclass=_CoroutineIteratorType):
        def __init__(self, *args, **kwargs):
            self.__args = args
            self.__kwargs = kwargs
            self.__anext = _sentinel

        async def __aiter__(self):
            return self

        async def __anext__(self):
            if self.__anext is _sentinel:
                self.__anext = await afunc(*self.__args, **self.__kwargs)
                del self.__args, self.__kwargs
            return await self.__anext()

    CoroutineIterator.__name__ = afunc.__name__
    CoroutineIterator.__module__ = afunc.__module__
    return CoroutineIterator


@coroutine_iterator
async def to_aiter(iterable):
    iterator = iter(iterable)
    async def __anext__():
        try:
            return next(iterator)
        except StopIteration as e:
            raise StopAsyncIteration() from e
    return __anext__


def to_async(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@coroutine_iterator
async def azip(*aiterables):
    aiters = await asyncio.gather(*tuple(map(aiter, aiterables)))
    async def __anext__():
        return tuple(await asyncio.gather(*tuple(map(anext, aiterables))))
    return __anext__


@coroutine_iterator
async def schedule(aiterable, scheduler):
    azipped = azip(aiterable, scheduler)
    async def __anext__():
        value, _ = await anext(azipped)
        return value
    return __anext__


async def alist(aiterable):
    values = []
    async for value in aiterable:
        values.append(value)
    return values


async def atuple(aiterable):
    return tuple(await alist(aiterable))


def acount(start=0, step=1):
    return to_aiter(itertools.count(start, step))


@coroutine_iterator
async def acycle(aiterable):
    aiterator = await aiter(aiterable)
    completed = False
    cache = []
    async def __anext__():
        nonlocal aiterator, completed
        try:
            value = await anext(aiterator)
            if not completed:
                cache.append(value)
            return value
        except StopAsyncIteration:
            completed = True
            aiterator = to_aiter(cache)
            return await anext(aiterator)
    return __anext__


def arepeat(object, times=_sentinel):
    args = () if times is _sentinel else (times,)
    return to_aiter(itertools.repeat(object, *args))


@coroutine_iterator
async def aaccumulate(aiterable, afunc=to_async(operator.add)):
    aiterator = await aiter(aiterable)
    accumulated = _sentinel
    async def __anext__():
        nonlocal accumulated
        current = await anext(aiterator)
        if accumulated == _sentinel:
            accumulated = current
        else:
            accumulated = await afunc(accumulated, current)
        return accumulated
    return __anext__

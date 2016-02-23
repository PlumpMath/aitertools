"""Test the aitertools module."""
import pytest

import aitertools


class TestAsyncBuiltins:
    """Tests for async ports of builtin functions."""

    @pytest.mark.asyncio
    async def test_aiter(self):
        """It should await and return the __aiter__ method."""
        class MyAsyncIterable:
            async def __aiter__(self):
                return 42
        assert await aitertools.aiter(MyAsyncIterable()) == 42

    class OneValueAsync:
        done = False
        async def __aiter__(self):
            return self
        async def __anext__(self):
            if not self.done:
                self.done = True
                return 42
            raise StopAsyncIteration()

    @pytest.mark.asyncio
    async def test_anext(self):
        """It should return the next value or the sentinel."""
        aiterator = self.OneValueAsync()
        assert await aitertools.anext(aiterator) == 42
        with pytest.raises(StopAsyncIteration):
            await aitertools.anext(aiterator)

    @pytest.mark.asyncio
    async def test_anext_with_default(self):
        """It should return the next value or the sentinel."""
        aiterator = self.OneValueAsync()
        assert await aitertools.anext(aiterator, None) == 42
        assert await aitertools.anext(aiterator, None) == None

    @pytest.mark.asyncio
    async def test_alist(self):
        """It should return a list from an async iterable."""
        expected = list(range(20))
        aiterator = aitertools.to_aiter(expected)
        assert await aitertools.alist(aiterator) == expected

    @pytest.mark.asyncio
    async def test_atuple(self):
        """It should return a tuple from an async iterable."""
        expected = tuple(range(20))
        aiterator = aitertools.to_aiter(expected)
        assert await aitertools.atuple(aiterator) == expected


class TestDecorators:
    """Tests for decorator functions."""

    @pytest.mark.asyncio
    async def test_coroutine_iterator(self):
        """It should make a coroutine iterator."""
        @aitertools.coroutine_iterator
        async def one_thing():
            iterator = iter([42])
            async def __anext__():
                try:
                    return next(iterator)
                except StopIteration as e:
                    raise StopAsyncIteration()
            return __anext__

        values = []
        async for value in one_thing():
            values.append(value)

        assert values == [42]

    @pytest.mark.asyncio
    async def test_coroutine_iterator_introspection(self):
        """It should have the same name as the function."""
        @aitertools.coroutine_iterator
        async def a_strange_name():
            return

        assert a_strange_name.__name__ == 'a_strange_name'
        assert a_strange_name.__module__ == __name__
        assert repr(a_strange_name) == "<class '{module}.{name}'>".format(
            module=a_strange_name.__module__, name=a_strange_name.__name__)


class TestUtils:
    """Tests for utility functions."""

    @pytest.mark.asyncio
    async def test_to_async(self):
        """It should allow a normal function to be awaited."""
        def test_func():
            return 42

        async_test_func = aitertools.to_async(test_func)
        assert async_test_func.__name__ == test_func.__name__
        assert async_test_func.__module__ == test_func.__module__
        assert async_test_func.__doc__ == test_func.__doc__

    @pytest.mark.asyncio
    async def test_to_aiter(self):
        """It should allow a standard iterator to be used async."""
        sync_iterable = list('abcdefg')
        async_iterator = aitertools.to_aiter(sync_iterable)

        values = []
        async for value in async_iterator:
            values.append(value)
        assert values == sync_iterable


class TestAsyncItertools:
    """Tests for async ports of itertools functions."""

    @pytest.mark.asyncio
    async def test_azip(self):
        """It should zip two async iterables together."""
        one = aitertools.to_aiter(range(10))
        two = aitertools.to_aiter(reversed(range(10)))

        expected = list(zip(range(10), reversed(range(10))))
        actual = []
        async for value in aitertools.azip(one, two):
            actual.append(value)

        assert actual == expected


class TestUniqueAsyncItertools:
    """Tests for functionality new to aitertools."""

    @pytest.mark.asyncio
    async def test_schedule(self):
        """It should return the same values, and exhaust the scheduler."""
        expected = list(range(20))

        aiterator = aitertools.to_aiter(expected)
        scheduler = aitertools.to_aiter(reversed(range(20)))

        actual = []
        async for val in aitertools.schedule(aiterator, scheduler):
            actual.append(val)

        assert actual == expected
        with pytest.raises(StopAsyncIteration):
            await aitertools.anext(scheduler)

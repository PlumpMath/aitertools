"""Test the aitertools module."""
import pytest
import operator

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

    @pytest.mark.asyncio
    async def test_acount_no_args(self):
        """It should return values starting at 0."""
        aiterator = aitertools.acount()
        assert await aitertools.anext(aiterator) == 0
        assert await aitertools.anext(aiterator) == 1
        assert await aitertools.anext(aiterator) == 2
        assert await aitertools.anext(aiterator) == 3

    @pytest.mark.asyncio
    async def test_acount_one_arg(self):
        """It should return values starting at a custom value."""
        aiterator = aitertools.acount(10)
        assert await aitertools.anext(aiterator) == 10
        assert await aitertools.anext(aiterator) == 11
        assert await aitertools.anext(aiterator) == 12
        assert await aitertools.anext(aiterator) == 13

    @pytest.mark.asyncio
    async def test_acount_two_args(self):
        """It should return values with a custom start and step."""
        aiterator = aitertools.acount(100, 5)
        assert await aitertools.anext(aiterator) == 100
        assert await aitertools.anext(aiterator) == 105
        assert await aitertools.anext(aiterator) == 110
        assert await aitertools.anext(aiterator) == 115

    @pytest.mark.asyncio
    async def test_acycle(self):
        """It should cycle an aiterable."""
        aiterable = aitertools.to_aiter(list(range(3)))
        aiterator = aitertools.acycle(aiterable)
        assert await aitertools.anext(aiterator) == 0
        assert await aitertools.anext(aiterator) == 1
        assert await aitertools.anext(aiterator) == 2
        assert await aitertools.anext(aiterator) == 0
        assert await aitertools.anext(aiterator) == 1
        assert await aitertools.anext(aiterator) == 2
        assert await aitertools.anext(aiterator) == 0

    @pytest.mark.asyncio
    async def test_arepeat_infinite(self):
        """It should repeat the given value infinitely.

        It can't really be determined that it will give the value
        infinitely, but we can make sure it takes the right arguments.
        """
        aiterator = aitertools.arepeat(42)
        for i in range(20):
            assert await aitertools.anext(aiterator) == 42

    @pytest.mark.asyncio
    async def test_arepeat_finite(self):
        """It should repeat the given value the given number of times."""
        aiterator = aitertools.arepeat(42, 10)
        for i in range(10):
            assert await aitertools.anext(aiterator) == 42
        with pytest.raises(StopAsyncIteration):
            await aitertools.anext(aiterator)

    @pytest.mark.asyncio
    async def test_aaccumulate_default(self):
        """It should default to adding."""
        iterable = [list(i) for i in 'abcdefg']  # A list of lists
        aiterator = aitertools.to_aiter(iterable)

        values = []
        async for value in aitertools.aaccumulate(aiterator):
            values.append(value)

        assert values == [
            ['a'],
            ['a', 'b'],
            ['a', 'b', 'c'],
            ['a', 'b', 'c', 'd'],
            ['a', 'b', 'c', 'd', 'e'],
            ['a', 'b', 'c', 'd', 'e', 'f'],
            ['a', 'b', 'c', 'd', 'e', 'f', 'g'],
        ]

    @pytest.mark.asyncio
    async def test_aaccumulate_override(self):
        """It should default to adding."""
        afunc = aitertools.to_async(operator.mul)
        aiterator = aitertools.to_aiter(range(1, 5))

        values = []
        async for value in aitertools.aaccumulate(aiterator):
            values.append(value)

        assert values == [1, 3, 6, 10]


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

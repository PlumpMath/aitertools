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

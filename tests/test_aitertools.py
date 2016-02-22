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

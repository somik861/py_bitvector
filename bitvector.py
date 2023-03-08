from math import log2
from itertools import dropwhile
from typing import Any, Callable
from operator import and_, or_

DEFAULT_SIZE = 64


class BitVector:
    def __init__(self, val: int | list[int | bool] = 0, size: int = DEFAULT_SIZE) -> None:
        self.value = [False] * size

        if type(val) is int:
            assert val >= 0 and (val == 0 or log2(
                val) < size), f'Value {val} is too big for size {size}'
            idx = -1
            while val > 0:
                self.value[idx] = (val % 2 == 1)
                val //= 2
                idx -= 1
            return

        if type(val) is list and type(val[0]) in [int, bool]:
            assert len(
                val) <= size, f'List of size {len(val)} is too big for size {size}'
            for i in range(-1, -len(val) - 1, -1):
                self.value[i] = val[i]
            return

        assert False, f'Invalid input type, valid: int | list[int | bool]; got {type(val)}'

    def as_int(self) -> int:
        out = 0
        for i, val in enumerate(reversed(self.value)):
            out += int(val) * 2**i
        return out

    def as_hex(self) -> str:
        return hex(self.as_int())

    def as_bits(self) -> str:
        bits = []
        for val in dropwhile(lambda x: not x, self.value):
            bits.append(str(int(val)))
        if not bits:
            bits.append('0')

        out = []
        for i, val in enumerate(reversed(bits)):
            if i % 4 == 0 and i != 0:
                out.append('\'')
            out.append(val)

        out = list(reversed(out))

        return ''.join(['0b'] + out)

    def __str__(self) -> str:
        return f'[{len(self)}] {self.as_int()}~{self.as_bits()}'

    def __repr__(self) -> str:
        return f'BitVector({self.as_int()}, size={len(self.value)})'

    def __len__(self) -> int:
        return len(self.value)

    def __getitem__(self, idx: int) -> bool:
        assert idx < len(
            self), f'Index {idx} out of range; range: [0, {len(self)})'
        return self.value[-idx - 1]

    def __setitem__(self, idx: int, new_val: bool | int) -> None:
        assert idx < len(
            self), f'Index {idx} out of range; range: [0, {len(self)})'

        new_val = bool(new_val)
        self.value[-idx - 1] = new_val


def _bv_test(f: Callable[[BitVector, BitVector, int], BitVector]) -> Any:
    def wrapper(lhs: BitVector, rhs: BitVector, size: int | None = None, *args, **kwargs) -> BitVector:
        if size is not None:
            assert len(lhs) == len(rhs) and size <= len(
                lhs), f'Missmatching sizes: {len(lhs)=} {len(rhs)=} has to be bigger than {size=}'
        else:
            assert len(lhs) == len(
                rhs), f'Missmatching sizes: {len(lhs)=} {len(rhs)=}'
            size = len(lhs)

        return f(lhs, rhs, size, *args, **kwargs)

    return wrapper


class ops:
    @staticmethod
    @_bv_test
    def _noop(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        pass

    @staticmethod
    @_bv_test
    def elem_wise(lhs: BitVector, rhs: BitVector, size: int, f: Callable[[bool, bool], bool], ) -> BitVector:
        out = BitVector(size=len(lhs))
        for i in range(size):
            out[i] = f(lhs[i], rhs[i])
        return out

    @staticmethod
    @_bv_test
    def eq(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        for i in range(size):
            if lhs[i] != rhs[i]:
                return False
        return True

    @staticmethod
    @_bv_test
    def neq(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        return not ops.eq(lhs, rhs, size)

    @staticmethod
    @_bv_test
    def bit_and(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        return ops.elem_wise(lhs, rhs, size, and_)

    @staticmethod
    @_bv_test
    def bit_or(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        return ops.elem_wise(lhs, rhs, size, or_)

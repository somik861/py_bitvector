from __future__ import annotations

from itertools import dropwhile
from typing import Any, Callable
from operator import and_, or_, xor, neg
from functools import total_ordering

DEFAULT_SIZE = 64


@total_ordering
class BitVector:
    def __init__(self, val: int | list[int | bool] = 0, size: int = DEFAULT_SIZE) -> None:
        assert size > 0, 'BitVector of size 0 does not make sense :D'

        self.value = [False] * size

        if type(val) is int:
            assert self.min_signed_value() <= val <= self.max_value(),\
                f'Value {val} is too big (or too small) for size {size}; range: [{self.min_signed_value()}, {self.max_value()}]'

            if val < 0:
                val += 2 ** len(self)

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

    def max_value(self) -> int:
        return 2**len(self) - 1

    def min_value(self) -> int:
        return 0

    def max_signed_value(self) -> int:
        return 2 ** (len(self) - 1) - 1

    def min_signed_value(self) -> int:
        return 2 ** (len(self) - 1)

    def as_bitvector(self, size: int) -> BitVector:
        out = BitVector(size=size)
        for i in range(min(size, len(self))):
            out[i] = self[i]

        return out

    def as_signed_int(self) -> int:
        if self.value[0] == 0:
            return self.as_int()

        return self.as_int() - 2 ** len(self)

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

    def __eq__(self, __o: object) -> bool:
        if type(__o) is not BitVector:
            return False
        return self.value == __o.value

    def __lt__(self, __o: object) -> bool:
        if type(__o) is not BitVector:
            return False

        return len(self) == len(__o) and self.as_int() < __o.as_int()

    def copy(self) -> BitVector:
        cpy = BitVector(self.value)
        return cpy

    def inject_at_start(self, other: BitVector) -> None:
        assert len(self) >= len(other),\
            f'Cannot inject bv of size {len(other)} into bv {len(self)}'
        for i in range(len(other)):
            self[i] = other[i]


def _bin_bv_test(f: Callable[[BitVector, BitVector, int], BitVector]) -> Any:
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


def _un_bv_test(f: Callable[[BitVector, int], BitVector]) -> Any:
    def wrapper(arg: BitVector, size: int | None = None, *args, **kwargs) -> BitVector:
        if size is not None:
            assert size <= len(arg),\
                f'Missmatching sizes: {len(arg)=} has to be bigger than {size=}'

        else:
            size = len(arg)

        return f(arg, size, *args, **kwargs)

    return wrapper


class ops:
    @staticmethod
    @_bin_bv_test
    def _noop(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        pass

    # ============ Extend operations
    @staticmethod
    def zext(arg: BitVector, new_size: int) -> BitVector:
        assert new_size > len(arg), \
            f'Cannot extend bv of size {len(arg)} to {new_size}'

        return BitVector(arg.value, new_size)

    @staticmethod
    def sext(arg: BitVector, new_size: int) -> BitVector:
        assert new_size > len(arg), \
            f'Cannot extend bv of size {len(arg)} to {new_size}'

        out = BitVector(arg.value, new_size)
        out.value[0] = arg.value[0]
        out[len(arg) - 1] = False
        return out

    @staticmethod
    def trunc(arg: BitVector, new_size: int) -> BitVector:
        assert new_size < len(arg), \
            f'Cannot truncate bv of size {len(arg)} to {new_size}'
        return BitVector.as_bitvector(new_size)

    # ============ Arithmetic operations

    @staticmethod
    @_bin_bv_test
    def add(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        op_res = BitVector(lhs.as_bitvector(size).as_int() +
                           rhs.as_bitvector(size).as_int(), size=max(len(lhs), len(rhs) + 1)).as_bitvector(size)
        res = lhs.copy()
        res.inject_at_start(op_res)
        return res

    @staticmethod
    @_bin_bv_test
    def sub(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        op_res = BitVector(lhs.as_bitvector(size).as_int() -
                           rhs.as_bitvector(size).as_int(), size=max(len(lhs), len(rhs) + 1)).as_bitvector(size)
        res = lhs.copy()
        res.inject_at_start(op_res)
        return res

    @staticmethod
    @_bin_bv_test
    def mul(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        op_res = BitVector(lhs.as_bitvector(size).as_int() *
                           rhs.as_bitvector(size).as_int(), size=len(lhs) + len(rhs) + 1).as_bitvector(size)
        res = lhs.copy()
        res.inject_at_start(op_res)
        return res

    @staticmethod
    @_bin_bv_test
    def sdiv(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        op_res = BitVector(lhs.as_bitvector(size).as_signed_int() //
                           rhs.as_bitvector(size).as_signed_int(), size=len(lhs)).as_bitvector(size)
        res = lhs.copy()
        res.inject_at_start(op_res)
        return res

    @staticmethod
    @_bin_bv_test
    def udiv(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        op_res = BitVector(lhs.as_bitvector(size).as_int() //
                           rhs.as_bitvector(size).as_int(), size=len(lhs)).as_bitvector(size)
        res = lhs.copy()
        res.inject_at_start(op_res)
        return res

    @staticmethod
    @_bin_bv_test
    def srem(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        op_res = BitVector(lhs.as_bitvector(size).as_signed_int() %
                           rhs.as_bitvector(size).as_signed_int(), size=len(lhs)).as_bitvector(size)
        res = lhs.copy()
        res.inject_at_start(op_res)
        return res

    @staticmethod
    @_bin_bv_test
    def urem(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        op_res = BitVector(lhs.as_bitvector(size).as_int() %
                           rhs.as_bitvector(size).as_int(), size=len(lhs)).as_bitvector(size)
        res = lhs.copy()
        res.inject_at_start(op_res)
        return res

    # ============ Bit operations

    @staticmethod
    @_bin_bv_test
    def elem_wise(lhs: BitVector, rhs: BitVector, size: int, f: Callable[[bool, bool], bool], ) -> BitVector:
        out = BitVector(size=len(lhs))
        for i in range(size):
            out[i] = f(lhs[i], rhs[i])
        return out

    @staticmethod
    @_un_bv_test
    def unary_op(arg: BitVector, size: int, f: Callable[[bool], bool]) -> BitVector:
        assert size <= len(
            arg), f'Size {size} is too big for bv of size {len(arg)}'

        out = BitVector(len(arg))
        for i in range(size):
            out[i] = f(arg[i])

        return out

    @staticmethod
    @_bin_bv_test
    def bit_and(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        return ops.elem_wise(lhs, rhs, size, and_)

    @staticmethod
    @_bin_bv_test
    def bit_or(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        return ops.elem_wise(lhs, rhs, size, or_)

    @staticmethod
    @_bin_bv_test
    def bit_xor(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        return ops.elem_wise(lhs, rhs, size, xor)

    @staticmethod
    @_un_bv_test
    def bit_neg(arg: BitVector, size: int) -> BitVector:
        return ops.unary_op(arg, size, neg)

    @staticmethod
    @_un_bv_test
    def shl(arg: BitVector, size: int) -> BitVector:
        arg = arg.copy()
        for i in reversed(range(1, size)):
            arg[i] = arg[i - 1]

        arg[0] = False
        return arg

    @staticmethod
    @_un_bv_test
    def lshr(arg: BitVector, size: int) -> BitVector:
        arg = arg.copy()
        for i in range(size - 1):
            arg[i] = arg[i + 1]

        arg[size - 1] = False
        return arg

    @staticmethod
    @_un_bv_test
    def ashr(arg: BitVector, size: int) -> BitVector:
        arg = arg.copy()
        for i in range(size - 1):
            arg[i] = arg[i + 1]

        return arg

    # ============ Relation operations

    @staticmethod
    @_bin_bv_test
    def eq(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        return lhs.as_bitvector(size) == rhs.as_bitvector(size)

    @staticmethod
    @_bin_bv_test
    def neq(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        return not ops.eq(lhs, rhs, size)

    @staticmethod
    @_bin_bv_test
    def ult(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        return lhs.as_bitvector(size) < rhs.as_bitvector(size)

    @staticmethod
    @_bin_bv_test
    def ule(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        return ops.ult(lhs, rhs, size) or ops.eq(lhs, rhs, size)

    @staticmethod
    @_bin_bv_test
    def ugt(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        return not ops.ule(lhs, rhs, size)

    @staticmethod
    @_bin_bv_test
    def uge(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        return not ops.ult(lhs, rhs, size)

    @staticmethod
    @_bin_bv_test
    def slt(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        return lhs.as_bitvector(size).as_signed_int() < rhs.as_bitvector(size).as_signed_int()

    @staticmethod
    @_bin_bv_test
    def sle(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        return ops.slt(lhs, rhs, size) or ops.eq(lhs, rhs, size)

    @staticmethod
    @_bin_bv_test
    def sgt(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        return not ops.sle(lhs, rhs, size)

    @staticmethod
    @_bin_bv_test
    def sge(lhs: BitVector, rhs: BitVector, size: int) -> BitVector:
        return not ops.slt(lhs, rhs, size)

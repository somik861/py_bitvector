from math import log2
from itertools import dropwhile

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

        out = []
        for i, val in enumerate(reversed(bits)):
            if i % 4 == 0 and i != 0:
                out.append('\'')
            out.append(val)

        out = list(reversed(out))

        return ''.join(['0b'] + out)

    def __str__(self) -> str:
        return f'{self.as_int()} ~ {self.as_bits()}'

    def __repr__(self) -> str:
        return f'BitVector({self.as_int()}, size={len(self.value)})'

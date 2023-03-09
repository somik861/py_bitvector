from bitvector import BitVector, ops
from typing import Any


bv8 = BitVector(8, size=5)
bv_15 = BitVector(-15, size=5)


def nas_op(lhs: BitVector, rhs: BitVector, op: Any) -> Any:
    assert len(lhs) == len(rhs), f'{len(lhs)} == {len(rhs)}'
    nas_lhs = ops.sext(lhs, new_size=8)
    nas_rhs = ops.sext(rhs, new_size=8)

    return ops.trunc(op(nas_lhs, nas_rhs), len(lhs))


print(f'{bv8 = !s}')
print(f'{bv_15 = !s}')

print(f'{ops.sext(bv8, new_size=8) = !s}')
print(f'{ops.sext(bv_15, new_size=8) = !s}')

print(f'{ops.bit_or(bv8, bv_15) = !s}')
print(f'{nas_op(bv8, bv_15, ops.bit_or) = !s}')

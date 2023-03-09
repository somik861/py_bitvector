from bitvector import BitVector, ops, BINARY_OPS
from typing import Any


def nas_op(lhs: BitVector, rhs: BitVector, op: Any) -> Any:
    assert len(lhs) == len(rhs), f'{len(lhs)} == {len(rhs)}'
    nas_lhs = ops.sext(lhs, new_size=8)
    nas_rhs = ops.sext(rhs, new_size=8)

    res = op(nas_lhs, nas_rhs)
    if type(res) is BitVector:
        return ops.trunc(res, len(lhs))

    return res


for operation in BINARY_OPS:
    try:
        for bs in range(2, 8):
            for lhs in range(-2**(bs - 1), 2**(bs)):
                for rhs in range(-2**(bs - 1), 2**(bs)):

                    bv_lhs = BitVector(lhs, size=bs)
                    bv_rhs = BitVector(rhs, size=bs)

                    try:
                        nat_res = operation(bv_lhs, bv_rhs)
                        nas_res = nas_op(bv_lhs, bv_rhs, operation)
                    except ZeroDivisionError:
                        continue

                    if type(nat_res) is BitVector:
                        if nat_res.as_signed_int() != nas_res.as_signed_int():
                            raise RuntimeError(
                                f'{bv_lhs = !s} {bv_rhs = !s} {operation = } {nat_res = !s} {nas_res = !s} ')
                        continue

                    if type(nat_res) is bool:
                        if nat_res != nas_res:
                            raise RuntimeError(
                                f'{nat_res = } {nas_res = } {operation = }')
                        continue

                    assert False
    except RuntimeError as e:
        print(e)

from bitvector import BitVector, ops, BINARY_OPS
from typing import Any


def nas_bin_op(lhs: BitVector, rhs: BitVector, op: Any) -> Any:
    assert len(lhs) == len(rhs), f'{len(lhs)} == {len(rhs)}'
    nas_lhs = ops.sext(lhs, new_size=8)
    nas_rhs = ops.sext(rhs, new_size=8)

    res = op(nas_lhs, nas_rhs)
    if type(res) is BitVector:
        rv = ops.trunc(res, len(lhs))
        rvext = ops.sext(rv, new_size=8)
        if rvext != res:
            raise RuntimeError(
                f'{rvext = !s} {res = !s} {lhs = !s} {rhs = !s}  {operation = !s}')
        return rv

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
                        nas_res = nas_bin_op(bv_lhs, bv_rhs, operation)
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


def nas_un_op(arg: BitVector, op: Any) -> Any:
    nas_arg = ops.sext(arg, new_size=8)

    res = op(nas_arg)
    if type(res) is BitVector:
        rv = ops.trunc(res, len(arg))
        rvext = ops.sext(rv, new_size=8)
        if rvext != res:
            raise RuntimeError(
                f'{rvext = !s} {res = !s} {arg = !s}  {op = !s}')
        return rv

    return res


def nas_shift_op(arg: BitVector, n: int, op: Any) -> Any:
    nas_arg = ops.sext(arg, new_size=8)

    res = op(nas_arg, n)
    if type(res) is BitVector:
        rv = ops.trunc(res, len(arg))
        rvext = ops.sext(rv, new_size=8)
        if rvext != res:
            raise RuntimeError(
                f'{rvext = !s} {res = !s} {arg = !s}  {op = !s}')
        return rv

    return res


try:
    for bs in range(2, 8):
        for arg in range(-2**(bs - 1), 2**(bs)):

            bv_arg = BitVector(arg, size=bs)

            nat_res = ops.bit_neg(bv_arg)
            nas_res = nas_un_op(bv_arg, ops.bit_neg)

            if type(nat_res) is BitVector:
                if nat_res.as_signed_int() != nas_res.as_signed_int():
                    raise RuntimeError(
                        f'{bv_arg = !s} {ops.bit_neg} {nat_res = !s} {nas_res = !s} ')
                continue

            assert False
except RuntimeError as e:
    print(e)

for shift in [ops.lshr, ops.ashr, ops.shl]:
    try:
        for bs in range(2, 8):
            for arg in range(-2**(bs - 1), 2**(bs)):
                for n in range(1, bs + 1):
                    bv_arg = BitVector(arg, size=bs)

                    nat_res = shift(bv_arg, n)
                    nas_res = nas_shift_op(bv_arg, n, shift)

                    if type(nat_res) is BitVector:
                        if nat_res.as_signed_int() != nas_res.as_signed_int():
                            raise RuntimeError(
                                f'{bv_arg = !s} {shift = } {n = } {nat_res = !s} {nas_res = !s} ')
                        continue

                    assert False
    except RuntimeError as e:
        print(e)

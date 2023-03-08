from bitvector import BitVector, ops, ALL_OPS


for operation in ALL_OPS:
    try:
        for bs in range(2, 8):
            for lhs in range(-2**(bs - 1), 2**(bs)):
                for rhs in range(-2**(bs - 1), 2**(bs)):

                    nat_lhs = BitVector(lhs, size=bs)
                    nat_rhs = BitVector(rhs, size=bs)
                    nas_lhs = ops.sext(BitVector(lhs, size=bs), new_size=8)
                    nas_rhs = ops.sext(BitVector(rhs, size=bs), new_size=8)

                    try:
                        nat_res = operation(nat_lhs, nat_rhs)
                        nas_res = operation(nas_lhs, nas_rhs)
                    except ZeroDivisionError:
                        continue
                    
                    if False:
                        try:
                            for i in range(8 - bs):
                                if type(nas_res) is BitVector and nas_res.value[i] != nas_res.value[0]:
                                    raise RuntimeError(
                                        f'{nas_res = !s} { operation = }')
                        except IndexError:
                            print(bs)

                    if type(nat_res) is BitVector:
                        if nat_res.as_signed_int() != nas_res.as_signed_int():
                            raise RuntimeError(
                                f'{nat_res.as_signed_int() = } {nas_res.as_signed_int() = } {operation = }')
                        continue

                    if type(nat_res) is bool:
                        if nat_res != nas_res:
                            raise RuntimeError(
                                f'{nat_res = } {nas_res = } {operation = }')
                        continue

                    assert False
    except RuntimeError as e:
        print(e)

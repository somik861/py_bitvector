from bitvector import BitVector, ops


bv32 = BitVector(32)
bv15 = BitVector(15)
bv3 = BitVector(3)

print(f'{bv32 = !s}')
print(f'{bv15 = !s}')
print(f'{bv3 = !s}')

print()

print(f'{bv32.as_bits() = !s}')
print(f'{bv32.as_int() = !s}')
print(f'{bv32.as_hex() = !s}')
print(f'{ops.eq(bv32, bv32) = }')

print()

print(f'{ops.eq(bv32, bv15) = }')
print(f'{ops.eq(bv15, bv3) = }')
print(f'{ops.eq(bv15, bv3, size=2) = }')

print()

print(f'{ops.bit_and(bv15, bv3) = !s}')
print(f'{ops.bit_or(bv32, bv15) = !s}')
print(f'{ops.bit_or(bv32, bv15, size=5) = !s}')

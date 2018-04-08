import os
import struct


# covert a number to an ascii byte string
def number_to_bytes(x): return x if isinstance(x, bytes) else bytes(str(int(x)), encoding='ascii')


# convert a string to an ascii byte string
def str_to_bytes(x): return x if isinstance(x, bytes) else str(x).encode('ascii')


# pack a short int
def pack_short_int(x): return x if isinstance(x, bytes) else x.to_bytes(2, byteorder='big')


# unpack a short int
def unpack_short_int(x): return int.from_bytes(x,  byteorder='big')
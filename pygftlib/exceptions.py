"""
Exceptions relating to protocol
"""


class PYGFTError(Exception):
    pass


class ProtocolException(PYGFTError):
    pass


class BadRequestException(PYGFTError):
    """
    Used when we receive an different type of packet while we were expecting some other type of packet
    """
    pass


class MalformedPacketException(PYGFTError):
    """
    Used when the packet received has some invalid OP_CODE, or cannot be parsed
    """
    pass

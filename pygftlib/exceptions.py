"""
Exceptions relating to protocols
"""


class HFTPError(Exception):
    pass


class ProtocolException(HFTPError):
    pass


class BadRequestException(HFTPError):
    """
    Used when we receive an different type of packet while we were expecting some other type of packet
    """
    pass


class MalformedPacketException(HFTPError):
    """
    Used when the packet received has some invalid OP_CODE, or cannot be parsed
    """
    pass

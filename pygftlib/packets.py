import struct
import sys

from pygftlib.helpers import *
import logging
logger = logging.getLogger(__name__)


class BasePacket(object):
    """
    This class is parent to all the hftp packet classes.
    """
    def __init__(self):
        # TODO: May be bytes_buffer is not needed anymore?
        self.bytes_buffer = None  # to store the encoded/decoded contents of a packet.
        self.op_code = 0  # op_code of the packet
        self.decode = self.parse_packet
        self.encode = self.build_packet

    def build_packet(self, **kwargs):
        """This method is used to receive data from a FileObject/InitRQ and get it encoded; So that later we may send it
        across the network. Note that this bytes sent here would not contain the op_code bytes as they are taken care
        of in the ProtocolFactory"""
        raise NotImplementedError

    def parse_packet(self, data):
        """Used the parse the contents of the packet. Again decoded content would be devoid of the op_code. Which is
        how it should be"""
        raise NotImplementedError


class INITRQPacket(BasePacket):
    """
    Implementing the INITRQ packet. Note that this would be sent over the network by the client and parsed by the server
    ::
               2 bytes    string    1 byte
              ----------------------------
    INITRQ   | 01    |  Filename  |   0  |
              ----------------------------
    """

    def __init__(self):
        super(INITRQPacket, self).__init__()
        self.op_code = 1
        self.file_name = None  # packet to contain the file_name

    def __str__(self):
        return 'INITRQ packet: filename = %s' % self.filename

    def build_packet(self, **kwargs):
        # TODO: consider replacing join with bytearray
        self.file_name = kwargs['file_name']
        return pack_short_int(self.op_code) + str_to_bytes(self.file_name) + b'\x00'

    def parse_packet(self, data):
        try:
            self.file_name = data[2:-1].decode('ascii')
        except ValueError:
            logger.exception('Could not parse request: {}'.format(data))
        return self


class DATAPacket(BasePacket):
    """
                2 bytes    2 bytes       n bytes
                ---------------------------------
        DATA  | 02    |   Block #  |    Data    |
                ---------------------------------
    """

    def __init__(self):
        super(DATAPacket, self).__init__()
        self.op_code = 2
        self.block_number = 0
        self.data = None

    def __str__(self):
        s = 'DATA packet: block = %d' % self.block_number
        if self.data:
            s += ' | data: %d bytes' % len(self.data)
        return s

    def build_packet(self, **kwargs):
        self.data = kwargs['data']
        self.block_number = kwargs['block_no']
        # TODO: consider replacing join with bytearray
        return pack_short_int(self.op_code) + pack_short_int(self.block_number) + str_to_bytes(self.data)

    def parse_packet(self, data):
        try:
            #  self.block_number, self.data = unpack_short_int(data[2:4]), data[4:].decode('ascii')
            #  Fixme: ^^ write raw bytes to a file
            self.block_number, self.data = unpack_short_int (data[2:4]), data[4:]
        except ValueError:
            logger.exception('Could not parse request: {}'.format(data))
        return self


class ACKPacket(BasePacket):
    """
                2 bytes    2 bytes
                -------------------
        ACK   | 03    |   Block #  |
                --------------------
    """
    def __init__(self):
        super(ACKPacket, self).__init__()
        self.op_code = 3
        self.block_number = 0

    def __str__(self):
        return 'ACK packet: block = %d' % self.block_number

    def build_packet(self, **kwargs):
        # TODO: consider replacing join with bytearray
        self.block_number = kwargs['block_no']
        return pack_short_int(self.op_code) + pack_short_int(self.block_number)

    def parse_packet(self, data):
        try:
            self.block_number = unpack_short_int(data[2:])
        except ValueError:
            logger.exception('Could not parse request: {}'.format(data))
        return self


# FIXME: Do we even need this?
class ERRPacket(BasePacket):
    """
                2 bytes  2 bytes        string    1 byte
                ----------------------------------------
        ERROR | 04    |  ErrorCode |   ErrMsg   |   0  |
                ----------------------------------------
        Error Codes
        Value     Meaning
        0         Not defined, see error message (if any).
        1         File not found.
        2         Access violation.
        3         Disk full or allocation exceeded.
        4         Illegal operation.
        5         Unknown transfer ID.
        6         File already exists.
    """
    def __init__(self):
        super(ERRPacket, self).__init__()
        self.op_code = 4
        self.err_code = 0
        self.errors = {
            0: b"Not defined, see error message (if any)",
            1: b"File Not Found",
            2: b"Access violation",
            3: b"Disk full or allocation exceeded.",
            4: b"Illegal operation.",
            5: b"Unknown transfer ID.",
            6: b"File already exists.",
        }
        self.err_msg = None

    def __str__(self):
        s = 'ERR packet: error_code = %d'%self.err_code
        s += ' | msg = %s' % self.errors[self.err_code]
        return s

    def build_packet(self, **kwargs):
        # TODO: consider replacing join with bytearray
        self.err_code = kwargs['err_code']
        return (pack_short_int(self.op_code) + pack_short_int(self.err_code)
                + str_to_bytes(self.errors[self.err_code]) + b'\x00')

    def parse_packet(self, data):
        try:
            self.err_code = unpack_short_int(data[2:4])
            self.err_msg = self.errors[self.err_code]
        except KeyError:
            logger.exception('Unidentified error message')
            self.err_msg = self.errors[0]
            raise
        except ValueError:
            logger.exception('Could not parse request: {}'.format(data))
        return self


# for testing --
if __name__ == '__main__':
    ack_pkt = ACKPacket()
    data_pkt = DATAPacket()
    err_pkt = ERRPacket()
    initrq_pkt = INITRQPacket()

    # TODO: change these to assert
    # printing the various encoded packets
    print(ack_pkt.build_packet(block_no=23))
    print(data_pkt.build_packet(block_no=24, data='test'))
    print(err_pkt.build_packet(err_code=3))
    print(initrq_pkt.build_packet(file_name='test.dummy'))

    print(ack_pkt.parse_packet(b'\x00\x03\x00\x17'))
    print(data_pkt.parse_packet(b'\x00\x02\x00\x18test'))
    print(err_pkt.parse_packet(b'\x00\x04\x00\x03Disk full or allocation exceeded.\x00'))
    print(initrq_pkt.parse_packet(b'\x00\x01test.dummy\x00'))
    print(initrq_pkt.parse_packet(b'\x00\x01test.dummy\x00').file_name)

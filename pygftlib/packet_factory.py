"""
Define packet_metrics -- such as since when have not sent/received a packet.
"""
from pygftlib import *   # TODO: only import what is required
from pygftlib.packets import INITRQPacket, ERRPacket, DATAPacket, ACKPacket
from pygftlib.exceptions import MalformedPacketException

# import logging as logger
import logging
import sys
logger = logging.getLogger(__name__)
# For debugging --
# logger.basicConfig(stream=sys.stdout, level=logger.INFO)
# TODO: More logging in b/w classes

OP_CODES = {
    'INITRQ': b'\x00\x01',
    'DATA': b'\x00\x02',
    'ACK': b'\x00\x03',
    'ERR': b'\x00\x04',
    b'\x00\x01': 'INITRQ',
    b'\x00\x02': 'DATA',
    b'\x00\x03': 'ACK',
    b'\x00\x04': 'ERR'
}

PACKET_TYPES = {
    'INITRQ': INITRQPacket,
    'DATA': DATAPacket,
    'ACK': ACKPacket,
    'ERR': ERRPacket
}


class PacketFactory(object):
    def __init__(self):
        pass

    @classmethod
    def from_bytes(cls, data):
        """
        Take in raw byte. Identify packet_type using op_code.
        :return decoded content
        - file_name in case of INITRQ
        - block_no, data - (content) in case of DATA
        - block_no in case of ACK
        - error_code, error_msg in case of ERR
        """
        op_code = data[:2]
        logger.debug('Received data for decoding. Raw contents: {}. Op_code : {}'.format(data, op_code))
        if op_code not in OP_CODES:
            logger.debug('Invalid OP_CODE')
            raise MalformedPacketException('Unidentified Packet Type - {}'.format(op_code))
        else:
            packet_instance = PACKET_TYPES[OP_CODES[op_code]]()
            if op_code == OP_CODES['INITRQ']:
                logger.debug('Packet type is INITRQ')
                file_name = packet_instance.parse_packet(data=data).file_name
                return file_name
            elif op_code == OP_CODES['DATA']:
                logger.debug('Packet type is DATA')
                block_no, content = int(packet_instance.parse_packet(data=data).block_number), packet_instance.\
                    parse_packet(data=data).data
                return block_no, content
            elif op_code == OP_CODES['ACK']:
                logger.debug('Packet type is ACK')
                block_no = int(packet_instance.parse_packet(data=data).block_number)
                return block_no
            elif op_code == OP_CODES['ERR']:
                logger.debug ('Packet type is ERR')
                err_code, err_msg = packet_instance.parse_packet(data=data).err_code, packet_instance.parse_packet(
                    data=data).err_msg
                return err_code, err_msg

    @classmethod
    def to_bytes(cls, type=None, **kwargs):
        """
        Covert some "data" into a specific packet_type.
        :param type:
        :return: bytes - packet
        """
        if type is None:
            raise ValueError('Protocol Type cannot be none')
        else:
            if type.upper() in ('ACK', 'INITRQ', 'DATA'):
                return PACKET_TYPES[type.upper()]().build_packet(**kwargs)
            else:
                # must be error. Error hasn't been fully implemented yet :-(
                raise NotImplementedError('Error packet type is being encoded. '
                                          'Err packet is currently not supported :-(')

    @classmethod
    def check_type(cls, packet_type=None, data=None):
        """
        Checks whether the given packet_type is the type it says it is!
        :return: boolean True or False
        """
        if data is None:
            raise ValueError('Not data supplied. Data cannot be None')
        elif packet_type is None:
            raise ValueError('Not packet_type supplied.')
        else:
            return packet_type.upper() == OP_CODES[data[:2]]

    @classmethod
    def is_valid(cls, packet_type=None, data=None):
        """
        Checks whether a given packet is valid_packet of the said pckt_type.
        :param packet_type:
        :param data:
        :return:
        """
        op_code = data[:2]
        if op_code not in OP_CODES:
            raise MalformedPacketException('Unidentified Packet Type - {}'.format(op_code))
        elif packet_type is None:
            raise ValueError('Packet Type cannot be None')
        else:
            if packet_type.upper() == 'INITRQ':
                return (len(data) >= MIN_PACKET_SIZE) and (len(data) <= MAX_PACKET_SIZE)
            elif packet_type.upper() == 'DATA':
                return (len(data) >= 2) and (len(data) <= MAX_PACKET_SIZE)
            elif packet_type.upper() == 'ACK':
                return len(data) == 4
            else:
                # must be error. Error hasn't been fully implemented yet :-(
                raise NotImplementedError('Error packet type is being encoded. '
                                          'Err packet is currently not supported :-(')


# for debugging:
if __name__ == '__main__':
    test = PacketFactory
    assert test.check_type('ack', b'\x00\x03\x00\x17'), 'ACK not validating correctly'
    print(test.is_valid('ack', b'\x00\x03\x00\x17'))
    print(test.from_bytes(b'\x00\x03\x00\x17'))
    print(test.to_bytes('ack', block_no=23))

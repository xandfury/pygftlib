"""
- Define various functionality relating to sending and receiving different kinds of packets.
- Keep context w.r.t states of the client/server. Maintain the last_pkt in case not ack is received or etc.
- Read/Write from FileObjects - better interactions with those classes
- Sender UDP client; Receiver UDP DatagramServer
"""
# FIXME: Package Level Imports
import gevent
from gevent.server import DatagramServer
from gevent import socket, queue
import gevent.monkey; gevent.monkey.patch_all()
import signal
import time
import sys

from pygftlib import *
from pygftlib.file_io import FileReader, FileWriter
from pygftlib.packet_factory import PacketFactory
from pygftlib.exceptions import *

import logging
logger = logging.getLogger(__name__)
# For debugging --
# import logging as logger
# logger.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class BaseProtocol (object):
    """Implement common functionality for Sender and Receiver"""

    def __init__(self):
        pass

    def send_err(self):
        raise NotImplementedError

    def handle_err(self):
        raise NotImplementedError


class Sender(object):
    """
    - Read fixed blk_size from a file_obj
    - Initiates connection to a Receiver by send it a INITRQ packet
    - Waits for the server to reply with a ACK packet having block_no = 0.
    - Convert the file_obj data to DATA packet. Writes to the socket. The block_no should be 1
    - Waits for the server to send the ACK. If the server does not send the packet within *some_time*, resend the packet.
        - Wait till timeout -- after which disconnect the client
    - If ACK is received, check the block_no on the packet. Verify with the block_no_counter available.
        - If there is no match, drop the packet and wait.
        - If there is a match, send DATA packet 2
    - repeat till transfer_complete. This happens when data_received from file_obj < or != blk_size
    """

    def __init__(self, file_name):
        self.transfer_complete = False
        self.error_occurred = False
        self.file_name = file_name  # the file to read and send across
        self.last_packet = None  # only maintain the last packet in  buffer -- for resending
        self.new_packet = None
        if not self.file_name:
            logger.fatal('No filename supplied for Sender. Filename cannot be empty!')
            sys.exit(3)
        self.file_obj = FileReader(self.file_name)
        self.last_active = None

        self.packet_factory = PacketFactory
        self.init_rq_packet = self.packet_factory.to_bytes(type='initrq', file_name=self.file_name)
        self.last_packet = self.init_rq_packet
        self.block_no = 0
        self.terminating_block_no = None

        # Initialize to current time.
        self.max_no_response_time = MAX_NO_RESPONSE_TIME  # disconnect the client if an ACK not received
        # within this time
        self.no_response_time = NO_RESPONSE_TIME  # resend the "last_data_packet" if no ACK is received within this time
        self.sock = None  # setup client sock --- later
        self.start = self.upload   # create alias to upload
        self._send_queue = gevent.queue.Queue()  # Add processed packets to the send queue

    def upload(self, host, port):
        self.sock = gevent.socket.socket(type=socket.SOCK_DGRAM)
        self.sock.settimeout(1)   # set socket to non-blocking mode.. But setting to 1 yeilds better results
        conn = (host, port)
        try:
            logger.info('Attempting to connect to server at {}'.format(conn))
            self.sock.connect(conn)
            # send the init_packet
            self.sock.send(self.init_rq_packet)
            self.last_active = time.time ()  # time since last we received a DATA packet from the server(Receiver)
            logger.info('Init packet sent successfully')
            while not (self.transfer_complete or self.error_occurred):
                gevent.joinall([gevent.spawn(self.handle_ack), gevent.spawn(self.send_packet)])
                # Block till all jobs are not finished
            if self.transfer_complete:
                logger.info('File Transfer Complete!!')
            else:
                logger.info('File Could not be Transferred !')
        except socket.error:
            logger.exception('Socket Error! Cannot establish connection! Sorry')
        except PYGFTError:
            logger.exception('Error occurred file parsing/encoding packet contents')
        except KeyboardInterrupt:
            logger.exception('Shutting down client')
        finally:
            self.stop()

    def stop(self):
        gevent.killall([gevent.spawn(self.handle_ack), gevent.spawn(self.send_packet)])
        self.sock.close()

    def _check_time(self):
        """
        Checks whether an ack has been received in the last "max_no_response_time". If it had been done so, return True
        else send False to disconnect the client
        :return: None
        """
        if int(time.time() - self.last_active) > self.max_no_response_time:
            logger.info('Receiver/server is not responding. Closing connection')
            return False
        elif (int(time.time() - self.last_active) < self.max_no_response_time) \
                and (int(time.time() - self.last_active) > self.no_response_time):
            # if an ACK is not received within the last no_response_time but may be still connected!
            # this is supposed to handle the UDP **packet lost** scenario.
            # resend the last packet and hope it reaches the server
            self._add_to_send_queue(packet=self.last_packet)
            return True
        else:
            # everything is jolly good! Nothing to do here. Move Along -- :-)
            return True

    def handle_ack(self):
        """
        Handles ACK packets. A response would triggered only when a valid ACK is received.
        """
        if self._check_time() and (not self.transfer_complete):
            try:
                logger.info ('Waiting to receive an ACK from Server')
                data, address = self.sock.recvfrom(MIN_PACKET_SIZE)
                # check if the data has valid op_code and is of correct length
                if not self.packet_factory.is_valid(packet_type='ack', data=data):
                    logger.info('Invalid/Malformed ACK Received from Receiver {}'.format(address))
                else:
                    # correct length and right op_code. Great! now parse the packet to get the block_no
                    block_no = self.packet_factory.from_bytes(data)
                    # update the last_active time to indicate that an ack has been received in **recent times**
                    self.last_active = time.time()
                    if block_no == self.block_no:
                        logger.debug('ACK Matches! Received ACK with correct block_no')
                        if self.block_no == 0:
                            logger.info('ACK Received. Initiating Transfer')
                        else:
                            logger.info('ACK Received for packet no {}'.format(self.block_no))
                        # Finally initiate transfer
                        self.block_no += 1
                        self._add_to_send_queue(address)
                    else:
                        # Better luck next time!!
                        logger.info('Received ACK packet. But of the wrong sequence/block_no. Dropping packet')
                        logger.debug('Contents of wrong ACK packet: {}. Block No: {}'.format(data, block_no))
                        # Nothing to do here, send_packet worker would send the DATA again to see
                        # if we fetch any results
            except socket.timeout:
                pass       # Do not print/log timeout stacktrace
        else:
            # Time this. If Ack not received in 10s (say) resend "last_packet"
            # If Ack not received in 30s (say)-- disconnect
            self.error_occurred = True

    def send_packet(self):
        """
        The actual worker that would send a packet to the remote server
        :return: None
        """
        # Check to see if there is any packet in the queue that is to be sent
        # If is is, send that packet. Otherwise if the queue is empty, send the last packet.
        if self._send_queue.qsize() > 0:
            packet = self._send_queue.get()
        else:
            packet = self.last_packet
        if len(packet) < MAX_PACKET_SIZE and (self.packet_factory.check_type('data', data=packet)):
            self.transfer_complete = True
        self.sock.send(packet)

    # FIXME: Refactor this function!!
    def _add_to_send_queue(self, address=None, packet=None):
        """Add a packet to be sent to the receiver"""
        if address is None:
            address = self.sock.getpeername()
        if packet is None:
            self.new_packet = self.packet_factory.to_bytes(type='data', block_no=self.block_no,
                                                           data=self.file_obj.read_chunk(DATA_SIZE))
            self.last_packet = self.new_packet
            logger.info('Sending packet to remote host: {}'.format(address))
            if self.packet_factory.is_valid(packet_type='data', data=self.new_packet) and \
                    self.packet_factory.check_type(packet_type='data', data=self.new_packet):
                if len(self.last_packet) != MAX_PACKET_SIZE:
                    self.terminating_block_no = self.block_no
                self._send_queue.put(self.new_packet)
        else:
            logger.info('Sending last packet again since no ACK was received')
            logger.debug('Resent packet contents: {}'.format(packet))
            self._send_queue.put(packet)


class Receiver(object):
    """
    - Start the UDP server on a host and port. Check for permissions to write on the CWD
    - Accept an incoming connection. Check if the packet is INITRQ type else discard the packet. <Done>
    - Send the ACK with block_no 0. Wait to receive DATA packet  <Done>
    - Verify DATA has block_no == ACK block_no + 1  <Done>
        - If yes, write to file. Else discard packet with appropriate error code  <No error codes at the moment>
        - Send ACK with block_no += 1    <Done>
    - repeat till transfer_complete. size(DATA) < or != blk_size. Close File pointers   <Done>
    """

    def __init__(self, timeout=None):
        self.client_state = {}  # a data structure to store block_number etc per respective socket.
        # TODO: check whether appending/insertion to a dictionary would be more efficient for any other DS?
        self.packet_factory = PacketFactory
        self.listener = None
        self.timeout = timeout

    def handle(self, data, address):
        self._clean_up()   # clean-up TODO: remove clean_up from here?
        if address not in self.client_state.keys():
            logger.info('New client has connected. Connection from {}:{}'.format(address[0], address[1]))
            # check data is valid INITRQ. If not, no point in continuing!
            if self.packet_factory.check_type('initrq', data) and self.packet_factory.is_valid('initrq', data):
                self.client_state[address] = {
                    'transfer_complete': False,
                    'block_number': 0,
                    'file_obj': None,
                    'file_name': None,
                    'last_active': None,
                    'inactive': (lambda: int(time.time() - self.client_state[address]['last_active']))
                }
                # build_up context - update the last_activity period
                self.client_state[address]['last_active'] = time.time()
                # parse the initrq packet
                # get the filename of the file - store it!
                self.client_state[address]['file_name'] = self.packet_factory.from_bytes(data)
                logger.info('Creating new file with name: {} for client {}'.format(
                    self.client_state[address]['file_name'], address
                ))
                # next create a file_obj to that file.
                self.client_state[address]['file_obj'] = FileWriter(
                    self.client_state[address]['file_name'], DATA_SIZE
                )
                # send ack_packet
                self.send_ack(address)
            else:
                logger.warning('Invalid/Malformed INITRQ packet received from client {}'.format(address))
        else:
            # we have already received some data from this client before!
            # determine type of packet
            if self.packet_factory.check_type('initrq', data):
                # May be client hasn't received an ACK.
                # send the ack again
                self.send_ack(address)
            elif self.packet_factory.check_type('data', data):
                # The packet is DATAPacket. Nice! Parse the contents of the packet
                block_no, content = self.packet_factory.from_bytes(data)
                block_no = int(block_no)  # covert block no to int if it is a str # FIXME: remove this
                # check the block_no on the file. Only write when the block_no on the packet +1 than block_number in
                # client's state
                if self.client_state[address]['block_number'] == (block_no - 1):
                    # Write to file
                    self.client_state[address]['file_obj'].write_chunk(content)
                    # increment block_no
                    self.client_state[address]['block_number'] += 1
                    # client is active
                    self.client_state[address]['last_active'] = time.time ()
                elif self.client_state[address]['block_number'] == block_no:
                    # client must have sent the duplicate DATA packet because it received no ack
                    self.send_ack(address)
                    # Ignore all other cases! -- # FIXME: see if there are corner cases remaining
                # check to see if the size of packet is < MAX_SIZE
                # If it is, gracefully disconnect the client. Close the file etc.
                if len(data) < MAX_PACKET_SIZE:
                    logger.info('File Transfer Complete! Wrote {} to disk'.format(
                        self.client_state[address]['file_obj'].name
                    ))
                    self.disconnect_client(address)
            else:
                logger.info('Received data from client. But Not of a valid packet type')

    def send_ack(self, address):
        # client is active
        self.client_state[address]['last_active'] = time.time()
        temp_block_no = self.client_state[address]['block_number']
        # create a awk packet. send that packet
        temp_packet = self.packet_factory.to_bytes(type='ack', block_no=temp_block_no)
        self.listener.socket.sendto(temp_packet, address)

    def disconnect_client(self, address):
        """
        Strictly speaking there is no defined way of gracefully closing a UDP connection.
        We just set the transfer_complete so that buffer is removed by clean_up function
        :return:
        """
        self.client_state[address]['transfer_complete'] = True

    def _clean_up(self, purge=False):
        """
        Cleanup our buffer --> client_state. Remove the entries if the client is not longer active
        """
        for client in list(self.client_state):
            if purge is False:
                if self.client_state[client]['inactive']() > CONN_TIMEOUT \
                        or self.client_state[client]['transfer_complete']:
                    _ = self.client_state.pop(client, None)
                    logger.info('Removing client {} context. Either transfer has completed or client has been inactive '
                                'for over {} seconds'.format(client, CONN_TIMEOUT))
            else:
                _ = self.client_state.pop(client, None)
                logger.info('Forcefully purging client {}'.format(client))

    def start(self, host, port):
        conn = (host, port)
        sock = gevent.socket.socket(gevent.socket.AF_INET, gevent.socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        sock.bind(conn)
        self.listener = DatagramServer(sock, self.handle)
        try:
            # server = gevent.spawn
            self.listener.serve_forever()
        except PYGFTError:
            # FIXME: proper exception handling
            logger.exception('Unable to parse contents, create file for INITRQ')
            # TODO: disconnect the client
        except socket.timeout:
            pass
        except socket.error:
            pass
        except KeyboardInterrupt:
            logger.exception('Received Keyboard Interrupt. Server would gracefully shutdown')
            self.stop()

    def stop(self):
        """Clean up."""
        # Delete files if transfer not complete?
        # Do anything else?
        self._clean_up(purge=True)
        self.listener.close()

"""
The MIT License

Copyright (c) 2018 Abhinav Saxena <xandfury@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

__version__ = "0.1"

# Some useful constants
MAX_PACKET_SIZE = 512
MIN_PACKET_SIZE = 4
DATA_SIZE = MAX_PACKET_SIZE - 4  # payload size of DATA packet. 4 bytes for packet_op_code + packet_block_no
CONN_TIMEOUT = 40  # remove all clients if they are inactive for over 30 seconds(say)
MAX_NO_RESPONSE_TIME = 20  # Disconnect the client if no ACK response is received from the server withing 5 seconds(say)
NO_RESPONSE_TIME = 1  # Resend the last data packet if no ACK is received within this time --- for client

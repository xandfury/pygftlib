# Move to __init__
MAX_PACKET_SIZE = 512
MIN_PACKET_SIZE = 4
DATA_SIZE = MAX_PACKET_SIZE - 4  # payload size of DATA packet. 4 bytes for packet_op_code + packet_block_no
CONN_TIMEOUT = 20  # remove all clients if they are inactive for over 30 seconds(say)
MAX_NO_RESPONSE_TIME = 10  # Disconnect the client if no ACK response is received from the server withing 5 seconds(say)
NO_RESPONSE_TIME = 1  # Resend the last data packet if no ACK is received within this time --- for client

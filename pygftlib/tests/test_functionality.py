import unittest
from pygftlib.protocol import Sender, Receiver
import os, sys
import filecmp
import gevent

current_dir = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(current_dir, "data.txt")


class TestFunctionality(unittest.TestCase):

    def test_lib_functionality(self):
        mock_service = Receiver()
        mock_client_service = Sender(path)
        worker_1 = gevent.spawn(mock_service.start, '127.0.0.1', 12345)
        worker_2 = gevent.spawn(mock_client_service.upload, '127.0.0.1', 12345)

        # Tweak this if unit tests fail
        gevent.joinall([worker_1, worker_2], timeout=2)

        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        file = [file for file in files if '2018-' in file]
        self.assertTrue(filecmp.cmp(str(file[0]), path))
        mock_service.stop()


if __name__ == '__main__':
    unittest.main()
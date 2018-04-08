"""
This module implements functionality to easy read and write to files. Based on gevent's sendfile
"""

import os
from datetime import datetime
from slugify import slugify

import logging as logger
import sys
# logger = logging.getLogger(__name__)
# For debugging --
logger.basicConfig(stream=sys.stdout, level=logger.INFO)
# TODO: More logging in b/w classes


def sanitize_file_name(name):
    """
    Ensure that file_name is legal. Slug the filename and store it onto the server.
    This would ensure that there are no duplicates as far as writing a file is concerned.
    :param name: Name of the file
    :return: slugify the file name to the format -
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' - ' + slugify(name)


class FileReader(object):
    def __init__(self, file_name=None, chunk_size=0):
        self.name = file_name
        self.chunk_size = chunk_size
        self._f = self._open_file()
        self.finished = False

    def _open_file(self):
        logger.debug('Opening File {}'.format(self.name))
        return open(self.name, 'rb')

    def read_chunk(self, size=None):
        size = size or self.chunk_size
        if self.finished:
            return b''

        data = self._f.read(size)
        logger.debug('Reading {} bytes of data from file {} - Contents {}'.format(size, self.name, data))
        if not data or (size > 0 and len(data) < size):
            self._f.close()
            self.finished = True
            logger.debug('Finished reading file {}. Closing!'.format(self.name))
        return data

    def __del__(self):
        if self._f and not self._f.closed:
            self._f.close()


class FileWriter(object):
    def __init__(self, file_name, chunk_size):
        self.name = sanitize_file_name(file_name)
        self.chunk_size = chunk_size
        self._f = self._open_file()

    def _open_file(self):
        logger.debug('Opening File {}'.format(self.name))
        return open(self.name, 'xb')

    def _flush(self):
        if self._f:
            self._f.flush()

    def write_chunk(self, data):
        bytes_written = self._f.write(data)
        logger.debug('Writing {} bytes of data to file {} - Contents {}'.format(self.chunk_size, self.name, data))
        if not data or len(data) < self.chunk_size:
            logger.debug('Finished writing file {}. Closing!'.format (self.name))
            self._f.close()

        return bytes_written

    def __del__(self):
        if self._f and not self._f.closed:
            self._f.close()
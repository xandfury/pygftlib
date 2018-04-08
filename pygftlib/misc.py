import argparse
import sys


class AgrsParse(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Simple Gevent based File Sharing Library',
            usage='''pygftlib <command> [<args>]

There are two modes in which pygftlib. The inner workings are like a protocol in itself. 
Hence in order to transfer files -- You need both sender and receiver
   send       Client mode. One client can send only one file at a time
   receive    Server mode. Capable of handling multiple concurrent connections at the same time
''')
        parser.add_argument('command', help='Subcommand to run')
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def send(self):
        parser = argparse.ArgumentParser(
            description='Send files to a compatible pygftlib server')
        # prefixing the argument with -- means it's optional
        parser.add_argument('filename', help='name of the file that has to be transferred')
        parser.add_argument('--host',
                            help='remote address of the sender(server) you want to send the file to',
                            default='127.0.0.1')
        parser.add_argument('--port', help='port number', default=12345, type=int)
        args = parser.parse_args(sys.argv[2:])
        print(args)

    def receive(self):
        parser = argparse.ArgumentParser(
            description='Start a server to receive files from a compatible client')
        # NOT prefixing the argument with -- means it's not optional
        parser.add_argument('--host', help='Server (Receiver) bind address', default='127.0.0.1')
        parser.add_argument('--port', help='Server (Receiver) bind port', default=12345, type=int)
        args = parser.parse_args(sys.argv[2:])
        print(args)


if __name__ == '__main__':
    AgrsParse()

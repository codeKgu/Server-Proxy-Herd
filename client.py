import asyncio
import time
import sys
from config import *


async def test(msg):
    print(msg)


async def tcp_echo_client(message, message_whatsat, loop):
    try:
        reader, writer = await asyncio.open_connection('127.0.0.1', SERVER_CONFIG[server_name][1],
                                                       loop=loop)
    except ConnectionRefusedError:
        return
    print("connected")
    print('Send: %r' % message)
    writer.write(message.encode())
    data = await reader.read(100)
    print('Received: %r' % data.decode())
    time.sleep(3)
    print('Send: %r' % message_whatsat)

    writer.write(message_whatsat.encode())
    data = await reader.readuntil(b'\n\n')
    print('Received: %r' % data.decode())
    print('Close the socket')


if __name__ == '__main__':
    if (len(sys.argv) != 3):
        print('Invalid number of arguments. Usage: python3 client.py [SERVER NAME] [ID]')
        exit(1)
    server_name = sys.argv[1]
    client_id = sys.argv[2]

    message_iamat = 'IAMAT {} +34.065445-118.444732 {:.9f}\n'.format(client_id, time.time())
    message_whatsat = 'WHATSAT {} 4 4\n'.format(client_id)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tcp_echo_client(message_iamat, message_whatsat, loop))
    loop.close()

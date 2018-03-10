import asyncio
import aiohttp
from config import *
from parse import *
import logging
import sys
import time
import json


def time_diff(client_time):
    server_time = time.time()
    if server_time - float(client_time) >= 0:
        return "+{:.9f}".format(server_time - float(client_time))
    else:
        return "{:.9f}".format(server_time - float(client_time))


def log(logger, message, entry='INPUT'):
    logger.info("{}: {}".format(entry, message.rstrip()))


async def request_gmaps(url_request):
    async with aiohttp.ClientSession() as session:
        async with session.get(url_request) as resp:
            return await resp.json()


class server:
    def __init__(self, server_name, server_config):
        self._name = server_name
        self._neighbors = dict.fromkeys(SERVER_CONFIG[server_name][0])
        self._logger = logging.getLogger(server_name)
        self._hdlr = logging.FileHandler('{}.log'.format(server_name))
        self._logger.setLevel(logging.INFO)
        self._logger.addHandler(self._hdlr)
        self._clients = {}

    def most_recent_client(self, pmessage, response_message):
        if not pmessage.id in self._clients or (float(pmessage.time) > self._clients[pmessage.id]["time"]):
            self._clients[pmessage.id] = {"time": float(pmessage.time), "lat": pmessage.lat, "long": pmessage.long, "string": response_message.rstrip()}
            return False
        return True

    async def flood_neighbors(self, message):
        already_flooded = message.split()[5:]
        for server in SERVER_CONFIG[self._name][0]:
            if server not in already_flooded:
                flood_message = "{} {}\n".format(message.rstrip(), self._name)
                await self.flood_server(server, flood_message)

    async def flood_server(self, server, message):
        try:
            reader, writer = await asyncio.open_connection('127.0.0.1', SERVER_CONFIG[server][1],
                                                           loop=loop)
            print("CONNECTED to {}".format(server))
            log(self._logger, "CONNECTED to {}".format(server), entry="INTERNAL")
            log(self._logger, message, entry="OUTPUT to {}".format(server))
            writer.write(message.encode())
            writer.close()
            print("DISCONNECTED with {}".format(server))
            log(self._logger, "DISCONNECTED with {}".format(server), entry="INTERNAL")
        except ConnectionRefusedError:
            log(self._logger, "CANNOT CONNECT to: {}".format(server), entry="INTERNAL")
            print("CANNOT CONNECT connect to: {}".format(server))
        return

    async def handle_imat(self, pmessage, message):
        response_message = "AT {} {} {} {} {}\n".format(self._name, time_diff(float(pmessage.time)),
                                                        pmessage.id, pmessage.loc, pmessage.time)
        log(self._logger, response_message, entry='OUTPUT')
        if not self.most_recent_client(pmessage, response_message):
            await self.flood_neighbors("FLOOD {}".format(response_message))
        return response_message

    async def handle_whatsat(self, pmessage):
        if pmessage.id not in self._clients:
            response_message = NONE
        else:
            request_url = "{}location={},{}&radius={}&key={}".format(REQUEST_URL, self._clients[pmessage.id]["lat"], self._clients[pmessage.id]["long"], 1000 * pmessage.radius, API_KEY)
            response_json = await request_gmaps(request_url)
            response_json['results'] = response_json['results'][:pmessage.num_results]
            response_str = "{}\n".format(json.dumps(response_json, indent=3))
            response_str = [char for char, next_char in zip(response_str[0:-1], response_str[1:]) if not(char == '\n' and next_char == '\n')]
            response_str = "".join(response_str)
            response_message = "{}\n{}\n\n".format(self._clients[pmessage.id]["string"], response_str)
            log(self._logger, response_message, entry="OUTPUT")
        return response_message

    async def handle_client(self, reader, writer):
        loop.create_task(self.handle_maintained_client(reader, writer))

    async def handle_maintained_client(self, reader, writer):
        try:
            data = await reader.readuntil('\n')
            messages = data.decode()
            message_arr = messages.splitlines(keepends=True)
            print(message_arr)
            for message in message_arr:
                print(message)
                response = await self.handle_message(message)
                # print(response)
                # response is only NONE for communication between servers
                if response != NONE:
                    writer.write(response.encode())
                    await writer.drain()
                else:
                    writer.close()
            await self.handle_maintained_client(reader, writer)

        except ConnectionResetError:
            # if cannot connect to server close
            writer.close()

    async def handle_message(self, message):
        log(self._logger, message)
        striped_message = message.strip()
        parsed_message = ParseMessage(striped_message)
        pmessage_type = parsed_message.check_command()
        response_msg = "? {}".format(message)
        if pmessage_type == IAMAT and parsed_message.check_iamat():
            print("RECIEVED: {} FROM CLIENT {}".format(message.rstrip(), parsed_message.id))
            response_msg = await self.handle_imat(parsed_message, message)
            print("SEND: {}".format(response_msg.rstrip()))
        elif pmessage_type == WHATSAT and parsed_message.check_whatsat():
            print("RECIEVED {} FROM CLIENT {}".format(message.rstrip(), parsed_message.id))
            whatsat_msg = await self.handle_whatsat(parsed_message)
            if whatsat_msg != NONE:
                response_msg = whatsat_msg
            else:
                log(self._logger, response_msg, entry="OUTPUT")
            print("SEND: {}".format(response_msg))
        elif pmessage_type == FLOOD:
            print("RECIEVED {}".format(message.rstrip()))
            self.most_recent_client(parsed_message, " ".join(message.split()[1:7]))
            await self.flood_neighbors(message)
            response_msg = NONE
        else:
            print("SEND: {}".format(response_msg))
            log(self._logger, response_msg, entry="OUTPUT")
        return response_msg


if __name__ == '__main__':
    if (len(sys.argv) != 2):
        print('Invalid number of arguments. Usage: python3 server.py [SERVER NAME]')
        exit(1)

    server_name = sys.argv[1]
    if not server_name in SERVER_IDS:
        print("Invalid server id. Server ids: Goloman, Hands, Holiday, Welsh, Wilkes")

    server = server(server_name, SERVER_CONFIG[server_name])
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(server.handle_client, '127.0.0.1', SERVER_CONFIG[server_name][1], loop=loop)
    server = loop.run_until_complete(coro)
    print(SERVER_CONFIG[server_name][0])
    # Serve requests until Ctrl+C is pressed
    print('************************  START *******************************')
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


# event loop runs coroutine, basically runs next on coroutine awaits on stuff until the lowest level yeilds and schedules

# Server-Proxy-Herd using Python with [asyncio](https://docs.python.org/3/library/asyncio.html) and [aiohttp](https://aiohttp.readthedocs.io/en/stable/)
## Project for CS131 Winter 2018
Spec: https://web.cs.ucla.edu/classes/winter18/cs131/hw/pr.html

Python dependencies: see requirements.txt
### To run a server
```
python server.py [Server Name]
```
Server names are: Goloman, Holiday, Hands, Wilkes, Welsh (see config.py)
### To talk to server
#### Run clieny.py
```
python client.py [Server Name] [id]
```
#### Use telnet
In terminal:
```
telnet 127.0.0.1 [Port of server]
```
For ports associated with server see config.py
Then run requests
##### IAMAT
Tell server where you are of the form

\[Command] [Client ID]  [ISO 6709 Location] [POSIX/UNIX Time]
```
IAMAT kiwi.cs.ucla.edu +34.068930-118.445127 1479413884.392014450 
```
##### WHATSAT
Ask server for JSON list of locations near a client as given by the [Google Places API](https://developers.google.com/places/)
```
WHATSAT kiwi.cs.ucla.edu 5 10
        [Client ID][Radius(km)][Number of Results]
```

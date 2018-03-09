import aiohttp
import asyncio
import time
url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=+34.068930,-118.445127&radius=3000&key=AIzaSyC-pALbeZ1iks-6xlsC4EQMa72kiOzf-No"


async def maps_http_request(url_request):
    async with aiohttp.ClientSession() as session:
        async with session.get(url_request) as resp:
            return await resp.text()


async def main(url):
    print("in")
    result = await maps_http_request(url)
    print(result)
    print("out")


if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(url))
    print(time.time())

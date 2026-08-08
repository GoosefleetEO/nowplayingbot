from discord_webhook import DiscordWebhook
import json
import aiohttp
import asyncio

webhook_url = "https://discord.com/api/webhooks/webook_goes_here"
metadata_url = "https://radio.station.invalid/metadata_endpoint"

async def main():
    artist = None
    title = None
    old_artist = None
    old_title = None

    while True:
        print("Loop start")
        async with aiohttp.ClientSession() as session:
            async with session.get(metadata_url) as response:

                result = json.loads(await response.text())
                print(result)
                if "artist" in result:
                    artist = result["artist"]
                    print(artist)
                else:
                    artist = None

                if "title" in result:
                    title = result["title"]
                    print(title)
                else:
                    title = "tell corgski to fix the metadata"

                if artist != old_artist or title != old_title:
                    message = f'Now Playing {title}' if artist is None else f'Now Playing {artist} - {title}'
                    webhook = DiscordWebhook(url=webhook_url, content=message)
                    response = webhook.execute()
                    old_artist = artist
                    old_title = title

        await asyncio.sleep(1)

asyncio.run(main())
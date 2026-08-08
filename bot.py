from discord_webhook import DiscordWebhook, DiscordEmbed
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
    webhook_resp = None

    while True:
        print("Loop start")
        webhook = DiscordWebhook(url=webhook_url)
        webhook.content = "Listen live at [HonksFM](https://honks.goosegoo.se)"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(metadata_url) as response:

                result = json.loads(await response.text())
                print(result)
                if "artist" in result:
                    artist = result["artist"]
                    print(artist)
                else:
                    artist = "Unknown Artist"

                if "title" in result:
                    title = result["title"]
                    print(title)
                else:
                    title = "tell corgski to fix the metadata"

                if artist != old_artist or title != old_title:
                    embed = DiscordEmbed(
                        title = "Now Playing",
                        description = "Now playing on HonksFM",
                        color = "ffa500"
                    )
                    
                    embed.add_embed_field(name="artist", value=artist)
                    embed.add_embed_field(name="title", value=title)
                    
                    webhook.remove_embeds()
                    webhook.add_embed(embed)
                    
                    if webhook_resp is None:
                        webhook_resp = webhook.execute()
                    else:
                        webhook_resp = webhook.edit()
                    old_artist = artist
                    old_title = title

        await asyncio.sleep(1)

asyncio.run(main())
from discord_webhook import DiscordWebhook, DiscordEmbed
import json
import aiohttp
import asyncio
import yaml

with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

#webhook_url = "https://discord.com/api/webhooks/webook_goes_here"
#metadata_url = "https://radio.station.invalid/metadata_endpoint"

async def main():
    artist = None
    title = None
    old_artist = None
    old_title = None
    metadata_url = config['host']
    webhooks = {}
    for name, hook in config['webhooks'].items():
        if "id" in hook:
            print(f'Reusing existing post for {name}')
            webhook = DiscordWebhook(url=hook['url'],id=hook['id'])
        else:
            print(f'Not reusing post for {name}')
            webhook = DiscordWebhook(url=hook['url'])
        
        webhooks[name] = {"hook": webhook, "type": hook['type']}

    while True:
        
        async with aiohttp.ClientSession() as session:
            async with session.get(metadata_url) as response:
                try:
                    parsed_result = {}
                    result = json.loads(await response.text())
                    for row in result:
                        parsed_result[row[0]] = row[1]
                except Exception:
                    asyncio.sleep(15)
                    print("Server offline, waiting 15s")
                    continue
                
                if "artist" in parsed_result:
                    artist = parsed_result["artist"]
                else:
                    artist = "Unknown Artist"

                if "title" in parsed_result:
                    title = parsed_result["title"]
                else:
                    title = "tell corgski to fix the metadata"

                if artist != old_artist or title != old_title:
                    
                    for name, hook in webhooks.items():
                        if hook['type'] == "nowplaying":
                            
                            webhook = hook["hook"]

                            webhook.content = "Listen live to [HonksFM](https://honks.goosegoo.se)"
                            
                            embed = DiscordEmbed(
                                title = "HonksFM",
                                color = "ffa500"
                            )
                            
                            embed.add_embed_field(name="artist", value=artist)
                            embed.add_embed_field(name="title", value=title)
                            embed.set_image(url="https://goosegoo.se/images/honkart.jpg")
                            
                            webhook.remove_embeds()
                            webhook.add_embed(embed)
                            
                            if webhook.id is None:
                                webhook.execute()
                                hook['id'] = webhook.id
                                config['webhooks'][name]['id'] = webhook.id
                                
                                with open('config.yml', 'w') as file:
                                    yaml.safe_dump(config, file)
                            else:
                                webhook.edit()
                                
                        elif hook['type'] == "log":
                            webhook = hook["hook"]

                            embed = DiscordEmbed(
                                title = "Now Playing",
                                color = "ffa500"
                            )
                            
                            embed.add_embed_field(name="artist", value=artist)
                            embed.add_embed_field(name="title", value=title)
                            embed.add_embed_field(name="path", value=parsed_result['filename'])
                            webhook.remove_embeds()
                            webhook.add_embed(embed)
                            webhook.execute()

                    old_artist = artist
                    old_title = title

        await asyncio.sleep(1)

asyncio.run(main())
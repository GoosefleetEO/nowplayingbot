from discord_webhook import DiscordWebhook, DiscordEmbed
import json
import aiohttp
import asyncio
import yaml
import datetime

with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

async def main():
    old_filename = None
    metadata_url = config['host']
    webhooks = {}
    color = 'ff0000' if 'color' not in config else config['color']
    default_artist = 'Unknown' if ('defaults' not in config and 'artist' not in config['defaults']['artist']) else config['defaults']['artist']
    default_title = 'Untitled' if ('defaults' not in config and 'title' not in config['defaults']['title']) else config['defaults']['title']
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
                    print("Server offline, waiting 15s")
                    asyncio.sleep(15)
                    continue
                
        if "artist" in parsed_result:
            artist = parsed_result["artist"]
        else:
            artist = default_artist

        if "title" in parsed_result:
            title = parsed_result["title"]
        else:
            title = default_title

        if old_filename == parsed_result['filename']:
            await asyncio.sleep(1)
            continue

        for name, hook in webhooks.items():
            if hook['type'] == "nowplaying":
                
                webhook = hook["hook"]

                webhook.content = "Listen live to [HonksFM](https://honks.goosegoo.se)"
                
                embed = DiscordEmbed(
                    title = "HonksFM",
                    color = color
                )
                
                duration = str(datetime.timedelta(seconds=float(parsed_result['liq_cue_out'])))
                
                embed.add_embed_field(name="artist", value=artist)
                embed.add_embed_field(name="title", value=title)
                embed.add_embed_field(name="duration", value=duration, inline=False)
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
                    color = color
                )
                
                duration = str(datetime.timedelta(seconds=float(parsed_result['liq_cue_out'])))
                
                embed.add_embed_field(name="artist", value=artist)
                embed.add_embed_field(name="title", value=title)
                embed.add_embed_field(name="duration", value=duration, inline=False)
                embed.add_embed_field(name="path", value=parsed_result['filename'])
                webhook.remove_embeds()
                webhook.add_embed(embed)
                webhook.execute()

        old_filename = parsed_result['filename']

        await asyncio.sleep(1)

asyncio.run(main())
from discord_webhook import DiscordWebhook
import json
import aiohttp
import asyncio

webhook_url = "http://example.webhook.invalid"
metadata_url = "http://example.metadata.invalid"

async def main():
	artist = None
	title = None
	old_artist = None
	old_title = None

	while True:
		async with aiohttp.ClientSession() as session:
			async with session.get(metadata_url) as response:
				
				result = json.loads(await response.text())
				
				if "artist" in result:
					artist = result["artist"]
				else:
					artist = None
				
				if "title" in result:
					title = result["title"]
				else:
					title = "tell corgski to fix the metadata"
				
				if artist != old_artist or title != old_title:				
					message = f'Now Playing {artist} - {title}' if artist else f'Now Playing {title}'
					webhook = DiscordWebhook(url=webhookurl, content=message)
					old_artist = artist
					old_title = title
				
		asyncio.sleep(1)
		
import aiohttp
import asyncio
import discord
import logging
import os

class FamBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

    async def on_ready(self):
        self.logger.info(f'Connected to Discord as {self.user}')

    async def on_message(self, message):
        # #TODO: More precise check by looking for member of bot group.
        # if message.author == self.user:
        #     return

        if message.content.startswith('$fambot'):
            #TODO: Use argparse or something better to parse arguments.
            args = message.content.split()[1:]
            call = args[0].strip().lower()
            if call == 'help':
                await self.help(message, args)
            elif call == 'echo':
                await self.echo(message, args)
            elif call == 'compare-weather':
                await self.compare_weather(message, args)

    async def help(self, message, args):
        await message.channel.send('$fambot echo <message>: repeat back a message')

    async def echo(self, message, args):
        await message.channel.send(' '.join(args[1:]))

    async def compare_weather(self, message, args):
        base_url = f"https://api.weatherapi.com/v1/current.json?key={os.environ.get('WEATHER_API_KEY')}"
        args = "&q={}&aqi=no"

        async with aiohttp.ClientSession() as session:
            tasks = [self._call_api(base_url + args.format(loc), session=session) for loc in os.environ.get("WEATHER_LOCATIONS").split(",")]
            responses = await asyncio.gather(*tasks)
            result = 'The current temperature and weather conditions are...\n'
            for resp in responses:
                result += f'{resp["location"]["name"]}, {resp["location"]["region"]}: {resp["current"]["temp_f"]}F and {resp["current"]["condition"]["text"]}\n'
            await message.channel.send(result)

    async def _call_api(self, url, session=None):
        if session is None:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    return await resp.json()
        else:
            async with session.get(url) as resp:
                return await resp.json()

def get_client():
    intents = discord.Intents.none()
    intents.guilds = True
    intents.messages = True
    intents.message_content = True

    return FamBot(intents=intents)

if __name__ == '__main__':
    client = get_client()
    client.run(os.environ.get("DISCORD_TOKEN"), log_level=logging.DEBUG)

import aiohttp
import asyncio
import discord
import logging
import io
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
            tasks = [self._pull_weather_and_report(base_url + args.format(loc), session, message.channel) for loc in os.environ.get("WEATHER_LOCATIONS").split(",")]
            await asyncio.gather(*tasks)

    async def _pull_weather_and_report(self, url, session, channel):
        response = await self._call_api(url, session=session)
        icon = f'https:{response["current"]["condition"]["icon"]}'
        async with session.get(icon) as icon_response:
            if icon_response.status != 200:
                file=None
            else:
                data = io.BytesIO(await icon_response.read())
                filename = f'{response["current"]["condition"]["text"]}.png'
                file = discord.File(data, filename=filename)
        answer = f'Weather for {response["location"]["name"]}, {response["location"]["region"]}: {response["current"]["condition"]["text"]} and {response["current"]["temp_f"]}F'
        await channel.send(answer, file=file)

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

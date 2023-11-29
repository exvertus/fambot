import aiohttp
import asyncio
import discord
import logging
import io
import openai
import os

class FamBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        # self.llm_client = openai.AsyncOpenAI()

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
            # else:
            #     await self.ask_llm(message, args)

    # async def ask_llm(self, message, args):
    #     completion = await self.llm_client.chat.completions.create(
    #         model="gpt-3.5-turbo",
    #         messages=[
    #             {"role": "system", 
    #              "content": f"You are a Discord bot named {os.environ.get('BOT_NAME')} and you are chatting with a family of adults." + 
    #              "The bot messages not already handled by commands are passed to you as a catch-all prior to human-review." +
    #              "While you are a functioning as a chatbot and should behave as such," +
    #              "You are an autoregressive language model that has been fine-tuned with instruction-tuning and RLHF."  +
    #              "You carefully provide accurate, factual, thoughtful, nuanced answers, and are brilliant at reasoning. " +
    #              "If you think there might not be a correct answer, you say so." +
    #              "Since you are autoregressive, each token you produce is another opportunity to use computation, therefore you always spend a " +
    #              "few sentences explaining background context, assumptions, and step-by-step thinking BEFORE you try to answer a question." +
    #              f"You were created by {os.environ.get('BOT_CREATOR')} and suggest asking them instead when you do not know the answer."},
    #              {"role": "user", "content": message.content}
    #         ])
    #     print('breakpoint')

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
        icon_url = f'https:{response["current"]["condition"]["icon"]}'
        name = f'{response["current"]["condition"]["text"]}.png'
        icon = await self.weather_icon(icon_url, session, name)
        answer = f'Weather for {response["location"]["name"]}, {response["location"]["region"]}: {response["current"]["condition"]["text"]} and {response["current"]["temp_f"]}F'
        await channel.send(answer, file=icon)

    async def weather_icon(self, icon_url, session, name):
        async with session.get(icon_url) as icon_response:
            if icon_response.status != 200:
                return None
            else:
                data = io.BytesIO(await icon_response.read())
                return discord.File(data, filename=name)

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

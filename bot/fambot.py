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

    async def help(self, message, args):
        await message.channel.send('$fambot echo <message>: repeat back a message')

    async def echo(self, message, args):
        await message.channel.send(' '.join(args[1:]))

def get_client():
    intents = discord.Intents.none()
    intents.guilds = True
    intents.messages = True
    intents.message_content = True

    return FamBot(intents=intents)

if __name__ == '__main__':
    client = get_client()
    client.run(os.environ.get("DISCORD_TOKEN"), log_level=logging.DEBUG)

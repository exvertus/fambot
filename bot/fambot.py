import discord
import logging
import os

class FamBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.call_response = {
            'help': self._help,
            'echo': self._echo,
            'introduce': self._introduce
        }

    async def on_ready(self):
        self.logger.info(f'Connected to Discord as {self.user}')

    async def on_message(self, message):
        #TODO: More precise check by looking for member of bot group.
        if message.author == self.user:
            return

        if message.content.startswith('$fambot'):
            #TODO: Use argparse to parse arguments.
            args = message.content.split()[1:]
            call = args[0].strip().lower()
            if call == 'shutdown':
                await message.channel.send('Goodbye, I am going to take a nap now.')
                await self.close()
            else:
                method = self.call_response.get(call, self._help)
                await method(message, args)

    def _help(self, message, args):
        return message.channel.send('Help menu coming soon...')

    def _echo(self, message, args):
        return message.channel.send(' '.join(args[1:]))
    
    def _introduce(self, message, args):
        return message.channel.send('Hello, I am FamBot. I am still a baby and take lots of naps but I will learn more soon.')

intents = discord.Intents.none()
intents.messages = True
intents.message_content = True

client = FamBot(intents=intents)

client.run(os.environ.get("DISCORD_TOKEN"), log_level=logging.DEBUG)

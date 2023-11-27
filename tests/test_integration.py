import asyncio
import os
import pytest
import pytest_asyncio
import uuid
import bot.fambot as fambot

class TestIntegration:
    @pytest_asyncio.fixture
    async def client(self):
        client = fambot.get_client()
        yield client
        await client.close()

    @pytest_asyncio.fixture
    async def connected_client(self, client):
        await client.login(os.environ.get("DISCORD_TOKEN"))
        client_task = asyncio.create_task(
            client.connect())
        await client.wait_until_ready()
        yield client
        await client.close()
        await client_task

    @pytest.mark.asyncio
    async def test_echo(self, connected_client):
        """
        Test that the bot can echo a unique message and read back the value.
        """
        bot_channel = connected_client.get_channel(int(os.environ.get("CHANNEL_ID")))
        test_message = str(uuid.uuid4())
        await bot_channel.send(f'$fambot echo {test_message}')
        await asyncio.sleep(1)
        assert bot_channel.last_message.content == test_message

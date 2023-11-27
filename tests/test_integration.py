import asyncio
import os
import pytest
import pytest_asyncio
import uuid
import bot.fambot as fambot

class TestIntegrationDiscord:
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
        def check(m):
            return m.author == connected_client.user and m.channel == bot_channel
        await connected_client.wait_for('message', timeout=3)
        assert bot_channel.last_message.content == test_message

    @pytest.mark.asyncio
    async def test_compare_weather(self, connected_client):
        """
        Test that the bot can compare the weather in multiple locations.
        """
        bot_channel = connected_client.get_channel(int(os.environ.get("CHANNEL_ID")))
        await bot_channel.send(f'$fambot compare-weather')
        def check(m):
            return m.author == connected_client.user and m.channel == bot_channel
        await connected_client.wait_for('message', timeout=60)
        assert bot_channel.last_message.content.startswith('Weather for ')

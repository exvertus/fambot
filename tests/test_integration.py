import asyncio
import discord
import io
import os
import pathlib
import pytest
import pytest_asyncio
import unittest.mock
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
        mock_icon_path = pathlib.Path(__file__).parent / 'mock-icon.png'
        with open(mock_icon_path.resolve(), 'rb') as dummy_icon:
            mock_icon_bytes = dummy_icon.read()
        mock_icon = discord.File(io.BytesIO(mock_icon_bytes), filename='mock-icon.png')

        with unittest.mock.patch('bot.fambot.FamBot._call_api') as mock_call_api, \
            unittest.mock.patch('bot.fambot.FamBot.weather_icon', return_value=mock_icon):
            mock_call_api.return_value = ({
                "location": {"name": "MockCity", "region": "MockRegion"},
                "current": {"condition": {"text": "Sunny", "icon": "//mockicon.png"}, "temp_f": 75.0}
            })
            bot_channel = connected_client.get_channel(int(os.environ.get("CHANNEL_ID")))
            await bot_channel.send(f'$fambot compare-weather')
            def check(m):
                return m.author == connected_client.user and m.channel == bot_channel
            await connected_client.wait_for('message', timeout=10, check=check)
            assert bot_channel.last_message.content.startswith('Weather for MockCity, MockRegion: Sunny and 75.0F')

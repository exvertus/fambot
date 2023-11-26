import logging
import os
import pytest
import uuid
import bot.fambot as fambot

class TestIntegration:
    # def test_self_message_ignored(self):
    #     """
    #     Test that the bot ignores messages from itself.
    #     """
    #     assert False

    def test_echo(self):
        """
        Test that the bot can echo a unique message and read back the value.
        """
        client = fambot.get_client()
        client.run(os.environ.get("DISCORD_TOKEN"), log_level=logging.DEBUG)
        print('breakpoint-1')

    def test_help(self):
        """
        Test that the bot can respond to a help command.
        """
        assert False

from discord import Guild
from lib.chat import Chat
from lib.api import DiscordClientBot

class Events(object):
    def __init__(self, window, loop):
        self.window = window
        self.bot = DiscordClientBot(
            self.window,
            None,
            command_prefix="18738131x"
        )
        self.chat = Chat(self.window, loop, self.bot)


    def onClick(self, guild, *args):
        if isinstance(guild, Guild):
            self.chat.processGuild(guild)

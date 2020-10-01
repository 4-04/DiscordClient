from discord import Guild
import random
import string
from lib.chat import Chat
from lib.api import DiscordClientBot

class Events(object):
    def __init__(self, window, loop):
        self.window = window
        self._randPrefix = ''.join(random.choice(string.ascii_letters) for _ in range(20))
        self.bot = DiscordClientBot(
            self.window,
            None,
            command_prefix=self.getPrefix
        )
        self.chat = Chat(self.window, loop, self.bot)

    async def getPrefix(self):
        if self.window.isbot:
            return self.window.entry_prefix.text()
        return self._randPrefix

    def onClick(self, guild, *args):
        if isinstance(guild, Guild):
            self.chat.processGuild(guild)

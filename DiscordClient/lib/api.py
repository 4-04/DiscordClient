import discord
from discord.ext import commands, tasks
from functools import partial
from PyQt5 import QtWidgets

class DiscordClientBot(commands.Bot):
    def __init__(self, window, createf, *args, **kwargs):
        self.window, self.createf = window, createf
        self.latest_messages = []
        super().__init__(*args, **kwargs)

    async def sendMessage(self, content, channel):
        await channel.send(content)

    async def fetchLatest(self, func, channel, amount):
        try:
            for msg in await channel.history(limit=amount).flatten():
                func(msg, channel.id)
        except discord.errors.Forbidden:
            pass

    async def on_message(self, msg):
        self.window.events.chat.addMsg(msg, msg.channel.id)

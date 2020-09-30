from PyQt5 import QtWidgets, uic, QtCore
from functools import partial
from discord import DMChannel
import asyncio
import sys
import os


class Chat(object):
    def __init__(self, window, loop, bot):
        self.window = window
        self.loop = loop
        self.bot = bot
        self.current_guild = None
        self.current_channel = None
        self.frames = {} # {channel_id: [frame, layout, fetched]}
        self.window.button_home.clicked.connect(self.loadHome)

    def clearLayout(self, layout):
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)

    def addSelf(self):
        if not self.current_channel:
            return
        text = self.window.message_send.toPlainText()
        self.addMsg(
            text,
            self.current_channel
        )
        self.window.message_send.setText("")
        self.loop.create_task(self.bot.sendMessage(text, self.current_channel))


    def addMsg(self, msg, channel):
        frame = self.frames.get(channel)
        if not frame:
            return
        frame, layout, _ = frame
        text = "<b style='color: white;'>{0}<b>\n<p style='color: #D6D7D4;'>{1}</p>".format(msg.author, msg.content)
        label = QtWidgets.QLabel(frame)
        label.setMaximumSize(QtCore.QSize(16777215, 50))
        label.setOpenExternalLinks(True)
        label.setText(text)
        label.setStyleSheet("border: 1px solid black;")
        layout.addWidget(label)

    def createFrame(self):
        frame = QtWidgets.QFrame(self.window.scrollAreaWidgetContents)
        frame.setStyleSheet("border: 0px;")
        frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frame.setFrameShadow(QtWidgets.QFrame.Raised)
        layout = QtWidgets.QVBoxLayout(frame)
        layout.setContentsMargins(-1, -1, 11, -1)
        return frame, layout


    def createGuildButton(self, guild):
        button = QtWidgets.QPushButton(self.window.frame)
        button.setText(guild.name)
        button.clicked.connect(
            partial(
                self.processGuild,
                guild
            )
        )
        self.window.verticalLayout.addWidget(button)

    def createChannels(self, guild):
        self.clearLayout(self.window.verticalLayout_5)
        for category in guild.categories:
            ## line (frame) ##
            line = QtWidgets.QLabel(self.window.frame_3)
            line.setText("<h3>{0}</h3>".format(category.name))
            line.setStyleSheet("border: 1px solid black; background-color: white;")
            self.window.verticalLayout_5.addWidget(line)
            ## channels ##
            for channel in category.text_channels:
                button = QtWidgets.QPushButton(self.window.frame_3)
                button.setText("#{0}".format(channel.name))
                button.setToolTip("Channel ID: {0}\nGuild ID {1}\nMembers: {2}".format(channel.id, channel.guild.name, len(channel.members)))
                button.clicked.connect(partial(self.processChannel, channel))
                self.window.verticalLayout_5.addWidget(button)

    def processChannel(self, channel):
        self.clearLayout(self.window.gridLayout_4)
        self.current_channel = channel
        frame = self.frames.get(channel.id)
        if not frame:
            frame, layout = self.createFrame()
            fetched = False
            self.frames[channel.id] = [frame, layout, fetched]
        else:
            frame, layout, fetched = framex
        if self.window.fetch_previous and not fetched:
            self.frames[channel.id] = [frame, layout, True]
            self.loop.create_task(self.bot.fetchLatest(self.addMsg, channel, self.window.fetch_amount))
        if self.window.load_members and hasattr(channel, 'members'):
            for member in channel.members:
                label = QtWidgets.QLabel(self.window.scrollAreaWidgetContents_3)
                label.setText(member.name)
                label.setToolTip("Member ID: {0}".format(member.id))
                self.window.verticalLayout_6.addWidget(label)
        name = channel.recipient.name if isinstance(channel, DMChannel) else channel.name
        self.window.channel_name.setText("<h1># {0}</h1>".format(name))
        self.window.gridLayout_4.addWidget(frame, 0, 0, 1, 1)


    def processGuild(self, guild):
        if self.current_guild == guild or not guild:
            return
        self.clearLayout(self.window.gridLayout_4)
        self.current_guild = guild
        self.createChannels(guild)


    def loadHome(self):
        self.clearLayout(self.window.verticalLayout_5)
        for channel in self.bot.private_channels:
            button = QtWidgets.QPushButton(self.window.frame_3)
            button.setText("#{0}".format(channel.recipient.name))
            button.setToolTip("Channel ID: {0}".format(channel.id))
            button.clicked.connect(partial(self.processChannel, channel))
            self.window.verticalLayout_5.addWidget(button)

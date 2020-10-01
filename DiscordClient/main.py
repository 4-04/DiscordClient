from PyQt5 import QtWidgets, uic, QtCore, QtGui
from functools import partial
from time import sleep
from qasync import QEventLoop, asyncSlot
import asyncio
import sys
import os
from lib.events import Events




class DiscordClient(QtWidgets.QMainWindow):
    signal_start_background_job = QtCore.pyqtSignal()
    def __init__(self, loop, *args, **kwargs):
        super(DiscordClient, self).__init__(*args, **kwargs)
        uic.loadUi(os.path.join('gui', 'discordclient.ui'), self)
        self.events = Events(self, loop)
        self.message_send.installEventFilter(self)
        self.token = ""
        self.isbot = False
        self.created = False


        self.button_connect.clicked.connect(self.connectDiscord)
        self.start()

    def showError(self, text):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(text)
        msg.setWindowTitle("Error")
        msg.exec_()

    @asyncSlot()
    async def connectDiscord(self):
        self.token = self.input_token.text().strip()
        if not self.token:
            return self.showError("Please fill out your account token in the settings tab.")
        # print(dir(self))
        self.isbot = str(self.type_account.currentText()).lower().startswith("bot")
        try:
            QtCore.QTimer.singleShot(5000, self.connectApi)
            await self.events.bot.start(self.token, bot=self.isbot)
            self.created = True
        except Exception as e:
            print(E)
            self.showError("Invalid token")


    def connectApi(self):
        self.username.setText(self.events.bot.user.name)
        self.tag.setText(self.events.bot.user.discriminator)
        self.account_type.setText('Account type: <b>{0}<b>'.format('Normal' if not self.events.bot.user.bot else 'Bot'))
        for guild in self.events.bot.guilds:
            self.events.chat.createGuildButton(guild)
        self.button_connect.setText("Connected to Discord.")

    def closEvent(self, event):
        self.events.bot.close()
        event.accept()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress and obj is self.message_send:
            if event.key() == QtCore.Qt.Key_Return and self.message_send.hasFocus():
                if not QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
                    self.events.chat.addSelf()
        return super().eventFilter(obj, event)

    def bindButtons(self):
        for item in self.__dict__:
            obj = self.__dict__[item]
            if isinstance(obj, QtWidgets.QPushButton) or isinstance(obj, QtWidgets.QToolButton):
                self.__dict__[item].clicked.connect(
                    partial(
                        self.events.onClick,
                        obj,
                        item
                    )
                )

    def start(self):
        self.bindButtons()
        self.show()



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    w = DiscordClient(loop)
    w.show()
    loop.run_forever()

    sys.exit(app.exec_())

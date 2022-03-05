import sys
import threading

from PyQt5 import QtWidgets

from client import Client, send_if_validate, choose_file_and_send
from views.home_view import HomeWindow
from views.chat_view import ChatWindow


def run_client(nickname_input):
    client.set_nickname(nickname_input)
    client.set_gui(chat)
    # client.set_app(app)
    client.run()


def switch_window(current_window, new_window):
    nickname_input = home.validate()

    if current_window.validate():
        # open new window
        new_window.show()

        # close current window
        current_window.close()

        # run client in new thread
        if nickname_input:
            client_thread = threading.Thread(target=run_client, args=(nickname_input,))
            client_thread.start()


if __name__ == "__main__":
    client = Client()

    app = QtWidgets.QApplication(sys.argv)

    home = HomeWindow()
    chat = ChatWindow()

    home.next_btn.clicked.connect(lambda: switch_window(home, chat))
    home.close_btn.clicked.connect(lambda: home.close())

    chat.send_btn.clicked.connect(lambda: send_if_validate(client))
    chat.choose_file_btn.clicked.connect(lambda: choose_file_and_send(client, 'U'))
    chat.multicast_btn.clicked.connect(lambda: choose_file_and_send(client, 'M'))

    home.show()

    app.lastWindowClosed.connect(lambda: client.disconnect() if client.connected else None)
    sys.exit(app.exec_())

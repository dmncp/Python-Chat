import socket
import sys
import threading
import random
from PyQt5 import QtWidgets, QtGui, QtCore
from PIL import Image
import io

serverIP = "127.0.0.1"
multicastIP = '224.1.1.1'
serverPort = 9008
multicastPort = 5007
buff_size = 1024
buff_size_udp = 65507  # maximum size of data into a single UDP packet = 64KB


def display(message, client_id, client_name, client_color, gui):
    # 1. create widget list item and set text: "ID: client_id | From: client_name \n message"
    if client_id:
        msg = f'ID: {client_id} | From: {client_name} \n{message}'
    else:
        msg = f'From: {client_name} \n{message}'
    item = QtWidgets.QListWidgetItem(msg)
    item.setFont(QtGui.QFont('Arial', 15))

    # 2. set background color to client_color
    item.setBackground(QtGui.QColor(client_color))

    # 3. add widget item to listWidget
    gui.listWidget.addItem(item)


def display_image(data, width, height, client, color):
    # 1. icon size on chat dialog
    max_width = 400
    if width != 0:
        max_height = int(max_width * height / width)
    else:
        max_height = 0

    img_to_display = QtGui.QIcon(data)
    item = QtWidgets.QListWidgetItem(img_to_display, '')
    item.setBackground(QtGui.QColor(color))

    # 3. add to listWidget
    client.client_gui.listWidget.setIconSize(QtCore.QSize(max_width, max_height))
    client.client_gui.listWidget.addItem(item)


def convert_to_img_and_display(msg_bytes, client, color):
    # 1. generate pixmap using received bytes
    pixmap = QtGui.QPixmap()
    pixmap.loadFromData(msg_bytes)

    display_image(pixmap, pixmap.size().width(), pixmap.size().height(), client, color)


def send_if_validate(client):
    if client.client_gui.validate():
        message = client.client_gui.msg_text.toPlainText()
        client.send_tcp(message)
        display(message, '', client.nickname, client.bg_color, client.client_gui)
        client.client_gui.msg_text.clear()


# popup window will be displayed when the client selects an image that is too large
def display_warning_window(msg):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setWindowTitle('File warning')
    msg_box.setText(msg)
    msg_box.exec_()


# if client wants to send msg using UDP he has to choose a file because UDP socket is using only to multimedia sending
# after sending we have to display our msg on chat dialog
def choose_file_and_send(client, send_method):
    file, check = QtWidgets.QFileDialog.getOpenFileNames(None, "QFileDialog.getOpenFileName()", "",
                                                         "PNG Files (*.png);;JPG Files (*.jpg);;JPEG Files (*.jpeg)")
    if check:
        # open image and get size
        image = Image.open(file[0])
        width, height = image.size
        # save img to bytes
        img_bytes = io.BytesIO()
        image.save(img_bytes, format=image.format)
        img_bytes = img_bytes.getvalue()

        # send image bytes using udp
        if len(img_bytes) >= buff_size_udp:
            display_warning_window('Nie można wysłać obrazu, ponieważ rozmiar jest za duży.')
        else:
            if send_method == 'U':  # unicast (standard method)
                client.send_udp(img_bytes)
            elif send_method == 'M':  # multicast method
                client.send_udp_multicast(img_bytes)

            # display on chat
            display('', '', client.nickname, client.bg_color, client.client_gui)
            display_image(file[0], width, height, client, client.bg_color)


class Client:
    def __init__(self):
        self.nickname = None
        self.socket_tcp = None
        self.socket_udp = None
        self.multicast_send = None
        self.multicast_receive = None
        self.quit = False
        self.threads = []
        self.client_gui = None
        self.app = None
        self.bg_color = "#%06x" % random.randint(0, 0xFFFFFF)
        self.connected = False

    def run(self):
        # 1. connect with server
        self.connect()
        self.connected = True
        print('Hello ', self.nickname)
        try:
            # 2. send client nickname from app to server
            self.send_tcp(self.nickname + '|' + self.bg_color)

            # 3. run thread to receive new messages
            self.run_thread(self.receive_udp)
            self.run_thread(self.receive_tcp)

            while not self.quit:
                self.receive_multicast_udp()

        except KeyboardInterrupt:
            self.disconnect()

        finally:
            print('Goodbye ', self.nickname)
            self.socket_tcp.close()
            self.socket_udp.close()

    # connect client with server using TCP and UDP protocol
    def connect(self):
        try:
            client_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # multicast udp sockets
            multicast_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            multicast_send.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)

            multicast_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            multicast_recv.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
            multicast_recv.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
            multicast_recv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        except socket.error as err:
            print('Failed to create a sockets: %s' % str(err))
            sys.exit()

        try:
            client_socket_tcp.connect((serverIP, serverPort))
            client_socket_udp.bind(('', client_socket_tcp.getsockname()[1]))

            # multicast binding
            multicast_recv.bind(('', multicastPort))
            host = socket.gethostbyname(socket.gethostname())
            multicast_recv.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
            multicast_recv.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
                                      socket.inet_aton(multicastIP) + socket.inet_aton(host))
        except socket.error as err:
            print('Failed to connect to %s on port %s: %s' % (serverIP, serverPort, str(err)))
            sys.exit()

        self.socket_tcp, self.socket_udp = client_socket_tcp, client_socket_udp
        self.multicast_send, self.multicast_receive = multicast_send, multicast_recv

    # disconnect client with server when client close app (close connection TCP and UDP)
    def disconnect(self):
        print('Disconnecting...')
        self.quit = True

        self.send_udp(bytes('EXIT', 'utf-8'))
        self.threads[0].join()

        self.send_tcp('EXIT')
        self.threads[1].join()

        self.send_udp_multicast(bytes('EXIT', 'utf-8'))
        self.connected = False

    # send message to server using TCP protocol
    def send_tcp(self, message):
        print('Sending TCP...')
        self.socket_tcp.send(message.encode('utf-8'))

    # send message to server using UDP protocol
    def send_udp(self, message_bytes):
        print('Sending UDP...')
        self.socket_udp.sendto(message_bytes, (serverIP, serverPort))

    # send message (file) using multicast UDP protocol
    def send_udp_multicast(self, message_bytes):
        print('Sending UDP multicast...')
        info = f'{self.nickname}|{self.bg_color}'
        self.multicast_send.sendto(info.encode('utf-8'), (multicastIP, multicastPort))
        self.multicast_send.sendto(message_bytes, (multicastIP, multicastPort))

    # receive reply from server using TCP protocol
    def receive_tcp(self):
        while not self.quit:  # can receive always if client doesn't want to exit
            buff = self.socket_tcp.recv(buff_size)

            if buff != 'EXIT'.encode('utf-8'):
                msg = buff.decode('utf-8').split('|')
                display(msg[2], msg[0], msg[1], msg[3], self.client_gui)

    # receive reply from server using UDP protocol
    def receive_udp(self):
        while not self.quit:  # can receive always if client doesn't want to exit
            info, addr = self.socket_udp.recvfrom(buff_size_udp)
            buff, addr = self.socket_udp.recvfrom(buff_size_udp)

            if info != 'EXIT'.encode('utf-8'):
                info = info.decode('utf-8').split('|')
                display('', info[0], info[1], info[2], self.client_gui)
                convert_to_img_and_display(buff, self, info[2])

    def receive_multicast_udp(self):
        # while not self.quit:
        info, addr = self.multicast_receive.recvfrom(buff_size_udp)
        buff, addr = self.multicast_receive.recvfrom(buff_size_udp)

        if buff != 'EXIT'.encode('utf-8'):
            info = info.decode('utf-8').split("|")
            if info[0] != self.nickname:
                display('Multicast msg', '', info[0], info[1], self.client_gui)
                convert_to_img_and_display(buff, self, info[1])

    def set_nickname(self, nickname):
        self.nickname = nickname

    def set_gui(self, gui_class):
        self.client_gui = gui_class

    def set_app(self, app):
        self.app = app

    # receive responses from server using new thread
    # (receive udp = first thread, receive tcp = second thread)
    def run_thread(self, target_fun):
        thr = threading.Thread(target=target_fun, args=())
        thr.daemon = True
        self.threads.append(thr)
        thr.start()

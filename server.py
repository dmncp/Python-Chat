import socket
import threading

serverIP = "127.0.0.1"
server_port = 9008
buff_size = 1024
buff_size_udp = 65507


class Server:
    def __init__(self):
        self.server_tcp = None
        self.server_udp = None
        self.threads = []
        self.client_id = 0
        self.sockets = []
        self.nicknames = []
        self.colors = []
        self.addresses = []

    # run server (main function)
    def run(self):
        # servers initialization
        self.tcp_initialization()
        self.udp_initialization()

        # run udp service - ready to receive and send messages using udp protocol
        self.run_thread(self.udp_service)

        # main server loop
        while True:
            print('Waiting for connection...')
            client, address = self.server_tcp.accept()
            print('New client connected!: ', address)

            nickname, client_color = self.receive_tcp(client).split('|')  # receive client nickname
            print('New client: (%s, %s)' % (self.client_id, nickname))

            self.sockets.append(client)
            self.nicknames.append(nickname)
            self.colors.append(client_color)
            self.addresses.append(address)

            # create new thread to communication with tcp client
            self.run_thread(self.tcp_service, client, self.client_id, address, nickname, client_color)

            self.client_id += 1

    # server initialization - TCP socket
    def tcp_initialization(self):
        server_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket_tcp.bind((serverIP, server_port))
        server_socket_tcp.listen()  # enable a server to accept connections.
        print('Python server is running - TCP...')

        self.server_tcp = server_socket_tcp

    # server initialization - UDP socket
    def udp_initialization(self):
        server_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket_udp.bind((serverIP, server_port))
        print('Python server is running - UDP...')

        self.server_udp = server_socket_udp

    # receive message from client using UDP
    def receive_udp(self):
        data, address_udp = self.server_udp.recvfrom(buff_size_udp)
        # data = data.decode('utf-8')
        client_id, client_nickname, color = self.get_client_info(address_udp)

        print(f'New UDP msg received from ({client_id, client_nickname})!: ', data)

        if data == 'EXIT'.encode('utf-8'):
            self.server_udp.sendto(bytes('EXIT', 'utf-8'), address_udp)
            self.server_udp.sendto(bytes('UDP unbind successfully', 'utf-8'), address_udp)
            return None, client_id, client_nickname, address_udp, color
        return data, client_id, client_nickname, address_udp, color

    # receive message from client using TCP
    def receive_tcp(self, client_socket, *args):
        data = client_socket.recv(buff_size).decode('utf-8')
        if args:
            print('New msg received from (%d, %s)!: ' % args, data)
        return data

    # send message to clients using TCP
    def send_tcp(self, message, sender_socket, sender_nickname, sender_id, color):
        try:
            for sock in self.sockets:
                if sock != sender_socket:
                    all_msg = f"{sender_id}|{sender_nickname}|{message}|{color}"
                    sock.send(bytes(all_msg, 'utf-8'))
        except socket.error as err:
            print('Failed to send message to client: %s' % err)

    # send message to clients using UDP
    def send_udp(self, message, sender_address, sender_nickname, sender_id, color):
        for address in self.addresses:
            if address != sender_address:
                info = f"{sender_id}|{sender_nickname}|{color}"
                self.server_udp.sendto(bytes(info, 'utf-8'), address)
                self.server_udp.sendto(message, address)

    # TCP service using by thread
    def tcp_service(self, client_socket, client_id, client_address, client_name, color):
        try:
            while True:
                received_data = self.receive_tcp(client_socket, client_id, client_name)
                if received_data == 'EXIT' or not received_data:
                    client_socket.send(bytes('EXIT', 'utf-8'))
                    return
                # send message to clients
                self.send_tcp(received_data, client_socket, client_name, client_id, color)

        except socket.error:
            print('Problem with client. Disconnecting...')
            # self.disconnect_client(client_socket, client_address, client_name, client_id, color)

        finally:
            self.disconnect_client(client_socket, client_address, client_name, client_id, color)

    # UDP service using by thread
    def udp_service(self):
        client_id = ''
        client_nickname = ''
        try:
            print('UDP connection starting\n')
            while True:
                data, client_id, client_nickname, addr_udp, color = self.receive_udp()
                if data:
                    self.send_udp(data, addr_udp, client_nickname, client_id, color)
        finally:
            print(f'UDP connection for ({client_id}, {client_nickname}) closed')

    # receive responses from server using new thread
    # (udp_service = first thread, tcp_service = second thread)
    def run_thread(self, target_fun, *args):
        if args:
            thread_args = args
        else:
            thread_args = ()

        thr = threading.Thread(target=target_fun, args=thread_args)
        thr.daemon = True
        self.threads.append(thr)
        thr.start()

    # disconnect client - remove from server 'db' (client, client_nicknames arrays)
    def disconnect_client(self, client_socket, client_address, client_name, client_id, color):
        self.sockets.remove(client_socket)
        self.addresses.remove(client_address)
        self.nicknames.remove(client_name)
        self.colors.remove(color)

        print(f"Client: ({client_id}, {client_name}) left the server")
        client_socket.close()

    # get info about client sending msg by UDP
    def get_client_info(self, address_udp):
        # get index of address_udp from clients addresses array
        address_id = self.addresses.index(address_udp)

        # find client nickname and color
        color = self.colors[address_id]
        nickname = self.nicknames[address_id]

        return address_id, nickname, color

    def stop(self):
        self.server_udp.close()
        self.server_tcp.close()


if __name__ == "__main__":
    server = Server()
    server.run()

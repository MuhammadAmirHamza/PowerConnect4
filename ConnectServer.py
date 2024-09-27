import socket


class ConnectServer:
    def __init__(self, server_hostname, server_port, game_id, color):
        self.server_hostname = server_hostname
        self.server_port = server_port
        self.game_id = game_id
        self.color = color
        self.socket = None

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_hostname, self.server_port))
            print(f"{self.color} Connected to {self.server_hostname} on port {self.server_port}")
        except Exception as e:
            print(f"{self.color} Error connecting to the server: {e}")
            return False
        return True

    def send_message(self, message):
        try:
            self.socket.sendall(f"{message}\n".encode())
            # print(f"{self.color} Sent: {message}")
            return True
        except Exception as e:
            print(f"{self.color} Error sending message: {e}")
            return False
    
    def receive_message(self):
        try:
            response = self.socket.recv(1024).decode().strip()
            # print(f"{self.color} Received: {response}")
            return True, response
        except Exception as e:
            print(f"{self.color} Error receiving message: {e}")
            return True, None

    def start_game(self):
        initial_message = f"{self.game_id} {self.color}"
        flag = self.send_message(initial_message)
        if flag:
            print(initial_message)

    def close_connection(self):
        if self.socket:
            self.socket.close()
            print("[Black] Connection closed.")

if __name__ == "__main__":
    pass
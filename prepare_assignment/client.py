from socket import *
import time
import struct
import keyboard
# CLIENT = gethostbyname(gethostname())
CLIENT = '10.100.102.12'
BROADCAST_PORT = 13117

size = 1024

class Client:
    def __init__(self, team_name):
        self.udp = socket(AF_INET, SOCK_DGRAM)
        self.udp.bind(('', BROADCAST_PORT))
        
        self.tcp = socket(AF_INET, SOCK_STREAM)
        self.team_name = team_name
    
    def search_host(self):
        
        print('Client started, listening for offer requests...')
        while True:
            message ,address = self.udp.recvfrom(size)
            print(address)
     
            data = struct.unpack('ii', message)
            password = data[0]
            port = data[1]
            print(password, port)
            if password == 95768:
                # We are about to play! let's connect to server.
                print(f"Received offer from {address[0]}, attempting to connect...")
                
                self.tcp.connect((address[0], port))
                self.tcp.send(f'{self.team_name}\n'.encode())
                self.play()
                break
           
            # time.sleep(1)
    def play(self):
        welcome_message = self.tcp.recv(size)
        print(welcome_message.decode())
        key_press = keyboard.read_key()
        self.tcp.sendall(key_press.encode())
        winner_message = self.tcp.recv(size)
        print(winner_message.decode())
            
client = Client("Rocket!")
client.search_host()
        

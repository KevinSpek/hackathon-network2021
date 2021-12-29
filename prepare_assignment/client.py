from socket import *
import time
import struct
import getch
from threading import Thread, Lock

CLIENT = gethostbyname(gethostname())
BROADCAST_PORT = 13117
size = 1024

class Client:
    def __init__(self, team_name):
        self.team_name = team_name
        
        
    def init_game(self):
                
        self.udp = socket(AF_INET, SOCK_DGRAM)
        self.udp.bind(('', BROADCAST_PORT))
        self.tcp = socket(AF_INET, SOCK_STREAM)
        self.gameover = False
    
    def search_host(self):
        self.init_game()
        print('Client started, listening for offer requests...')
        while True:
            try:
                message ,address = self.udp.recvfrom(size)
                #print(address)
        
                data = struct.unpack('ii', message)
                password = data[0]
                port = data[1]
                #print(password, port)
            except:
                continue
            if password == 95768:
                # We are about to play! let's connect to server.
                print(f"Received offer from {address[0]}, Attempting to connect...")
                
                self.tcp.connect((address[0], port))
                self.tcp.send(f'{self.team_name}\n'.encode())
                print("Connected")
                self.play()
           
            time.sleep(1)
            
    def __listen_keyboard(self):
        key_press = getch.getch()
        if not self.gameover:
            self.tcp.send(key_press.encode())
        
    def __listen_gameover(self):
        winner_message = self.tcp.recv(size)
        self.gameover = True
        print(winner_message.decode())
        
    def play(self):
        while True:  
            welcome_message = self.tcp.recv(size)
            #print(welcome_message.decode())
            if "welcome" in welcome_message.decode().lower():
                break
        print(welcome_message.decode())
        
        key_listen = Thread(target=self.__listen_keyboard)
        game_listen = Thread(target=self.__listen_gameover)
        
        key_listen.start()
        game_listen.start()
        
        
        game_listen.join()
    
        key_listen._Thread_stop()
        
        
client = Client("!")
client.search_host()
        

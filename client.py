from socket import *
import time
import struct
import getch
from threading import Thread
from getch import getch



BROADCAST_PORT = 13117
size = 1024

class GameOver:
    def __init__(self):
        self.gameover = False
    def finish(self):
        self.gameover = True
    
    def finished(self):
        return self.gameover

class Client:
    
    
    
    
    def __init__(self, team_name):
        self.team_name = team_name
        
        
    def init_game(self):
                
        self.udp = socket(AF_INET, SOCK_DGRAM)
        self.udp.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        self.udp.bind(('172.99.255.255', BROADCAST_PORT))
        self.tcp = socket(AF_INET, SOCK_STREAM)
        self.gameover = False
    
    def search_host(self):
        self.init_game()
        print('Client started, listening for offer requests...')
        while True:
            try:
                message ,address = self.udp.recvfrom(size)
                data = struct.unpack('Ibh', message)
                magic_cookie = data[0]
                magic_type = data[1]
                port = data[2]
            except:
                continue
            if magic_cookie == 0xabcddcba and magic_type == 0x2:
                # We are about to play! let's connect to server.
                print(f"Received offer from {address[0]}, Attempting to connect...")
                try:
                    self.tcp.connect((address[0], port))
                    self.tcp.send(f'{self.team_name}\n'.encode())
                    print("Connected")
                    self.play()
                    break
                except:
                    pass
                print("Failed to connect, listening for other offer requests...")
            time.sleep(1)
            
    def __listen_keyboard(self, gameover, socket):
        key_press = getch()
        
        if not gameover.finished():
            try: socket.send(key_press.encode())
            except: pass
        
    def __listen_gameover(self, gameover):
        try:
            winner_message = self.tcp.recv(size)
            gameover.finish()
            print(self.__decode(winner_message))
        except:
            print("Issue receiving message from server.")
        

    def __decode(self, string):
        st = string.decode().replace("  ", "").strip()
        return st
        
    def play(self):
        try:
            while True:
                  
                welcome_message = self.tcp.recv(size)
                #print(welcome_message.decode())
                m = self.__decode(welcome_message).lower()
                if m == '':
                    # Bad server.
                    # Searching for new one
                    self.search_host()
                    
                    
                
                
                if "welcome" in m or "quick" in m or "maths" in m or "math" in m:
                    break
                print(self.__decode(welcome_message))
                
            print(self.__decode(welcome_message))
            gameover = GameOver()
            key_listen = Thread(target=self.__listen_keyboard, args=(gameover, self.tcp))
            game_listen = Thread(target=self.__listen_gameover, args=(gameover,))
            
            key_listen.start()
            game_listen.start()
            
            
            game_listen.join()
        
            
            print("Game finished.")
            print()
            print()
        except:
            print("Something bad happened. Restarting")
        self.search_host()
        
        
client = Client("The BITles")
client.search_host()
        

from socket import *
import sys
import time
import struct

import random
from threading import Thread

GAME_PORT = 65432 # THE IP WHERE THE GAME WILL TAKE PLACE
BROADCASE_PORT = 65431 # THE IP WHERE BROADCASE IS HAPPENING
UDP_PORT = 65400
# HOST = '10.100.102.12' # THE IP OF THE SERVER MACHINE
HOST = '93.173.11.212'

# HOST = gethostbyname(gethostname())
class Server:
    def __init__(self):
        self.udp = socket(AF_INET, SOCK_DGRAM)
        self.udp.bind(('', UDP_PORT))
        self.udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        
        
        self.tcp = socket(AF_INET, SOCK_STREAM)
        self.tcp.bind(('', GAME_PORT))
        self.tcp.listen(10)

        
        self.MAX_CONNECTIONS = 1 # 2 maximum players
        self.teams = [] # teams formarted as follows: (team_socket, team_address, team_name)

    def __broadcast(self):

        
        print(f"Server started, listening on IP address {HOST}")
        password = struct.pack('ii', 95768, GAME_PORT) # this is the password the verify it came from the right server
        
        while not self.__full(): # wait for MAX_CONNECTIONS to be filled 
            
            try: self.udp.sendto(password, ('<broadcast>', BROADCASE_PORT))
            except: pass
            time.sleep(1)
                    
    def __full(self):
        self.__remove_disconnected()
        return len(self.teams) == self.MAX_CONNECTIONS 
    
    def __remove_disconnected(self):
        
        to_remove = []
        for socket, address, team_name in self.teams:
            try:
                socket.send("check".encode())
            except:
                to_remove.append((socket, address, team_name))
                
        for socket, address, team_name in to_remove:
            print(f"Team {team_name} Disconnected")
            self.teams.remove((socket, address, team_name))
                
        
    def __receive_teams(self):
        while not self.__full():
            try:
                socket, address = self.tcp.accept()
                if not self.__full():
                    team_name = socket.recv(2048).decode()
                    socket.setblocking(0)
                    print(f"Team {team_name} Connected!")
                    self.teams.append((socket, address, team_name))
            except:
                pass
    

            
    def init_game(self):
        broadcast_thread = Thread(target=self.__broadcast)
        receive_thread = Thread(target=self.__receive_teams)
        
        broadcast_thread.start()
        receive_thread.start()
        
        broadcast_thread.join()
        receive_thread.join()
        time.sleep(2)
        if self.__full():
            print("Not enough players... waiting for new players")
            self.init_game()
        else:
            self.__play()
        
    
        
        
    
    def __play(self):
        
        welcome_message = 'Welcome to Quick Maths.\n'
        welcome_message += f'Player 1: {self.teams[0][2]}\n'
        # welcome_message += f'Player 2: {self.teams[1][2]}\n'
        welcome_message += '==\n'
        welcome_message += 'Please answer the following question as fast as you can:\n'
        
        num1 = random.randint(0,4)
        num2 = random.randint(0,4)
        welcome_message += f'How much is {num1}+{num2}?'
        
        for socket, address, team_name in self.teams:
            socket.sendall(welcome_message.encode())
            answer = socket.recv(1024).decode()
            # TODO: WAIT FOR KEY RESPONSE FROM EACH TEAM!
        print(answer)
        
                
            
        
        
            
            
            
            
    

server = Server()
server.init_game()
        
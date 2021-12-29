from socket import *
import time
import struct
import select
import random
from threading import Thread

GAME_PORT = 2093 # THE IP WHERE THE GAME WILL TAKE PLACE
BROADCASE_PORT = 13117 # THE IP WHERE BROADCASE IS HAPPENING
UDP_PORT = 65339
HOST = gethostbyname(gethostname())
# HOST = '111'
magic_cookie = 0xabcddcba
magic_type = 0x2

class Server:
    def __init__(self):
        self.udp = socket(AF_INET, SOCK_DGRAM)
        self.udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.udp.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        self.udp.bind(('', UDP_PORT))
        
        
        self.tcp = socket(AF_INET, SOCK_STREAM)
        self.tcp.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        self.tcp.bind(('', GAME_PORT))
        self.tcp.listen(10)
        


        
        self.MAX_CONNECTIONS = 1 # 2 maximum players
        self.__reset_game()

    def __broadcast(self):

        
        print(f"Server started, listening on IP address {HOST}")
        password = struct.pack('Ibh', magic_cookie, magic_type, GAME_PORT) # this is the password the verify it came from the right server
        
        while not self.__full(): # wait for MAX_CONNECTIONS to be filled 
            
            try: self.udp.sendto(password, ('<broadcast>', BROADCASE_PORT))
            except: pass
            time.sleep(1)
                    
    def __full(self):
        self.__remove_disconnected()
        return len(self.team_sockets) == self.MAX_CONNECTIONS 
    
    def __remove_disconnected(self):
        
        to_remove = []
        for socket in self.team_sockets:
            try:
                socket.send("check if live".encode())
            except:
                to_remove.append(socket)
                
        for socket in to_remove:
            print(f"Team {self.get_team_name(socket)} Disconnected") # PRINT TEAM NAME
            del self.team_names[socket.getsockname()]
            self.team_sockets.remove(socket)
                
    def get_team_name(self, socket):
        return self.team_names[socket.getsockname()]
         
    
    def __receive_teams(self):
        while not self.__full():
            try:
                socket, address = self.tcp.accept()
                if not self.__full():
                    socket.setblocking(0)
                    team_name = socket.recv(2048).decode().replace("\n", "")
                    print(f"Team {team_name} Connected!")
                    self.team_names[socket.getsockname()] = team_name
                    self.team_sockets.append(socket)
            except:
                pass
    

            
    def init_game(self):
        broadcast_thread = Thread(target=self.__broadcast)
        receive_thread = Thread(target=self.__receive_teams)
        
        broadcast_thread.start()
        receive_thread.start()
        
        broadcast_thread.join()
        receive_thread.join()
        time.sleep(10)
        if not self.__full():
            print("Not enough players... waiting for new players")
            self.init_game()
        else:
            self.__play()
        
    def __reset_game(self):
        self.team_sockets = [] 
        self.team_names = {}
        
        
    
    def __play(self):
        
        welcome_message = 'Welcome to Quick Maths.\n'
        welcome_message += f'Player 1: {self.get_team_name(self.team_sockets[0])}\n'
        welcome_message += f'Player 2: {self.get_team_name(self.team_sockets[1])}\n'
        welcome_message += '=======\n'
        welcome_message += 'Please answer the following question as fast as you can:\n'
        
        num1 = random.randint(0,4)
        num2 = random.randint(0,4)
        welcome_message += f'How much is {num1}+{num2}?'
        print()
        print()
        print(welcome_message)
        flag = True 
        error = False
        for socket in self.team_sockets:
            try:
                socket.sendall(welcome_message.encode())
            except:
                error = True
        
        if not error:
            read_sockets, write_sockets, error_sockets = select.select(self.team_sockets, [], [], 10)
            for socket in read_sockets:
                answer = socket.recv(1024).decode()
                try:
                    if int(answer) == num1 + num2:
                        winner = self.get_team_name(socket)
                    else:
                        winner = self.get_team_name([sock for sock in self.team_sockets if sock != socket][0])  
                    flag = False
                    break     
                except:
                    pass
        
            
        msg = "Game over.\n\n"
        if error:
            msg += "A team has disconnected."
        elif flag:
            msg += "No winners. Draw"
        else:
            msg += f"The winner is: {winner}"
        
        
        print(msg)
        for socket in self.team_sockets:
            try:
                socket.send(msg.encode())
            except:
                pass
        print()
        print("=================================")
        print('Restarting')
        time.sleep(2)   
        self.__reset_game()
        self.init_game()
            
            
        
       

server = Server()
server.init_game()
        
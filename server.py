from socket import *
import time
import struct
import select
import random
from threading import Thread
import scapy.all as scapy

GAME_PORT = 2093 # THE IP WHERE THE GAME WILL TAKE PLACE
BROADCASE_PORT = 13117 # THE IP WHERE BROADCASE IS HAPPENING
TCP_PORT = 20000
HOST = gethostbyname(gethostname())
# HOST = scapy.get_if_addr("eth2")
# HOST = '111'
magic_cookie = 0xabcddcba
magic_type = 0x2

class Server:
    def __init__(self):
        self.udp = socket(AF_INET, SOCK_DGRAM)
        self.udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.udp.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        self.udp.bind((HOST, GAME_PORT))
        
        
        self.tcp = socket(AF_INET, SOCK_STREAM)
        self.tcp.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        self.tcp.bind((HOST, TCP_PORT))
        self.tcp.listen(10)
        


        
        self.MAX_CONNECTIONS = 2 # 2 maximum players
        self.__reset_game()

    def __broadcast(self):

        
        print(f"Server started, listening on IP address {HOST}")
        password = struct.pack('Ibh', magic_cookie, magic_type, TCP_PORT) # this is the password the verify it came from the right server
        
        while not self.__full(): # wait for MAX_CONNECTIONS to be filled 
            
            try: self.udp.sendto(password, ('172.99.255.255', BROADCASE_PORT))
            except: pass
            
            time.sleep(1)
                    
    def __full(self):
        self.__remove_disconnected()
        return len(self.team_sockets) == self.MAX_CONNECTIONS 
    
    def __remove_disconnected(self):
        
        to_remove = []
        for socket in self.team_sockets:
            try:
                pass # UNCOMMENT TO CHECK IF CLIENT IS LIVE!
                # socket.send("check if live".encode())
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
        i = 1
        for team_socket in self.team_sockets:
            welcome_message += f'Player {i}: {self.get_team_name(team_socket)}\n'
            i += 1
        welcome_message += '=======\n'
        welcome_message += 'Please answer the following question as fast as you can:\n'
        list_of_questions = ["Number of kilometers in 1.864 miles (Rounded up)",
                            "Number of plagues in Egypt",
                            "Number of apollo mission spaceflight that landed the first two men on the moon",
                            "Number of different types of hands in Poker",
                            "Number of presidents before Obama in the united states",
                            "Number of legs a black widow spider has",
                            "Number of key in old phones that featured the letters M, N and O",
                            "Number of NOT FOUND error in the internet",
                            "Number of golder starts in the EU flag"
                    
                            ]        
        answers = [3, 10, 11, 10, 43, 8, 6, 404, 12]
        fibo = [0, 1, 1, 2, 3, 5, 8]
        num1 = random.randint(3,7)
        index_question = random.randint(0,len(list_of_questions)-1)
        res = (fibo[num1-1]) * answers[index_question]  % 10
        welcome_message += f'How much is Fibonacci({num1}) TIMES the {list_of_questions[index_question]} MODULU 10?'
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
            read_sockets, write_sockets, error_sockets = select.select(self.team_sockets, [], [], 15)
            for socket in read_sockets:
                answer = socket.recv(1024).decode()
                try:
                    if int(answer) == res:
                        winner = self.get_team_name(socket)
                    else:
                        winner = self.get_team_name([sock for sock in self.team_sockets if sock != socket][0])  
                    flag = False
                    break     
                except:
                    pass
        
        print()
        print()
        msg = "Game over.\n\n"
        msg += f"The answer is {fibo[num1-1]} * {answers[index_question]} % 10 = {res} \n"

        
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
        
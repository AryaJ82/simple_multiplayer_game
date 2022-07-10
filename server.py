########################
# Author: Arya Jafari
# Description: A two way TCP connection/communication
#########################

import socket
import sys
import threading
import pickle
import pygame
from concurrent.futures import ThreadPoolExecutor
from random import randint

IP = '127.0.0.1'
PORT = 2255
clock = pygame.time.Clock()
def add_tuple(a, b):
    return a[0] + b[0], a[1] + b[1]

#number of players
NUM = 3

class Server:
    def __init__(self, NUM, IP = "127.0.0.1", PORT = 2255) -> None:
        self.NUM = NUM
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = True
    
        self.player_data = [{"pos": (randint(0, 800), randint(0, 400)), "fired":0} for i in range(NUM)]
        self.bullet_data = []

        self.cons = []
        # 0: port for player 1
        # 1: port for playe 2
        self.thrd = ThreadPoolExecutor(max_workers=NUM)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((IP, PORT))
        self.socket.listen(5)
    
    def _listen_loop(self, client):
        """
        Threaded loop that listens to <client> for packets
        """
        while self.running:
            rcv_len = 1
            response = b""
            while rcv_len:
                data = client.recv(4096)
                rcv_len = len(data)
                response += data
                if rcv_len < 4096:
                    break
            if response:
                index = self.cons.index(client)
                if response == b"exit":
                    self.cons.pop(index)
                    self.player_data.pop(index)
                    self.NUM -= 1
                    break
                else:
                    self.player_data[index] = pickle.loads(response)
        client.close()

    def fire_bullets(self, pos):
        self.bullet_data.append([add_tuple(pos, (20, 0)), (1, 0)])
        self.bullet_data.append([add_tuple(pos, (-20, 0)), (-1, 0)])
        self.bullet_data.append([add_tuple(pos, (0, 20)), (0, 1)])
        self.bullet_data.append([add_tuple(pos, (0, -20)), (0, -1)])

    def game_update(self):
        for i in range(self.NUM):
            # fire bullets if necessary
            if self.player_data[i]["fired"]:
                self.fire_bullets(self.player_data[i]["pos"])
                self.player_data[i]["fired"] = 0
        for b in self.bullet_data:
            # move bullets and delete them if out of bound
            b[0] = add_tuple(b[0], b[1])
            if abs(b[0][0] - 400) > 400 or abs(b[0][1] - 300) > 300:
                self.bullet_data.remove(b)

    def send_data(self):
        
        d = {"current": 0,
             "NUM": len(self.player_data),
             "players": list(map(lambda x: x["pos"], self.player_data)),
             "bullets": list(map(lambda x: x[0], self.bullet_data)),}
        for i in range(self.NUM):
        # send the updated data to other players
        # the sent data includes the index of the player
            d["current"] = i
            self.cons[i].send(pickle.dumps(d))

    def start(self):
        for i in range(self.NUM):
            client, address = self.socket.accept()
            print(f"Connection from {address}")
            self.cons.append(client)
            self.thrd.submit(self._listen_loop, client)

            # self.thrd[i].start()
        game = threading.Thread(target=self._run, daemon=True)
        game.start()

    def _run(self):
        try:
            while self.running:
                self.game_update()
                self.send_data()
                clock.tick(30)

        except Exception as e:
            print(e)
            self.running = False
            self.socket.close()
            sys.exit()



class ServerClient:
    def __init__(self, IP="127.0.0.1", PORT=2255) -> None:
        """ Creates a <ServerClient> object that will send console
        input to IP, PORT
        """
        self.running = True
        # TODO: bool flag the prevents the game from loading past this point
        # self.data = {"current":0, "players": [(200,300), (500,300)], "bullets":[]}
        self.data = {"running": False}
        # self.data should be a
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.connect((IP, PORT))
    
    def _receive(self):
        """
        Threaded method which recieves data from IP:PORT
        """
        while self.running:
            rcv_len = 1
            response = b""
            while rcv_len:
                data = self.socket.recv(4096)
                rcv_len = len(data)
                response += data
                if rcv_len < 4096:
                    break
            if response:
                try:
                    self.data = pickle.loads(response)
                except:
                    pass

    def handle_connection(self):
        """
        Method which implements communication between self and
        the server
        """
        rcv = threading.Thread(target=self._receive, daemon=True)
        rcv.start()
    
    def send(self, s):
        self.socket.send(pickle.dumps(s))


if __name__ == "__main__":
    try:
        NUM = int(sys.argv[1])
    except:
        pass

    server = Server(NUM)
    server.start()

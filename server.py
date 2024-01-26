import random

import socketserver
import threading

import json

BUFFERSIZE = 512

SCREENWIDTH = 640
SCREENHEIGHT = 480
BALL_DIAMETER = 20

ballpos_x=None
ballpos_y=None
ballmov_x=None
ballmov_y=None

ball_exchanges = 0

player1_pos = 0
player2_pos = 0

player1_score = 0
player2_score = 0

player1 = None
player2 = None
playing_player = 0


def spawn_ball():
    # ballpos_x, ballpos_y, ballmov_x, ballmov_y
    global ballmov_x
    global ballmov_y
    ballmov_x = 4
    ballmov_y = 4
    #ballmov_x = 0.5
    #ballmov_y = 0.5
    if bool(random.getrandbits(1)):
        ballmov_x *= -1
    if bool(random.getrandbits(1)):
        ballmov_y *= -1
    
    return SCREENWIDTH//2 - BALL_DIAMETER//2, random.randint(0, SCREENHEIGHT-BALL_DIAMETER), ballmov_x, ballmov_y


import socket
import threading
import socketserver

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        global player1
        global player2
        global player1_pos
        global player2_pos
        global player1_score
        global player2_score
        global playing_player
        global ballpos_x
        global ballpos_y
        global ballmov_x
        global ballmov_y
        global ball_exchanges
        # Echo the back to the client
        while True:
            data = self.request.recv(1024)
            #print(data)
            if not data:
                break
            data=data.decode()
            data = [e+"}" for e in data.split("}") if e]

            for d in data:
                d=json.loads(d)
                #print(d)
                if "player" in d:
                    if player1 is None:
                        ballpos_x, ballpos_y, ballmov_x, ballmov_y = spawn_ball()
                        player1=self
                        self.request.sendall(json.dumps("1").encode())
                    elif player2 is None:
                        player2=self
                        self.request.sendall(json.dumps("2").encode())
                        #players are ready
                        if ballmov_x>0:
                            playing_player=2
                        else:
                            playing_player=1
                    else:
                        self.request.sendall(json.dumps("no empty player slots").encode())
                elif "get_playing_player" in d:
                    self.request.sendall(json.dumps(str(playing_player)).encode())
                elif "set_playing_player" in d:
                    playing_player = d["set_playing_player"]
                    ball_exchanges+=1
                elif "get_ball_pos" in d:
                    self.request.sendall(json.dumps([ballpos_x, ballpos_y, ballmov_x, ballmov_y]).encode())
                elif "get_opponent_pos" in d:
                    if self == player1:
                        self.request.sendall(json.dumps(player2_pos).encode())
                    else:
                        self.request.sendall(json.dumps(player1_pos).encode())
                
                elif "set_own_position" in d:
                    if self == player1:
                        player1_pos = d["set_own_position"]
                    else:
                        player2_pos = d["set_own_position"]
                elif "set_ball_pos" in d:
                    ballpos_x, ballpos_y, ballmov_x, ballmov_y = d["set_ball_pos"]
                elif "got_goal" in d:
                    ball_exchanges=0
                    ballpos_x, ballpos_y, ballmov_x, ballmov_y = spawn_ball()
                    if ballmov_x>0:
                        playing_player=2
                    else:
                        playing_player=1
                    if self == player1:
                        player2_score+=1
                    else:
                        player1_score+=1
                    self.request.sendall(json.dumps("done").encode())
                    print(playing_player)
                elif "get_score" in d:
                    self.request.sendall(json.dumps([player1_score, player2_score]).encode())
                elif "get_ball_exchanges" in d:
                    self.request.sendall(json.dumps(ball_exchanges).encode())
                else:
                    print(f"No function {d}")
                    exit

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass



# Port 0 means to select an arbitrary unused port
HOST, PORT = "localhost", 4321

server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
with server:
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()

    server_thread.join()
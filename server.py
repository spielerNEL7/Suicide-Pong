import random
import socketserver
import threading
import json

import time

BUFFERSIZE = 512

SCREENWIDTH = 640
SCREENHEIGHT = 480
BALL_DIAMETER = 20


matches = []

class Match:
    # Initialize variables for ball position and movement
    ballpos_x = None
    ballpos_y = None
    ballmov_x = None
    ballmov_y = None

    # Initialize variables for game state
    ball_exchanges = 0
    player1_pos = 0
    player2_pos = 0
    player1_score = 0
    player2_score = 0
    player1 = None
    player2 = None
    playing_player = 0

    last_conn_player1 = None
    last_conn_player2 = None

    prev_player = 0


def spawn_ball():
    """
    Function to spawn a new ball with random position and movement direction.
    """
    global ballmov_x, ballmov_y
    #ballmov_x = 4
    #ballmov_y = 4
    ballmov_x = 0.5
    ballmov_y = 0.5
    
    if bool(random.getrandbits(1)):
        ballmov_x *= -1
    if bool(random.getrandbits(1)):
        ballmov_y *= -1
    
    return SCREENWIDTH // 2 - BALL_DIAMETER // 2, random.randint(0, SCREENHEIGHT - BALL_DIAMETER), ballmov_x, ballmov_y

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """
    Handler class to handle incoming TCP requests.
    """

    this_match = Match()

    def handle(self):
        """
        Method to handle incoming requests.
        """


        while True:
            data = self.request.recv(1024)
            if self.this_match.player1 == self:
                self.this_match.last_conn_player1 = time.time()
                if self.this_match.last_conn_player2 is not None and self.this_match.last_conn_player2 < time.time() - 1:
                    # player 2 has disconnected
                    self.end_connection()
            else:
                self.this_match.last_conn_player2 = time.time()
                if self.this_match.last_conn_player1 is not None and self.this_match.last_conn_player1 < time.time() - 1:
                    # player 2 has disconnected
                    self.end_connection()


            if not data:
                break

            data = json.loads(data.decode())

            print(f"got: {data}")



            if len(data) == 1:
                if "player" in data:
                    # Assign players based on availability
                    if len(matches) == 0 or matches[-1].player2 != None:
                        print("new match")
                        # create new match
                        self.this_match = Match()
                        matches.append(self.this_match)
                        self.this_match.ballpos_x, self.this_match.ballpos_y, self.this_match.ballmov_x, self.this_match.ballmov_y = spawn_ball()
                        self.this_match.player1 = self
                        self.request.sendall(json.dumps("1").encode())

                    else:
                        print("added player 2")
                        # add player 2 to last Match
                        self.this_match = matches[-1]
                        self.this_match.player2 = self
                        self.request.sendall(json.dumps("2").encode())
                        if self.this_match.ballmov_x > 0:
                            self.this_match.playing_player = 2
                        else:
                            self.this_match.playing_player = 1

                elif "get_playing_player" in data:
                    self.request.sendall(json.dumps(str(self.this_match.playing_player)).encode())
                
                elif "get_ball_pos" in data:
                    self.request.sendall(json.dumps([self.this_match.ballpos_x, self.this_match.ballpos_y, self.this_match.ballmov_x, self.this_match.ballmov_y]).encode())

                elif "got_goal" in data:
                    self.this_match.ball_exchanges = 0
                    self.this_match.ballpos_x, self.this_match.ballpos_y, self.this_match.ballmov_x, self.this_match.ballmov_y = spawn_ball()
                    if self.this_match.ballmov_x > 0:
                        self.this_match.playing_player = 2
                    else:
                        self.this_match.playing_player = 1
                    if self == self.this_match.player1:
                        self.this_match.player2_score += 1
                    else:
                        self.this_match.player1_score += 1
                    self.request.sendall(json.dumps("done").encode())
                    print(self.this_match.playing_player)
                
                elif "get_data" in data:
                    self.send_data()
                
                elif "own_position" in data:
                    if self == self.this_match.player1:
                        self.this_match.player1_pos = data["own_position"]
                    else:
                        self.this_match.player2_pos = data["own_position"]
                    self.send_data()
            
            else:
                if self == self.this_match.player1:
                    self.this_match.player1_pos = data["own_position"]
                else:
                    self.this_match.player2_pos = data["own_position"]

                self.this_match.playing_player = data["playing_player"]
                if self.this_match.playing_player != self.this_match.prev_player:
                    self.this_match.ball_exchanges += 1
                    self.this_match.prev_player = self.this_match.playing_player

                self.this_match.ballpos_x, self.this_match.ballpos_y, self.this_match.ballmov_x, self.this_match.ballmov_y = data["ball_pos"]
                self.send_data()




    def send_data(self):
        opponent_pos = 0
        if self == self.this_match.player1:
            opponent_pos = self.this_match.player2_pos
        else:
            opponent_pos = self.this_match.player1_pos

        print(f"send: {self.this_match.playing_player, self.this_match.ballpos_x, self.this_match.ballpos_y, self.this_match.ballmov_x, self.this_match.ballmov_y, opponent_pos, self.this_match.player1_score, self.this_match.player2_score, self.this_match.ball_exchanges}")
        self.request.sendall(json.dumps([self.this_match.playing_player, self.this_match.ballpos_x, self.this_match.ballpos_y, self.this_match.ballmov_x, self.this_match.ballmov_y, opponent_pos, self.this_match.player1_score, self.this_match.player2_score, self.this_match.ball_exchanges]).encode())


    def end_connection(self):
        self.request.sendall(json.dumps("opponent disconnected").encode())
        self.server.socket.shutdown()
        self.server.socket.close()
        self.server.server_close()
                

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    Threaded TCP Server class.
    """
    pass

# Define server host and port
HOST, PORT = "127.0.0.1", 4321

# Create a threaded TCP server
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

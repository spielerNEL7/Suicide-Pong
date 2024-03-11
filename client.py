import pygame
from pygame.locals import *
import sys
import socket
import json
import time

# Define the size of the message buffer
BUFFERSIZE = 512

# Set the server address
serverAddr = '192.168.56.1'
if len(sys.argv) == 2:
    serverAddr = sys.argv[1]

# Connect to the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((serverAddr, 4321))

# Initialize pygame
pygame.init()

# Define colors
ORANGE = (255, 140, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

SCREENWIDTH = 640
SCREENHEIGHT = 480

# Open a window
screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))

# Set window title
windowSurface = pygame.display.set_caption("Pong")
running = True

# Set screen update rate
clock = pygame.time.Clock()

# Define variables/constants
player = 0
s.sendall(json.dumps({"player": ""}).encode())
answer = json.loads(s.recv(BUFFERSIZE).decode())
if answer == "1":
    player = 1
elif answer == "2":
    player = 2
elif answer == "no empty player slots":
    print("no empty player slots")
    pygame.quit()
    exit()
else:
    print("error")
    print(answer)
    pygame.quit()
    exit()
print(f"Joined as player {str(player)}")

BALL_DIAMETER = 20

# Define functions to interact with the server

def get_playing_player():
    """
    Get the current playing player from the server.
    """
    s.sendall(json.dumps({"get_playing_player": ""}).encode())
    answer = json.loads(s.recv(BUFFERSIZE).decode())
    return int(answer)

def set_playing_player(player):
    """
    Set the current playing player on the server.
    """
    s.sendall(json.dumps({"set_playing_player": player}).encode())

def get_ball_pos():
    """
    Get the position of the ball from the server.
    """
    s.sendall(json.dumps({"get_ball_pos": ""}).encode())
    answer = json.loads(s.recv(BUFFERSIZE).decode())
    return answer

def set_ball_pos(x, y, mov_x, mov_y):
    """
    Set the position and movement of the ball on the server.
    """
    s.sendall(json.dumps({"set_ball_pos": [x, y, mov_x, mov_y]}).encode())

def get_opponent_pos():
    """
    Get the position of the opponent from the server.
    """
    s.sendall(json.dumps({"get_opponent_pos": ""}).encode())
    answer = json.loads(s.recv(BUFFERSIZE).decode())
    return int(answer)

def set_own_position(y):
    """
    Set the position of the player controlled by this client.
    """
    s.sendall(json.dumps({"set_own_position": y}).encode())

def got_goal():
    """
    Notify the server that a goal has been scored.
    """
    s.sendall(json.dumps({"got_goal": ""}).encode())
    s.recv(BUFFERSIZE).decode()

def get_score():
    """
    Get the current score from the server.
    """
    s.sendall(json.dumps({"get_score": ""}).encode())
    answer = json.loads(s.recv(BUFFERSIZE).decode())
    return answer

def get_ball_exchanges():
    """
    Get the number of ball exchanges from the server.
    """
    s.sendall(json.dumps({"get_ball_exchanges": ""}).encode())
    answer = json.loads(s.recv(BUFFERSIZE).decode())
    return int(answer)

# Initialize player positions and scores
player1_x = 20
player1_y = 20
player1_mov = 0
player1_score = 0

player2_x = SCREENWIDTH - (2 * 20)
player2_y = 20
player2_mov = 0
player2_score = 0

full_racket_height = 220

racket_height = full_racket_height

playing_player = 0

ball_exchanges = 0

ball_speed = 1

# Wait for both players to join before starting the game
while get_playing_player() == 0:
    print("waiting for other player")
    time.sleep(0.1)

# Get playing player and initial ball position from the server
playing_player = get_playing_player()
ballpos_x, ballpos_y, ballmov_x, ballmov_y = get_ball_pos()

# Main game loop
while running:

    # Check for user input events
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        if event.type == pygame.KEYDOWN:

            # Handle player movement keys
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                if player == 1:
                    player1_mov = -6
                elif player == 2:
                    player2_mov = -6
                else:
                    exit()
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                if player == 1:
                    player1_mov = 6
                elif player == 2:
                    player2_mov = 6
                else:
                    exit()

        # Stop player movement
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN or event.key == pygame.K_w or event.key == pygame.K_s:
                if player == 1:
                    player1_mov = 0
                elif player == 2:
                    player2_mov = 0
                else:
                    exit()

    # Update player positions
    if player == 1:
        if player1_mov != 0:
            player1_y += player1_mov
        if player1_y < 0:
            player1_y = 0
        if player1_y > SCREENHEIGHT - racket_height:
            player1_y = SCREENHEIGHT - racket_height
        set_own_position(player1_y)
        player2_y = get_opponent_pos()

    elif player == 2:
        if player2_mov != 0:
            player2_y += player2_mov
        if player2_y < 0:
            player2_y = 0
        if player2_y > SCREENHEIGHT - racket_height:
            player2_y = SCREENHEIGHT - racket_height
        set_own_position(player2_y)
        player1_y = get_opponent_pos()

    # Clear the screen
    screen.fill(BLACK)

    # Draw game objects
    ball = pygame.draw.ellipse(screen, WHITE, [ballpos_x, ballpos_y, BALL_DIAMETER, BALL_DIAMETER])
    player1 = pygame.draw.rect(screen, WHITE, [player1_x, player1_y, 20, racket_height])
    player2 = pygame.draw.rect(screen, WHITE, [player2_x, player2_y, 20, racket_height])

    # Handle ball movement and collisions
    if playing_player != player:
        playing_player = get_playing_player()
        ballpos_x, ballpos_y, ballmov_x, ballmov_y = get_ball_pos()
        ball_exchanges = get_ball_exchanges()
        racket_height = full_racket_height - ball_exchanges *10
        ball_speed = 1 + (ball_exchanges * 0.002)

        if racket_height < 10:
            racket_height = 10
        racket_height = full_racket_height - ball_exchanges * 5
        
    else:
        ballpos_x += ballmov_x
        ballpos_y += ballmov_y

        if ballpos_y > SCREENHEIGHT - BALL_DIAMETER or ballpos_y < 0:
            ballmov_y = ballmov_y * - ball_speed
        

        if ballpos_x < 0 or ballpos_x > SCREENWIDTH - BALL_DIAMETER:
            print("got goal")
            playing_player = 0
            got_goal()

            continue

        if player == 1:
            if player1.colliderect(ball) and ballmov_x < 0:
                ballmov_x = ballmov_x * - ball_speed
                set_ball_pos(ballpos_x, ballpos_y, ballmov_x, ballmov_y)
                playing_player = 2
                set_playing_player(2)
                ball_exchanges += 1

        elif player == 2:
            if player2.colliderect(ball) and ballmov_x > 0:
                ballmov_x = ballmov_x * - ball_speed
                set_ball_pos(ballpos_x, ballpos_y, ballmov_x, ballmov_y)
                playing_player = 1
                set_playing_player(1)
                ball_exchanges += 1
        
        set_ball_pos(ballpos_x, ballpos_y, ballmov_x, ballmov_y)

    # Display scores
    player1_score, player2_score = get_score()
    font = pygame.font.SysFont(None, 70)

    text1 = font.render(str(player1_score), True, RED)
    screen.blit(text1, [100, 10])

    text2 = font.render(str(player2_score), True, RED)
    screen.blit(text2, [SCREENWIDTH - 125, 10])

    # Update the window
    pygame.display.flip()

    # Set frame rate
    clock.tick(60)

# Quit pygame
pygame.quit()

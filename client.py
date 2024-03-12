import pygame
from pygame.locals import *
import sys
import socket
import json

import asyncio

# Define the size of the message buffer
BUFFERSIZE = 512

# Set the server address
serverAddr = '192.168.200.139'
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
    print(answer)
    return int(answer)


def get_ball_pos():
    """
    Get the position of the ball from the server.
    """
    s.sendall(json.dumps({"get_ball_pos": ""}).encode())
    answer = json.loads(s.recv(BUFFERSIZE).decode())
    return answer


def got_goal():
    """
    Notify the server that a goal has been scored.
    """
    s.sendall(json.dumps({"got_goal": ""}).encode())
    print(f"goal: {s.recv(BUFFERSIZE).decode()}")


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
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            s.sendall(json.dumps({"close_conn": ""}).encode())
            s.shutdown(0)
            s.close()
            exit()
        screen.fill(BLACK)
        font = pygame.font.SysFont(None, 70)

        text = font.render("waiting for other player", True, RED)
        screen.blit(text, [100, 10])
        pygame.display.flip()

        clock.tick(60)

# Get playing player and initial ball position from the server
playing_player = get_playing_player()
ballpos_x, ballpos_y, ballmov_x, ballmov_y = get_ball_pos()


playingplayer_changed = False


opponent_pos = 0


loop = asyncio.get_event_loop()

won = False


async def get_data():
    data = json.loads(s.recv(BUFFERSIZE).decode())
    print(f"data: {data}")
    if data == "opponent disconnected":
        print("You won")


        global won
        won = True
        return
    
    global playing_player, ballpos_x, ballpos_y, ballmov_x, ballmov_y, opponent_pos, player1_score, player2_score, ball_exchanges

    
    playing_player, ballpos_x, ballpos_y, ballmov_x, ballmov_y, opponent_pos, player1_score, player2_score, ball_exchanges = data



def send_data():
    if player == 1:
        player_pos = player1_y
    else:
        player_pos = player2_y

    if playing_player == player:
        a = json.dumps({"playing_player": playing_player, "ball_pos": [ballpos_x, ballpos_y, ballmov_x, ballmov_y], "own_position": player_pos})
        print(f"send: {a}")
        s.sendall(json.dumps({"playing_player": playing_player, "ball_pos": [ballpos_x, ballpos_y, ballmov_x, ballmov_y], "own_position": player_pos}).encode())
    
    elif playingplayer_changed:
        a = json.dumps({"playing_player": playing_player, "ball_pos": [ballpos_x, ballpos_y, ballmov_x, ballmov_y], "own_position": player_pos})
        print(f"send: {a}")
        s.sendall(json.dumps({"playing_player": playing_player, "ball_pos": [ballpos_x, ballpos_y, ballmov_x, ballmov_y], "own_position": player_pos}).encode())

    else:
        a = json.dumps({"own_position": player_pos})
        print(f"send: {a}")
        s.sendall(json.dumps({"own_position": player_pos}).encode())


send_data()

def run_once(loop):
    loop.call_soon(loop.stop)
    loop.run_forever()

# Main game loop
while running:

    if won:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        screen.fill(BLACK)
        font = pygame.font.SysFont(None, 70)

        text = font.render("You Won!", True, RED)
        screen.blit(text, [100, 10])
        pygame.display.flip()

        clock.tick(60)
        continue
    

    loop.create_task(get_data())


    run_once(loop)

    if playingplayer_changed:
        if playing_player != player:
            playingplayer_changed = False

    if player == 1:
        player2_y = opponent_pos
    else:
        player1_y = opponent_pos

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

    elif player == 2:
        if player2_mov != 0:
            player2_y += player2_mov
        if player2_y < 0:
            player2_y = 0
        if player2_y > SCREENHEIGHT - racket_height:
            player2_y = SCREENHEIGHT - racket_height

    # Clear the screen
    screen.fill(BLACK)

    # Draw game objects
    ball = pygame.draw.ellipse(screen, WHITE, [ballpos_x, ballpos_y, BALL_DIAMETER, BALL_DIAMETER])
    player1 = pygame.draw.rect(screen, WHITE, [player1_x, player1_y, 20, racket_height])
    player2 = pygame.draw.rect(screen, WHITE, [player2_x, player2_y, 20, racket_height])

    # Handle ball movement and collisions
    if playing_player != player:

        racket_height = full_racket_height - ball_exchanges *10

        if racket_height < 10:
            racket_height = 10

        
    else:
        ball_speed = 1 + (ball_exchanges * 0.01)
        ballpos_x += ballmov_x * ball_speed
        ballpos_y += ballmov_y * ball_speed

        if ballpos_y > SCREENHEIGHT - BALL_DIAMETER or ballpos_y < 0:
            ballmov_y = ballmov_y * -1
        

        if ballpos_x < 0 or ballpos_x > SCREENWIDTH - BALL_DIAMETER:
            print("got goal")
            print(ballpos_x)
            playing_player = 0
            got_goal()
            s.sendall(json.dumps({"get_data": ""}).encode())
            continue

        if player == 1:
            if player1.colliderect(ball) and ballmov_x < 0:
                ballmov_x = ballmov_x * -1
                playing_player = 2
                playingplayer_changed = True
                ball_exchanges += 1

        elif player == 2:
            if player2.colliderect(ball) and ballmov_x > 0:
                ballmov_x = ballmov_x * -1
                playing_player = 1
                playingplayer_changed = True
                ball_exchanges += 1
        

    # Display scores
    font = pygame.font.SysFont(None, 70)

    text1 = font.render(str(player1_score), True, RED)
    screen.blit(text1, [100, 10])

    text2 = font.render(str(player2_score), True, RED)
    screen.blit(text2, [SCREENWIDTH - 125, 10])

    # Update the window

    pygame.display.flip()

    try:
        send_data()
    except Exception as ex:
        if won:
            pass
        else:
            raise ex
    # Set frame rate
    clock.tick(60)

# Quit pygame
pygame.quit()

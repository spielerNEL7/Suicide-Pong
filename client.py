import pygame
from pygame.locals import *
import sys
import socket

import json
import time


BUFFERSIZE = 512

serverAddr = '127.0.0.1'
if len(sys.argv) == 2:
  serverAddr = sys.argv[1]
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((serverAddr, 4321))


# initialisieren von pygame
pygame.init()

# genutzte Farbe
ORANGE  = ( 255, 140, 0)
RED     = ( 255, 0, 0)
GREEN   = ( 0, 255, 0)
BLACK = ( 0, 0, 0)
WHITE   = ( 255, 255, 255)

SCREENWIDTH = 640
SCREENHEIGHT = 480

# Fenster öffnen
screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))

# Titel für Fensterkopf
windowSurface = pygame.display.set_caption("Unser erstes Pygame-Spiel")
running = True

# Bildschirm Aktualisierungen einstellen
clock = pygame.time.Clock()

# Definieren der Variablen/Konstanten
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
print(f"Joind as player {str(player)}")


BALL_DIAMETER = 20


def get_playing_player():
    s.sendall(json.dumps({"get_playing_player": ""}).encode())
    answer = json.loads(s.recv(BUFFERSIZE).decode())
    return int(answer)

def set_playing_player(player):
    s.sendall(json.dumps({"set_playing_player": player}).encode())


def get_ball_pos():
    s.sendall(json.dumps({"get_ball_pos": ""}).encode())
    answer = json.loads(s.recv(BUFFERSIZE).decode())
    return answer

def set_ball_pos(x, y, mov_x, mov_y):
    s.sendall(json.dumps({"set_ball_pos": [x, y, mov_x, mov_y]}).encode())

def get_opponent_pos():#TODO
    s.sendall(json.dumps({"get_opponent_pos": ""}).encode())
    answer = json.loads(s.recv(BUFFERSIZE).decode())
    return int(answer)

def set_own_position(y):#TODO
    s.sendall(json.dumps({"set_own_position": y}).encode())

def got_goal():
    s.sendall(json.dumps({"got_goal": ""}).encode())
    s.recv(BUFFERSIZE).decode()

def get_score():
    s.sendall(json.dumps({"get_score": ""}).encode())
    answer = json.loads(s.recv(BUFFERSIZE).decode())
    return answer

def get_ball_exchanges():
    s.sendall(json.dumps({"get_ball_exchanges": ""}).encode())
    answer = json.loads(s.recv(BUFFERSIZE).decode())
    return int(answer)


player1_x = 20
player1_y = 20
player1_mov = 0
player1_score = 0

player2_x = SCREENWIDTH - (2 * 20)
player2_y = 20
player2_mov = 0
player2_score = 0

full_racket_height = 220

racket_height=full_racket_height

playing_player=0

ball_exchanges = 0

while get_playing_player() == 0:
    print("waiting for other player")
    time.sleep(0.1)

playing_player = get_playing_player()

ballpos_x, ballpos_y, ballmov_x, ballmov_y = get_ball_pos()

# Schleife Hauptprogramm
while running:


    # Überprüfen, ob Nutzer eine Aktion durchgeführt hat
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        if event.type == pygame.KEYDOWN:

            # Taste für Spieler 1
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                if player==1:
                    player1_mov = -6
                elif player==2:
                    player2_mov = -6
                else:
                    exit()
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                if player==1:
                    player1_mov = 6
                elif player==2:
                    player2_mov = 6
                else:
                    exit()


        # zum Stoppen der Spielerbewegung
        if event.type == pygame.KEYUP:

            # Tasten für Spieler 1
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN or event.key == pygame.K_w or event.key == pygame.K_s:
                if player==1:
                    player1_mov = 0
                elif player==2:
                    player2_mov = 0
                else:
                    exit()


    # Spiellogik
    
    if player==1:
        if player1_mov != 0:
            player1_y += player1_mov

        if player1_y < 0:
            player1_y = 0

        if player1_y > SCREENHEIGHT - racket_height:
            player1_y = SCREENHEIGHT - racket_height
        
        set_own_position(player1_y)
        player2_y = get_opponent_pos()

    elif player==2:
        if player2_mov != 0:
            player2_y += player2_mov

        if player2_y < 0:
            player2_y = 0

        if player2_y > SCREENHEIGHT - racket_height:
            player2_y = SCREENHEIGHT - racket_height

        set_own_position(player2_y)
        player1_y = get_opponent_pos()


    # Spielfeld löschen
    screen.fill(BLACK)

    # Spielfeld/figuren zeichnen
    # -- Ball
    ball = pygame.draw.ellipse(screen, WHITE, [ballpos_x, ballpos_y, BALL_DIAMETER, BALL_DIAMETER])

    # -- Spielerfigur 1
    player1 = pygame.draw.rect(screen, WHITE, [player1_x, player1_y, 20, racket_height])
    # -- Spielerfigur 2
    player2 = pygame.draw.rect(screen, WHITE, [player2_x, player2_y, 20, racket_height])


    if playing_player != player:
        playing_player = get_playing_player()
        ballpos_x, ballpos_y, ballmov_x, ballmov_y = get_ball_pos()
        ball_exchanges = get_ball_exchanges()
        racket_height = full_racket_height - ball_exchanges *5
        
        
    else:
    # bewegen unseres Balls/Kreises
        ballpos_x += ballmov_x
        ballpos_y += ballmov_y

        if ballpos_y > SCREENHEIGHT - BALL_DIAMETER or ballpos_y < 0:
            ballmov_y = ballmov_y * -1
        

        if ballpos_x < 0 or ballpos_x > SCREENWIDTH - BALL_DIAMETER:
            print("got goal")
            playing_player=0
            got_goal()
            continue


        if player==1:
            if player1.colliderect(ball) and ballmov_x < 0:
                ballmov_x = ballmov_x * -1
                set_ball_pos(ballpos_x, ballpos_y, ballmov_x, ballmov_y)
                playing_player=2
                set_playing_player(2)
                ball_exchanges += 1
                #racket_height -= 5

        elif player==2:
            if player2.colliderect(ball) and ballmov_x > 0:
                ballmov_x = ballmov_x * -1
                set_ball_pos(ballpos_x, ballpos_y, ballmov_x, ballmov_y)
                playing_player=1
                set_playing_player(1)
                ball_exchanges += 1
                #racket_height -= 5
        
        set_ball_pos(ballpos_x, ballpos_y, ballmov_x, ballmov_y)

    '''ausgabetext = "Ballwechsel: " + str(ballwechsel)
    font = pygame.font.SysFont(None, 70)
    text = font.render(ausgabetext, True, RED)
    screen.blit(text, [100, 10])'''

    player1_score, player2_score = get_score()

    ausgabetext = str(player1_score)
    font = pygame.font.SysFont(None, 70)
    text = font.render(ausgabetext, True, RED)
    screen.blit(text, [55, 10])

    ausgabetext = str(player2_score)
    font = pygame.font.SysFont(None, 70)
    text = font.render(ausgabetext, True, RED)
    screen.blit(text, [SCREENWIDTH - 80, 10])

    # Fenster aktualisieren
    pygame.display.flip()

    # Refresh-Zeiten festlegen
    clock.tick(60)

pygame.quit()
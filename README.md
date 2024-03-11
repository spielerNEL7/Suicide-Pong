# Suicide-Pong
# README.md

## Multiplayer Pong Game

This repository contains a simple multiplayer Pong game implemented in Python using the Pygame library for graphics and Socket programming for network communication. The game allows two players to compete against each other over a network connection.

### Requirements

Before running the game, make sure you have the following requirements installed on your system:

- **Python 3.x**: The game is written in Python 3, so you need Python 3 installed on your machine. You can download and install Python 3 from the [official Python website](https://www.python.org/).

- **Pygame**: Pygame is a set of Python modules designed for writing video games. It provides functionalities for handling graphics, sound, and user input. You can install Pygame using pip:
    ```
    pip install pygame
    ```
### Installation

To get started with the game, follow these installation steps:

1. Clone the repository to your local machine using the following command:
    ```
    git clone https://github.com/spielerNEL7/Suicide-Pong.git
    ```

2. Navigate to the directory where you cloned the repository.

3. Install the required dependencies mentioned above.

### Usage

Once you have installed the necessary dependencies, you can run the game by following these steps:

1. Make sure that the correct server IP address is specified in both files (**`client.py`** and **`server.py`**). It is the IP address of the machine on which the server is started. 

2. Open two terminal windows or command prompts.

3. In one terminal, navigate to the repository directory and run the server script:
    ```
    python server.py
    ```

4. In the other terminal, navigate to the repository directory and run the client script:
    ```
    python client.py
    ```

5. As soon as the server has been started successfully and both players are connected, the game starts.

### Program Structure

The repository consists of the following files:

- **`client.py`**: This file contains the code for the client-side of the game. It handles user input, displays the game graphics using Pygame, and communicates with the server for multiplayer functionality.

- **`server.py`**: This file contains the code for the server-side of the game. It manages the game state, handles communication between multiple clients, and coordinates gameplay.

### Gameplay

- The game starts once two players are connected to the server.

- Both players can either use the UP and DOWN arrow keys or the W and S keys to control their bars.

- The objective of the game is to hit the ball with your bar in such a way that the opponent misses it.

- Each time a player misses the ball, the opposing player scores a point.

- Each time the ball is successfully defended by a player, the bars of both players are reduced in size. This continues until the minimum size has been reached or one of the two players scores a point. The bar size is then reset. With each defense the ballspeed also increases slightly.

### Acknowledgments

This game was created as a project for learning network programming concepts and Pygame. It is inspired by the classic game of Pong.

### Disclaimer

This game is a simple demonstration and may not have advanced features or error handling. It is intended for educational purposes only. Feel free to modify and enhance the game as per your requirements!

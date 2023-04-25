# Fault-Tolerant Agario Game
## CS262 Final Project: Elena Horton and Jerry Yang

## Overview
This repository contains code that creates an n-fault tolerant, multiplayer version of the popular game agar.io in Python. 

## Installation
To set up your environment to run our code:
1) Run `pip install -r requirements.txt` from this folder. 
2) Edit the `config.py` file to add your desired IP address and port number
3) Follow the usage instructions to play the game.

## Structure of this project
All of the code needed to run this game is included in this top folder. the `proto` file contains the definitions of the grpc functions used by both the client and server code, and the `tests` file contains our test code.

The `model.py` file contains all of the functions necessary for maintaining the game logic. It is directly accessed by the `run_game_server.py` code, which acts as the primary server and is replicable with n-1 fault tolerance, where n is the number of game server instances. The `run_view_server.py` module is the lead server that simply maintains a list of active game servers and directs clients to the current leader. `config.py` contains necessary definitions, and should be modified to include the correct server IP addresses. `client.py` contains the client code-- it is what a player must run to play the game. It is responsible for receiving the game state from the game servers and rendering it appropriately to the user. Finally, `replication.py` contains the logic for handling replication amongst the game servers-- the view server access this module directly to determine which server is the leader and which servers are available as backups. If the lead server goes down, it adjusts this accordingly and initiates a client reconnect to the next lead server. 

## Usage
To run the servers, first start the view server with `python3 run_view_server.py`. Then run as many game servers as you'd like with `python run_game_server.py x` where `x` is the game server's number (i.e. 1 for the first one, 2 for the second one, etc.). 

To start the client, ensure that the connection details are correct in the `config.py` file and simply run `python3 client.py [username]` where `username` is your chosen username. To exit the program, simply exit the window. 

## Testing

## Limitations
While this system is n-fault tolerant based on the number of game servers present, it will not survive if the view server crashes. This was a design decision we made based on the 24/7 nature of the game-- it is more important for the complex game logic to be backed up amongst several servers than to protect against the simple operations of the view server going down. Future work would be to extend replication to the view server. 

## Engineering Notebook
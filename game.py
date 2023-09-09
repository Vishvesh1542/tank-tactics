import json
import numpy as np
import random

class Player:
    def __init__(self, user_class) -> None:
        self.user_class = user_class
        self.block_number = 1
        self.x_pos = 0
        self.y_pos = 0

class Game:
    def __init__(self, players: list | tuple) -> None:
        self.players = players

        if len(players) < 10:
            self.grid = np.zeros((10, 10))
        else:
            self.grid = np.zeros((25, 25))
        self._generate_start_positions(players)
    
    # Generates where the players starts at the start of game
    def _generate_start_positions(self, players: list) -> None:
        random.shuffle(players)
        
        # Define the starting positions for each number of players
        starting_positions = {
            1: [(5, 5)],
            2: [(1, 5), (8, 5)],
            3: [(4, 2), (1, 5), (7, 5)],
            4: [(1, 1), (8, 1), (1, 8), (8, 8)],
            5: [(4, 1), (2, 3), (6, 3), (2, 7), (6, 7)],
            6: [(3, 1), (6, 1), (3, 4), (6, 4), (3, 7), (6, 7)],
            7: [(3, 0), (6, 0), (3, 3), (6, 3), (3, 6), (6, 6), (3, 9)],
            8: [(3, 0), (6, 0), (3, 3), (6, 3), (3, 6), (6, 6), (3, 9), (6, 9)]
        }

        index = 0
        no_ = len(players)
        for player in players:
            x, y = starting_positions[no_][index]
            player.x_pos = x
            player.y_pos = y

            self.grid[y, x] = player.block_number

            index += 1
    
    def update(self) -> None:
        self.grid = np.zeros((10, 10))
        for player in self.players:
            self.grid[player.y_pos, player.x_pos] = player.block_number
        
    def move(self, direction: tuple, player: Player):
        player_x = player.x_pos
        player_y = player.y_pos
        
        if direction[0] > 0:
            if player_x < 9:
                player_x += 1
            else:
                return 'Player is already on edge!'
        elif direction[0] < 0:
            if player_x > 1:
                player_x -= 1
            else:
                return 'Player is already on edge!'
                
        if direction[1] > 0:
            if player_y < 9:
                player_y += 1
            else:
                return 'Player is already on edge!'
        elif direction[1] < 0:
            if player_y > 1:
                player_y -= 1
            else:
                return 'Player is already on edge!'
        
        self.update()
        return 'Successfully moved!'
            
 
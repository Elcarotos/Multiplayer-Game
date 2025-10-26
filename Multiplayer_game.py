import pygame
import random
import math
from pygame.locals import *
from sys import exit

# Settings
case_x, case_y = 30, 23
size_x, size_y = 32, 32
sword_width = 8
filepath = "maps/map_06.txt"
size_bush = 2 # Taille des buissons
p_decoration = [0, 0, 1] # Probabilité d'une décoration, 1/3 ici
duree_party = 20 # in seconds

# Init pygame
pygame.init()
screen = pygame.display.set_mode((case_x*size_x, case_y*size_y), pygame.SCALED)
clock = pygame.time.Clock()
# Text settings
FONT = "E:/Ressources/Police_write/MinecraftStandard.otf"
FONT_LITTLE = pygame.font.Font(FONT, 12)
FONT_BIG = pygame.font.Font(FONT, 17)

TAILLE_CRUSEUR = 10
ESPACE_LINES = 45

BLACK = [0, 0, 0] # Background of the text
WHITE = [250, 250, 250] # Abled text of the game
GREY = [120, 120, 120] # Disabled text of the game
# Init joystick
pygame.joystick.init()
nb_players = pygame.joystick.get_count() # Nombre de joystick donc de joueurs
print("Joueurs :", nb_players) # Nombre de joystick(s) trouvés

# List
COLORS = ["PURPLE", "GREEN", "BLUE", "YELLOW"]
MAP = []
tiles = []
spawners = []
players = []

# Class of the game
class Game():
    def __init__(self, state):
        self.init_players_game()
        self.set_state(state)
        
    def set_state(self, state):
        self.state = state
        if self.state == "menu":
            self.init_players_menu()
        if self.state == "settings":
            self.init_players_settings()
        if self.state == "party":
            self.counter = duree_party
            self.timer = pygame.time.set_timer(pygame.USEREVENT, 1000)
            self.init_map()
            self.init_players_party()
        if self.state == "end":
            self.init_players_end()

    # Init player for game
    def init_players_game(self):
        for controller in range(nb_players):
            players.append(Player(pygame.joystick.Joystick(controller)))
            players[-1].controller.init()


    # Init players for menu
    def create_selecters_menu(self):
        for player in players:
            player.set_selecter(Selecter([0, 1], 0))

            
    # Init menu
    def init_players_menu(self):
        self.create_selecters_menu()
        
    # Affichage menu
    def affichage_title(self):
        x_text, y_text = 305, 100
        text = "Welcome to you travelers"
        screen.blit(FONT_BIG.render(text, True, WHITE), (x_text, y_text))
        
    def affichage_new_game_menu(self):
        x_text, y_text = 365, 300
        text = "Select this for NEW GAME"
        screen.blit(FONT_LITTLE.render(text, True, WHITE), (x_text, y_text))
        
    def affichage_quit_menu(self):
        x_text, y_text = 385, 340
        text = "Select this for QUIT"
        screen.blit(FONT_LITTLE.render(text, True, WHITE), (x_text, y_text))
        
    def affichage_vote_menu(self):
        x_text, y_text = 300, 300
        for line in players[-1].selecter.states:
            nb_vote = len([player for player in players if player.selecter.valeur == line])
            if nb_vote != 0:
                text = "(" + str(nb_vote) + "/" + str(nb_players) + ")"
                screen.blit(FONT_LITTLE.render(text, True, WHITE), (x_text, y_text+40*line))
                
    def affichage_selecters_lines_menu(self):
        for player in players:
            if player.selecter.position <= 1:
                x_text = 700 
                y_text = 300 + ESPACE_LINES*player.selecter.position - TAILLE_CRUSEUR
                text = "<"
                screen.blit(FONT_BIG.render(text, True, player.selecter.color), (x_text, y_text))
                
    # Update menu
    def choice_lines_menu(self):
        choice = []
        for player in players:
            choice.append(player.selecter.valeur)
        if choice.count(0) >= math.floor(nb_players/2+1):
            self.set_state("settings")
        if choice.count(1) >= math.floor(nb_players/2+1):
            destroy()
            
    # Maj menu
    def affichage_menu(self):
        screen.fill(BLACK)
        self.affichage_title()
        self.affichage_new_game_menu()
        self.affichage_quit_menu()
        self.affichage_vote_menu()
        self.affichage_selecters_lines_menu()
        
    def controller_menu(self, player):
        y_axis = player.controller.get_axis(1)
        if abs(y_axis) > 0.5 and not player.selecter.cooldown_y:
            [player.selecter.move(y_axis) for player in players]
            player.selecter.set_cooldown_y(True)
        if abs(y_axis) < 0.5 and player.selecter.cooldown_y:
            player.selecter.set_cooldown_y(False)
            
        if player.controller.get_button(0) and not player.option_cooldown:
            if player.selecter.position == 0:
                player.selecter.set_valeur(0)
            if player.selecter.position == 1:
                player.selecter.set_valeur(1)
            player.set_option_cooldown(True)
        elif not player.controller.get_button(0) and player.option_cooldown:
            player.set_option_cooldown(False)
            
    def update_menu(self):
        self.choice_lines_menu()


    # Init players for settings
    def create_selecters_settings(self):
        for player in players:
            player.set_selecter(Selecter([[0, 1], [0, 1, 2, 3]], [0, 0]))
            
    def create_selecters_color_settings(self):
        for player in players:
            if player.color != None:
                player.selecter.set_color(player.color)
                
    # Init settings
    def init_players_settings(self):
        self.create_selecters_settings()
        self.create_selecters_color_settings()
        
    # Affichage menu
    def affichage_consign(self):
        x_text, y_text = 50, 50
        text = "Set your party :"
        screen.blit(FONT_BIG.render(text, True, WHITE), (x_text, y_text))
        
    def affichage_launch_party(self):
        x_text, y_text = 550, 600
        text = "Select this for LAUNCH PARTY"
        if len([player.color for player in players if player.color != None]) == nb_players:
            COLOR = WHITE
        else:
            COLOR = GREY
        screen.blit(FONT_LITTLE.render(text, True, COLOR), (x_text, y_text))
        
    def affichage_return_menu(self):
        x_text, y_text = 550, 640
        text = "Select this for RETURN MENU"
        screen.blit(FONT_LITTLE.render(text, True, WHITE), (x_text, y_text))
        
    def affichage_colors_settings(self):
        x_color = 64
        y_color = -32
        for color in COLORS:
            y_color += 136
            pygame.draw.rect(screen, color, (x_color, y_color, 32, 32))
            
    def affichage_vote_settings(self):
        x_text, y_text = 480, 600
        votes = [player for player in players if player.selecter.valeur != None]
        votes = [player.selecter.valeur[1] for player in votes if player.selecter.valeur[0] == 0]
        if votes.count(0) != 0 and len([player for player in players if player.color != None]) == nb_players:
            text = "(" + str(votes.count(0)) + "/" + str(nb_players) + ")"
            screen.blit(FONT_LITTLE.render(text, True, WHITE), (x_text, y_text))
        if votes.count(1) != 0:
            text = "(" + str(votes.count(1)) + "/" + str(nb_players) + ")"
            screen.blit(FONT_LITTLE.render(text, True, WHITE), (x_text, y_text+40))
            
    def affichage_selecters_colors_settings(self):
        for player in players:
            if player.selecter.position[0] == 1:
                x_text = 96 + 20*players.index(player)+1
                y_text = 104 + 136*player.selecter.position[1]
                text = "<"
                screen.blit(FONT_BIG.render(text, True, player.selecter.color), (x_text, y_text))
                
    def affichage_selecters_lines_settings(self):
        for player in players:
            if player.selecter.position[0] == 0:
                x_text = 840 + 20*players.index(player)+1
                y_text = 600 + ESPACE_LINES*player.selecter.position[1] - TAILLE_CRUSEUR
                text = "<"
                screen.blit(FONT_BIG.render(text, True, player.selecter.color), (x_text, y_text))
                
    # Update settings
    def choice_colors_settings(self):
        for player in players:
            if player.selecter.valeur == [1, 0] and [player.color for player in players].count("PURPLE") == 0:
                player.selecter.set_color("PURPLE")
                player.set_color("PURPLE")
            if player.selecter.valeur == [1, 1] and [player.color for player in players].count("GREEN") == 0:
                player.selecter.set_color("GREEN") 
                player.set_color("GREEN")
            if player.selecter.valeur == [1, 2] and [player.color for player in players].count("BLUE") == 0:
                player.selecter.set_color("BLUE") 
                player.set_color("BLUE")
            if player.selecter.valeur == [1, 3] and [player.color for player in players].count("YELLOW") == 0:
                player.selecter.set_color("YELLOW") 
                player.set_color("YELLOW")
                
    def choice_lines_settings(self):
        choice = []
        for player in players:
            choice.append(player.selecter.valeur)
        if choice.count([0, 0]) >= math.floor(nb_players/2+1) and len([player.color for player in players if player.color != None]) == nb_players:
            self.set_state("party")
        if choice.count([0, 1]) >= math.floor(nb_players/2+1):
            self.reset_colors()
            self.set_state("menu")
            
    def reset_colors(self):
        for player in players:
            player.set_color(None)
            
    # Maj settings           
    def affichage_settings(self):
        screen.fill(BLACK)
        self.affichage_consign()
        self.affichage_launch_party()
        self.affichage_return_menu()
        self.affichage_colors_settings()
        self.affichage_vote_settings()
        self.affichage_selecters_colors_settings()
        self.affichage_selecters_lines_settings()
        
    def controller_settings(self, player):
        x_axis = player.controller.get_axis(0)
        y_axis = player.controller.get_axis(1)
        if abs(x_axis) > 0.5 and not player.selecter.cooldown_x:
            player.selecter.move_x(x_axis)
            player.selecter.set_cooldown_x(True)
        if abs(x_axis) < 0.5 and player.selecter.cooldown_x:
            player.selecter.set_cooldown_x(False) 
        if abs(y_axis) > 0.5 and not player.selecter.cooldown_y:
            player.selecter.move_y(y_axis)
            player.selecter.set_cooldown_y(True)
        if abs(y_axis) < 0.5 and player.selecter.cooldown_y:
            player.selecter.set_cooldown_y(False)
            
        if player.controller.get_button(0) and not player.option_cooldown:
            if player.selecter.position == [0, 0]:
                player.selecter.set_valeur([0, 0])
            if player.selecter.position == [0, 1]:
                player.selecter.set_valeur([0, 1])
            if player.selecter.position == [1, 0]:
                player.selecter.set_valeur([1, 0])
            if player.selecter.position == [1, 1]:
                player.selecter.set_valeur([1, 1])
            if player.selecter.position == [1, 2]:
                player.selecter.set_valeur([1, 2])
            if player.selecter.position == [1, 3]:
                player.selecter.set_valeur([1, 3])
            player.set_option_cooldown(True)   
        elif not player.controller.get_button(0) and player.option_cooldown:
            player.set_option_cooldown(False)
            
    def update_settings(self):
        self.choice_colors_settings()
        self.choice_lines_settings()

    
    # Init map for party
    def load_map_from_file(self):
        with open(filepath, 'r') as f:
            lines = f.readlines()
            for line in lines:
                for caracters in line:
                    if caracters == 'S':
                        MAP.append('S')
                    if caracters == '0':
                        MAP.append(0)
                    if caracters == '1':
                        MAP.append(1)
                    if caracters == '2':
                        MAP.append(2)
            return MAP
        
    def create_tiles(self):
        for y in range(case_y):
            for x in range(case_x):
                tiles.append(Tile(pygame.Rect(x*size_x, y*size_y, size_x, size_y)))
                
    def create_map(self):
        for tile in range(len(MAP)):
            if MAP[tile] == 'S':
                tiles[tile].set_state(0)
            if MAP[tile] == 0:
                tiles[tile].set_state(0)
            if MAP[tile] == 1:
                tiles[tile].set_state(1)
            if MAP[tile] == 2:
                tiles[tile].set_state(2)
                
    def create_decorations(self):
        for tile in range(len(tiles)):
            if tiles[tile].state == 1 and tiles[tile-case_x].state == 0 and tiles[tile-case_x-size_bush].decoration  == 0:
                if random.choice(p_decoration) == 1:
                    tiles[tile-case_x].set_decoration(1)
                    
    def create_edges(self):
        for tile in range(len(tiles)):
            if tiles[tile].state == 1:
                tiles[tile].edges = [] # Reset the edges var_list
                if tiles[tile-1].state != 1:
                    tiles[tile].set_edges("Left")
                if tiles[(tile+1) % len(tiles)].state != 1:
                    tiles[tile].set_edges("Right")
                if tiles[tile-case_x].state == 0:
                    tiles[tile].set_edges("Top")
                if tiles[(tile+case_x) % len(tiles)].state == 0:
                    tiles[tile].set_edges("Bottom")
                    
    # Init players for party
    def create_spawners(self):
        for tile in range(len(MAP)):
             if MAP[tile] == 'S':
                 tiles[tile].set_spawner(True)
                 spawners.append(tiles[tile])
                 
    def create_players(self):
        chosen_spawners = random.sample(spawners, nb_players)
        for player in players:
            player.set_rect(pygame.Rect((chosen_spawners[players.index(player)].rect.x, chosen_spawners[players.index(player)].rect.y), (32, 48)))
            
    # Init party
    def init_map(self):
        MAP = self.load_map_from_file()
        self.create_tiles()
        self.create_map()
        self.create_decorations()
        self.create_edges()
        
    def init_players_party(self):
        self.create_spawners()
        self.create_players()
        
    # Affichage party
    def affichage_background(self):
        screen.blit(Tile.images["BACKGROUND"], (0, 0))
    def affichage_tiles(self):
        for tile in tiles:
            if tile.state == 0:
                screen.blit(Tile.images["EMPTY_TILE"], tile.rect)
            if tile.state == 1:
                screen.blit(Tile.images["SOLID_TILE"], tile.rect)
            if tile.state == 2:
                screen.blit(Tile.images["DAMAGE_TILE"], tile.rect)
          
    def affichage_players(self):
        for player in players:
            pixel_array = pygame.PixelArray(Player.images[player.direction + "_STATE"])
            pixel_array.replace(pygame.Color("white"), pygame.Color(player.color))
            image_player = pixel_array.make_surface()
            screen.blit(image_player, player.rect)
            pixel_array = pygame.PixelArray(Player.images[player.direction + "_STATE"])
            pixel_array.replace(pygame.Color(player.color), pygame.Color("white"))
            image_player = pixel_array.make_surface()
            
    def affichage_decorations(self):
        for tile in tiles:
            if tile.decoration == 1:
                screen.blit(Tile.images["GRASS_DECORATION"], tile.rect)
                
    def affichage_edges(self):
        for tile in tiles:
            if tile.state == 1:
                if "Left" in tile.edges:
                        screen.blit(Tile.images["LEFT_EDGES"], tile.rect)
                if "Right" in tile.edges:
                        screen.blit(Tile.images["RIGHT_EDGES"], tile.rect)
                if "Top" in tile.edges:
                        screen.blit(Tile.images["TOP_EDGES"], tile.rect)
                if "Bottom" in tile.edges:
                        screen.blit(Tile.images["BOTTOM_EDGES"], tile.rect)
                        
    def affichage_attacks(self):
        for player in players:
             if player.attack != None:
                screen.blit(Attack.images[player.attack.direction + "_SWORD"], player.attack.rect)
                
    def affichage_board(self):
        pygame.draw.rect(screen, BLACK, (0, case_y*size_y - size_y*3, case_x*size_x, size_y*3))
        
    def affichage_scores(self):
        x_text = 10
        y_text = case_y*size_y - size_y*3
        for player in players:
            text = "Deaths of player : " + str(player.deaths)
            screen.blit(FONT_LITTLE.render(text, True, player.color), (x_text, y_text))
            if players.index(player) % 2 == 0:
                x_text += 750
            else:
                x_text = 10
                y_text += 30
                
    def affichage_timer(self):
        x_text, y_text = 425, case_y*size_y - size_y*3
        text = "Time : " + str(self.counter)
        screen.blit(FONT_BIG.render(text, True, WHITE), (x_text, y_text))
        
    # Maj party
    def affichage_party(self):
        self.affichage_background()
        self.affichage_tiles()
        self.affichage_players()
        self.affichage_decorations()
        self.affichage_edges()
        self.affichage_attacks()
        self.affichage_board()
        self.affichage_scores()
        self.affichage_timer()
        
    def controller_party(self, player):
        x_axis = player.controller.get_axis(0)
        y_axis = player.controller.get_axis(1)
        # right/left move with left stick :
        if abs(x_axis) > 0.5:
            player.move(x_axis)
            direction = "LEFT" if x_axis < -0.5 else "RIGHT"
            player.set_direction(direction)
        if abs(y_axis) > 0.2:
            direction = "TOP" if y_axis < -0.5 else "BOTTOM"
            player.set_direction(direction)
        # Jump button has to be relached for rejump :
        if player.controller.get_button(0) and not player.jump_cooldown:
            player.jump()
            player.set_jump_cooldown(True)
        elif not player.controller.get_button(0) and player.jump_cooldown:
            player.set_jump_cooldown(False)
        # Attack buttons :
        if player.controller.get_button(10) and not player.attack_cooldown:
            player.make_attack()
            player.set_attack_cooldown(True)
        elif not player.controller.get_button(10) and player.attack_cooldown:
            player.set_attack_cooldown(False)
            
    def update_party(self, player):
        player.check_death()
        player.update_move_x_collisions()
        player.update_move_y_collisions()
        if player.attack != None:
            player.attack.update_rect()
            player.attack.update_collisions()
        player.cooldowns()


    # Init players for menu
    def create_selecters_end(self):
        for player in players:
            player.set_selecter(Selecter([0, 1], 0))
            
    def create_selecters_color_end(self):
        for player in players:
            player.selecter.set_color(player.color)
            
    # Init menu
    def init_players_end(self):
        self.create_selecters_end()
        self.create_selecters_color_end()
        
    # Affichage end
    def find_classement(self, player):
        return player.deaths
    
    def affichage_final_scores(self):
        x_text, y_text = 340, 100
        text = "Players final score : "
        screen.blit(FONT_BIG.render(text, True, WHITE), (x_text, y_text))
        
    def affichage_classement(self):
        x_text, y_text = 330, 100
        players.sort(key=self.find_classement)
        for player in players:
            y_text += 40
            text = "Player " + player.color + " is : " + str(players.index(player)+1) + " with " + str(player.deaths) + " deaths"
            screen.blit(FONT_LITTLE.render(text, True, player.color), (x_text-10, y_text+40))
            
    def affichage_new_game_end(self):
        x_text, y_text = 360, 500
        text = "Select this for NEW GAME"
        screen.blit(FONT_LITTLE.render(text, True, WHITE), (x_text, y_text))
        
    def affichage_return_settings_end(self):
        x_text, y_text = 320, 540
        text = "Select this for RETURN SETTINGS"
        screen.blit(FONT_LITTLE.render(text, True, WHITE), (x_text, y_text))
        
    def affichage_vote_end(self):
        x_text, y_text = 240, 500
        for line in players[-1].selecter.states:
            nb_vote = len([player for player in players if player.selecter.valeur == line])
            if nb_vote != 0:
                text = "(" + str(nb_vote) + "/" + str(nb_players) + ")"
                screen.blit(FONT_LITTLE.render(text, True, WHITE), (x_text, y_text+40*line))
                
    def affichage_selecters_lines_end(self):
        for player in players:
            if player.selecter.position <= 1:
                x_text = 700 + 20*players.index(player)+1
                y_text = 500 + ESPACE_LINES*player.selecter.position - TAILLE_CRUSEUR
                text = "<"
                screen.blit(FONT_BIG.render(text, True, player.selecter.color), (x_text, y_text))
                
    # Update end
    def choice_lines_end(self):
        choice = []
        for player in players:
            choice.append(player.selecter.valeur)
        if choice.count(0) >= math.floor(nb_players/2+1):
            self.reset_end()
            self.set_state("party")
        if choice.count(1) >= math.floor(nb_players/2+1):
            self.reset_end()
            self.set_state("settings")
            
    def reset_end(self):
        global players
        MAP.clear()
        tiles.clear()
        spawners.clear()
        players = [player.reset() for player in players]
        
    # Maj end
    def affichage_end(self):
        screen.fill(BLACK)
        self.affichage_final_scores()
        self.affichage_classement()
        self.affichage_new_game_end()
        self.affichage_return_settings_end()
        self.affichage_vote_end()
        self.affichage_selecters_lines_end()
        
    def controller_end(self, player):
        y_axis = player.controller.get_axis(1)
        if abs(y_axis) > 0.5 and not player.selecter.cooldown_y:
            player.selecter.move(y_axis)
            player.selecter.set_cooldown_y(True)
        if abs(y_axis) < 0.5 and player.selecter.cooldown_y:
            player.selecter.set_cooldown_y(False)
            
        if player.controller.get_button(0) and not player.option_cooldown:
            if player.selecter.position == 0:
                player.selecter.set_valeur(0)
            if player.selecter.position == 1:
                player.selecter.set_valeur(1)
            player.set_option_cooldown(True)
        elif not player.controller.get_button(0) and player.option_cooldown:
            player.set_option_cooldown(False)
            
    def update_end(self):
        self.choice_lines_end()
        

# Class for the game
class Tile():
    images = {"BACKGROUND" : pygame.image.load("textures/background.png").convert(),
              "SOLID_TILE" : pygame.image.load("textures/solid_tile.png").convert_alpha(),
              "DAMAGE_TILE" : pygame.image.load("textures/damage_tile.png").convert_alpha(),
              "EMPTY_TILE" : pygame.image.load("textures/empty_tile.png").convert_alpha(),
              "GRASS_DECORATION" : pygame.image.load("textures/grass_decoration.png").convert_alpha(),
              "LEFT_EDGES" : pygame.image.load("textures/left_edges.png").convert_alpha(),
              "RIGHT_EDGES" : pygame.image.load("textures/right_edges.png").convert_alpha(),
              "TOP_EDGES" : pygame.image.load("textures/top_edges.png").convert_alpha(),
              "BOTTOM_EDGES" : pygame.image.load("textures/bottom_edges.png").convert_alpha()}

    def __init__(self, rect):
        self.rect = rect
        self.state = 0
        self.decoration = 0
        self.edges = []
        self.spawner = None

    def set_state(self, state):
        self.state = state
    def set_decoration(self, decoration):
        self.decoration = decoration
    def set_edges(self, direction):
        self.edges += [direction]
    def set_spawner(self, spawner):
        self.spawner = spawner


class Player():
    images = {"IMMOBILE_STATE" : pygame.image.load("textures/immobile_state.png").convert_alpha(),
              "LEFT_STATE" : pygame.image.load("textures/left_state.png").convert_alpha(),
              "RIGHT_STATE" : pygame.image.load("textures/right_state.png").convert_alpha(),
              "TOP_STATE" : pygame.image.load("textures/top_state.png").convert_alpha(),
              "BOTTOM_STATE" : pygame.image.load("textures/bottom_state.png").convert_alpha()}
    constants = {"SPEED" : 8, "JUMP_POWER" : 16, "GRAVITY" : 1.2, "INVINCIBILIY_DURATION" : 200}

    def __init__(self, controller):
        self.controller = controller
        self.rect = None
        self.selecter = None
        self.color = None
        self.deaths = 0

        self.health = 100
        self.invincibility_time = 0
        
        self.jump_cooldown = True
        self.attack_cooldown = True
        self.option_cooldown = True
        
        self.velocity_x = 0
        self.velocity_y = 0
        self.direction = "IMMOBILE"
        
        self.on_ground = False
        self.invincibility = False
        self.attack = None

    def set_rect(self, rect):
        self.rect = rect
    def set_selecter(self, selecter):
        self.selecter = selecter
    def set_color(self, color):
        self.color = color
    def set_jump_cooldown(self, jump_cooldown):
        self.jump_cooldown = jump_cooldown
    def set_attack_cooldown(self, attack_cooldown):
        self.attack_cooldown = attack_cooldown
    def set_option_cooldown(self, option_cooldown):
        self.option_cooldown = option_cooldown
    def set_invincibility(self):
        self.invincibility = True
        self.invincibility_time = pygame.time.get_ticks()
    def set_direction(self, direction):
        self.direction = direction

    def get_damage(self, damage):
        if not self.invincibility:
            self.health -= damage
            self.set_invincibility()
            
    def check_death(self):
        if self.health <= 0:
            self.deaths += 1
            self.respawn()
            
    def respawn(self):
        # stats
        self.health = 100
        self.invincibility_time = 0
        self.jump_cooldown = True
        self.attack_cooldown = True
        self.velocity_x = 0
        self.velocity_y = 0
        self.direction = "IMMOBILE"
        self.on_ground = True
        self.attack = None
        self.set_invincibility()
        # position
        chosen_spawner = random.choice([spawner for spawner in spawners if not spawner.rect.collidelistall(players)]) # Prevent spawn on other players
        self.rect.x = chosen_spawner.rect.x
        self.rect.y = chosen_spawner.rect.y
        
    def reset(self):
        self.rect = None
        self.selecter = None
        self.deaths = 0
        self.health = 100
        self.invincibility_time = 0
        self.jump_cooldown = True
        self.attack_cooldown = True
        self.option_cooldown = True
        self.velocity_x = 0
        self.velocity_y = 0
        self.direction = "IMMOBILE"
        self.on_ground = False
        self.invincibility = False
        self.attack = None
        return self
        
    def move(self, direction):
        self.velocity_x = direction * Player.constants["SPEED"]
    def jump(self):
        if self.on_ground:
            self.velocity_y -= Player.constants["JUMP_POWER"]
            self.on_ground = False
    def make_attack(self):
        if not self.attack:
            if self.direction == "IMMOBILE":
                return
            else:
                self.attack = Attack(self, self.direction)

    def get_collidable_objects(self, state):
        if state == "move":
            collidable_tiles = [tile for tile in tiles if tile.state != 0]
            other_players = [player for player in players if self.rect != player.rect]
            return [obj for obj in collidable_tiles + other_players]
        if state == "attack":
            collidable_tiles = [tile for tile in tiles if tile.state == 2]
            other_players = [player for player in players if self.rect != player.rect]
            return [obj for obj in collidable_tiles + other_players]

    def update_move_x_collisions(self):
        self.rect.x += self.velocity_x
        collidable_objects = self.get_collidable_objects("move")
        for collidable_object in collidable_objects:
            if self.rect.colliderect(collidable_object.rect):
                if self.velocity_x > 0:
                    self.rect.right = collidable_object.rect.left
                elif self.velocity_x < 0:
                    self.rect.left = collidable_object.rect.right
        self.velocity_x = 0
        
    def update_move_y_collisions(self):
        self.rect.y += self.velocity_y
        self.velocity_y += Player.constants["GRAVITY"]
        if self.velocity_y > 15:
            self.velocity_y = 15
        elif self.velocity_y > 4:
            self.on_ground = False
        collidable_objects = self.get_collidable_objects("move")
        for collidable_object in collidable_objects:
            if self.rect.colliderect(collidable_object.rect):
                if isinstance(collidable_object, Tile):
                    next_collidable_object = collidable_objects[collidable_objects.index(collidable_object)+1]
                    if collidable_object.state == 2:
                        # check right fall on spike/damage block
                        if next_collidable_object.state == 1 and self.rect.colliderect(next_collidable_object.rect): 
                            pass
                        else:
                            self.get_damage(100) # Player take damage (Dead)
                if self.velocity_y > 0:
                    self.rect.bottom = collidable_object.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:
                    self.rect.top = collidable_object.rect.bottom
                    self.velocity_y = 0
                    self.on_ground = False
                    
    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if self.attack:
            if current_time - self.attack.time >= Attack.constants["ATTACK_DURATION"]:
                self.attack = None
        if self.invincibility:
            if current_time - self.invincibility_time >= Player.constants["INVINCIBILIY_DURATION"]:
                self.invincibility = False


class Attack():
    images = {"LEFT_SWORD" : pygame.image.load("textures/left_sword.png").convert_alpha(),
              "RIGHT_SWORD" : pygame.image.load("textures/right_sword.png").convert_alpha(),
              "TOP_SWORD" : pygame.image.load("textures/top_sword.png").convert_alpha(),
              "BOTTOM_SWORD" : pygame.image.load("textures/bottom_sword.png").convert_alpha()}
    constants = {"ATTACK_DURATION" : 200}
    
    def __init__(self, player, direction):
        self.player = player
        self.direction = direction
        self.time = pygame.time.get_ticks()
        self.rect = self.update_rect()

    def update_rect(self):
        if self.direction == "LEFT":
            self.rect = pygame.Rect(self.player.rect.x-size_x, self.player.rect.y+(size_y/2)-(sword_width/2), size_x, sword_width)
        elif self.direction == "RIGHT":
            self.rect = pygame.Rect(self.player.rect.x+size_x, self.player.rect.y+(size_y/2)-(sword_width/2), size_x, sword_width)
        elif self.direction == "TOP":
            self.rect = pygame.Rect(self.player.rect.x+(size_x/2)-(sword_width/2), self.player.rect.y-size_y, sword_width, size_y)
        elif self.direction == "BOTTOM":
            self.rect = pygame.Rect(self.player.rect.x+(size_x/2)-(sword_width/2), self.player.rect.y+size_y, sword_width, size_y)
            
    def update_collisions(self):
        collidable_objects = self.player.get_collidable_objects("attack")
        for collidable_object in collidable_objects:
            if isinstance(collidable_object, Tile) and self.direction == "BOTTOM":
                if self.rect.colliderect(collidable_object.rect):
                    self.player.set_invincibility() # Frames of invincibility
                    self.player.controller.rumble(0.5, 1, 200) # Rumblings of controller (don't work)
                    self.player.jump()
            if isinstance(collidable_object, Player):
                if collidable_object.attack != None and self.rect.colliderect(collidable_object.attack.rect):
                    self.player.set_invincibility() #  Frames of invincibility
                    if self.direction == "BOTTOM":
                        self.player.jump()
                elif self.rect.colliderect(collidable_object.rect):
                    if self.direction == "BOTTOM":
                        self.player.on_ground = True
                        collidable_object.get_damage(100)
                        self.player.jump()
                    else:
                        collidable_object.get_damage(50)


class Selecter():
    def __init__(self, states, position):
        self.states = states
        self.position = position
        self.color = "WHITE"
        self.valeur = None
        self.cooldown_x = None
        self.cooldown_y = None

    def set_color(self, color):
        self.color = color 
    def set_valeur(self, valeur):
        self.valeur = valeur
    def set_cooldown_x(self, cooldown_x):
        self.cooldown_x = cooldown_x
    def set_cooldown_y(self, cooldown_y):
        self.cooldown_y = cooldown_y
        
    def move(self, direction):
        if direction > 0:
            self.position = self.states[(self.position+1) % len(self.states)]
        if direction < 0:
            self.position = self.states[(self.position-1) % len(self.states)] 
    def move_x(self, x_axis):
        if x_axis > 0:
            self.position[0] = self.states.index(self.states[(self.position[0]+1) % len(self.states)])
        if x_axis < 0:
            self.position[0] = self.states.index(self.states[(self.position[0]-1) % len(self.states)])
        self.position[1] = self.states[self.position[0]][0]    
    def move_y(self, y_axis):
        if y_axis > 0:
            self.position[1] = self.states[self.position[0]][(self.position[1]+1) % len(self.states[self.position[0]])]
        if y_axis < 0:
            self.position[1] = self.states[self.position[0]][(self.position[1]-1) % len(self.states[self.position[0]])]
    
    
# Close process function
def destroy():
    pygame.quit()
    exit()

# Main loop of the game
def main_game_loop():
    # Init game
    game = Game("menu")
    
    while True :
        for event in pygame.event.get():
            # Close and shut down program
            if event.type == QUIT:
                destroy()
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    destroy()
            # Time counter
            if event.type == pygame.USEREVENT: 
                game.counter -= 1
                if game.counter == 0:
                    game.set_state("end")

        clock.tick(60) # FPS of the game

        if game.state == "menu":
            game.affichage_menu()
            for player in players:
                game.controller_menu(player)
            game.update_menu()

        if game.state == "settings":
            game.affichage_settings()
            for player in players:
                game.controller_settings(player)
            game.update_settings()
            
        if game.state == "party":
            game.affichage_party()
            for player in players:
                game.controller_party(player)
                game.update_party(player)
                
        if game.state == "end":
            game.affichage_end()
            for player in players:
                game.controller_end(player)
            game.update_end()
        
        pygame.display.flip()
        
if __name__ == '__main__':
    main_game_loop()

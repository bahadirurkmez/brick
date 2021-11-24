# Imports
import sys, os
import pygame
from pygame.locals import *
import random, time
from enum import Enum
import pickle

 
######################################################
###
### v0.1 to v0.1.1 changes
### bugfix: ball gets stuck in top line solved
### bugfix: label locations corrected for levelup state
###
### v0.1.1 to v0.1.2 changes
### improvement: added time delay between gifts
### added level 11

#######################################################
#              Initial Setup                          #
#######################################################

# TODO: CHECK LOGIC FOR GIFT DROP WHEN FIRING ISNOT ALLOWED
# TODO: CHECK LOGIC FOR BALL GIFT COLLISION
# TODO: ADD MUSIC TO GIFT - BOARD COLLISION
# TODO: CODE BRIDGE TYPE BRICK LAYOUT
# TODO: LEVEL 1 and LEVEL 2 BORING. ESPECIALLY WHEN ONLY A FEW BRICKS LEFT FIND A SOLUTION
# TODO: CAN GROW CAN SHRINK LOGIC
# TODO: MAKE LEVELS 15
# TODO: SAVE STATE AFTER LEVELUP and ASK at the beginning if user wants to open last saved



#Initializing 
pygame.init()
pygame.mixer.init()
font_preferences = [
        "Roboto",
        "Montserrat",
        "Times",
        "Comic Sans MS"]

# Frame Per Second
fps = 30
fpsClock = pygame.time.Clock()

def find_data_file(filename):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        datadir = os.path.dirname(__file__)
    # The following line has been changed to match where you store your data files:
    return os.path.join(datadir, 'resources', filename)


sound_brick_destroyed = pygame.mixer.Sound(os.path.join(find_data_file('brick_destroyed.ogg')))
sound_brick_hit = pygame.mixer.Sound(os.path.join(find_data_file('brick_hit.ogg')))
sound_life_lost = pygame.mixer.Sound(os.path.join(find_data_file('life_lost.ogg')))
sound_board_hit = pygame.mixer.Sound(os.path.join(find_data_file('paddle_hit.ogg')))
sound_wall_hit =  pygame.mixer.Sound(os.path.join(find_data_file('wall_hit.ogg')))

#########################################################
#                 classes                               #
#########################################################
class GameStates(Enum):
    NEW = 'new'
    SERVE = 'serve'
    PLAY = 'play'
    GAMEOVER = 'gameover'
    LEVELUP =   'levelup'
    PLAYERHIGHSCORED = 'playerhigh'
    GAMEWON = 'gamewon'

    def __str__(self) -> str:
        return self.value

class DirectionChanges(Enum):
    VERTICAL = 0
    HORIZONTAL = 1
    BOTH = 2

    def __str__(self) -> str:
        return self.value

class BrickTypes(Enum):
    # Brick types
    # Index 0 is hits required to kill
    # index 1 is image
    # index 2 is the points to earn with each hit
    # index 3 gifts that brick discharges

    PLAIN =     (1,'brick.png',20,['grow'])
    MARILYN =   (2, 'marilyn.png',30,['lives', 'grow'])
    EVA =       (3, 'eva.png',40,['lives', 'ammo'])
    CHARLIZE =  (4, 'charlize.png',50,['ammo', 'bomb'])


class GameVars():

    # Brick types in each level
    # index 0: tuple of brick count in rows and columns
    # Index 1: tuple of possible bricks and percantage of them in whole
    # Index 2: Board can grow
    # Index 3: Board can shrink
    # Index 4: tuple of board's firing option (False/True,({Ammo type:Quantity})
    # Index 5: speed coeff
    # Index 6: maximum gifts to be given
    # Index 7: 

    LEVELS = {
    1:((9,5),((BrickTypes.PLAIN,100),),False,False,(False,{}),1.1,3),
    2:((5,5),((BrickTypes.PLAIN,66),(BrickTypes.MARILYN,34)),False,False,(False,{}),1.1,3),
    3:((9,8),((BrickTypes.PLAIN,66),(BrickTypes.MARILYN,34)),False,False,(False,{}),1.1,4),
    4:((9,7),((BrickTypes.PLAIN,50),(BrickTypes.MARILYN,50)),False,False,(True,{'ammo':24}),1.3,4),
    5:((9,6),((BrickTypes.PLAIN,50),(BrickTypes.MARILYN,30),(BrickTypes.EVA,20)),False,False,(True,{'ammo': 15}),1.35,4),
    6:((8,8),((BrickTypes.PLAIN,40),(BrickTypes.MARILYN,27),(BrickTypes.EVA,23),(BrickTypes.CHARLIZE,10)),True,False,
                (True,{'ammo': 9}),1.35,5),
    7:((9,7),((BrickTypes.PLAIN,10),(BrickTypes.MARILYN,40),(BrickTypes.EVA,32),(BrickTypes.CHARLIZE,18)),True,True,
                (True,{'ammo': 7,'bomb':9}),1.35,5),
    8:((9,7),((BrickTypes.PLAIN,10),(BrickTypes.MARILYN,20),(BrickTypes.EVA,35),(BrickTypes.CHARLIZE,25)),True,True,
                (True,{'ammo': 9,'bomb':9}),1.4,7),
    9:((9,7),((BrickTypes.PLAIN,8),(BrickTypes.MARILYN,24),(BrickTypes.EVA,36),(BrickTypes.CHARLIZE,32)),True,True,
                (True,{'ammo': 12,'bomb':12}),1.4,9),
    10:((9,8),((BrickTypes.PLAIN,2),(BrickTypes.MARILYN,27),(BrickTypes.EVA,39),(BrickTypes.CHARLIZE,32)),True,True,
                (True,{'ammo': 12,'bomb':12}),1.4,9),
    11:((9,9),((BrickTypes.PLAIN,4),(BrickTypes.MARILYN,24),(BrickTypes.EVA,36),(BrickTypes.CHARLIZE,36)),True,True,
                (True,{'ammo': 12,'bomb':12}),1.4,9),
    }
    SCORE = 0
    LIVES = 7
    LEVEL = 1
    LEVELOPTS = LEVELS[LEVEL]
    GAMESTATE = GameStates.NEW
    AVAILABLEGIFTCOUNT= LEVELOPTS[6]
    ISGIFTAVAIL = True
    GIFTTIME = pygame.time.get_ticks()
    AMMOCOUNT = LEVELOPTS[4][1].get('ammo',0)
    BOMBCOUNT = LEVELOPTS[4][1].get('bomb',0)
    MAXAMMO = 24
    MAXBOMB = 20
    ISSCORECHECKED = False
    PLAYERPLACE = 6

    try:
        with open(find_data_file('scores.dat'), 'rb') as file: 
            SCORES = pickle.load(file)
            for i in range(len(SCORES)-1):
                for j in range(len(SCORES)-i-1):
                    if SCORES[j][1] <= SCORES[j+1][1]:
                        SCORES[j], SCORES[j+1] = SCORES[j+1], SCORES[j]
    except:
       #  SCORES = [['ALARA',21920,9],['BAHAD',20870,9],['SELIN',13200,6],['_____',0,0],['_____',0,0]]
        SCORES = [['_____',0,0],['_____',0,0],['_____',0,0],['_____',0,0],['_____',0,0]]
class Gift(pygame.sprite.Sprite):
    def __init__(self,type):
        super(Gift, self).__init__()
        self.yspeed = 3
        self.type = type
        self.animation_frames = 10
        self.current_frame = 0
        self.index = 0
        images = {
                    'lives': ['heart.png','heart_1.png','heart_2.png','heart_3.png'], 
                    'grow': ['board_gift.png','board_gift_1.png','board_gift_2.png','board_gift_3.png'],
                    'ammo': ['ammo.png','ammo.png','ammo.png','ammo.png'],
                    'bomb': ['bomb.png','bomb.png','bomb.png','bomb.png'],
                    }
        self.images = images
        self.image = pygame.image.load(os.path.join(find_data_file(self.images[self.type][self.index])))
        self.rect = self.image.get_rect()
        self.isAlive = False
        
    def update(self,surface, ball, ammo, bomb, board):
        self.rect.y = self.rect.y + self.yspeed
        self.current_frame +=1
        if self.current_frame >= self.animation_frames:
            self.current_frame = 0
            self.index = (self.index + 1) % len(self.images)
            self.image = pygame.image.load(os.path.join(find_data_file(self.images[self.type][self.index])))

        if self.checkcollision(board.rect) and self.isAlive and GameVars.GAMESTATE == GameStates.PLAY: 
            # board collision with gifts
            if self.type == 'lives': 
                GameVars.LIVES +=1
                self.isAlive = False
            elif self.type == 'grow':
                initialw = board.rect.width
                board.image = pygame.image.load(os.path.join(find_data_file('board_grow.png')))
                neww = board.image.get_rect().width
                if playingarea['x'] + (neww - initialw) > board.rect.x: board.rect.x += neww - initialw
                if playingarea['x'] + playingarea['w'] < board.rect.x + neww: board.rect.x -= neww - initialw
                board.rect = Rect(board.rect.x, board.rect.y, neww, board.rect.height)
                board.timer = fps
                board.state = 'grow'
                self.isAlive = False
            elif self.type == 'ammo':
                GameVars.AMMOCOUNT += 1 if GameVars.AMMOCOUNT < GameVars.MAXAMMO else 0
                self.isAlive = False
            elif self.type == 'bomb': 
                GameVars.BOMBCOUNT += 1 if GameVars.BOMBCOUNT < GameVars.MAXBOMB else 0
                self.isAlive = False
        elif self.checkcollision(ball.rect) and self.isAlive and GameVars.GAMESTATE == GameStates.PLAY:
            # ball collision with gift
            pass
        elif (self.checkcollision(ammo.rect) or self.checkcollision(bomb.rect)) and self.isAlive and GameVars.GAMESTATE == GameStates.PLAY:
            # ammo and bomb collision collision with gift
            if ammo != None: ammo.isAlive = False
            if bomb != None: bomb.isAlive = False
            self.isAlive = False
        surface.blit(self.image, self.rect)
    
    def checkcollision(self, rectobj):
        return rectobj.colliderect(self.rect)

class Ammo(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.isAlive = False
        self.yspeed = 0 # speed along y
        self.image = pygame.image.load(os.path.join(find_data_file('ammo.png')))
        self.rect = self.image.get_rect()

    def checkcollision(self, rectobj):
        return rectobj.colliderect(self.rect)

    def update(self,surface, state, ball, bricks):
        self.rect.y = self.rect.y + self.yspeed

        # passes the playing area
        if self.rect.y < 0: self.isAlive = False

        # check if any brcik hit
        for b in bricks:
            if self.checkcollision(b.rect) and b.isAlive:
                GameVars.SCORE += b.score
                b.isAlive = False
                self.isAlive = False
                pygame.mixer.Sound.play(sound_brick_destroyed)
                break
        
        # check if we hit ball
        if self.checkcollision(ball.rect):
            ball.isAlive = False
            ball.isHit = True
            self.isAlive = False
            pygame.mixer.Sound.play(sound_life_lost)
        
        surface.blit(self.image, self.rect)

class Bomb(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.isAlive = False
        self.yspeed = 0 # speed along y
        self.image = pygame.image.load(os.path.join(find_data_file('bomb.png')))
        self.rect = self.image.get_rect()

    def checkcollision(self, rectobj):
        return rectobj.colliderect(self.rect)

    def update(self,surface, state, ball, bricks):
        self.rect.y = self.rect.y + self.yspeed

        # passes the playing area
        if self.rect.y < 0: self.isAlive = False

        # check if any brcik hit
        for b in bricks:
            if self.checkcollision(b.rect) and b.isAlive:
                GameVars.SCORE += b.score
                b.isAlive = False
                self.isAlive = False  
                livebricks =[lb for lb in bricks if lb.isAlive]
                for i in range(2):
                    if len(livebricks) == 0: break
                    lb = random.choice(livebricks)
                    lb.isAlive = False
                pygame.mixer.Sound.play(sound_brick_destroyed) # change this to explosion
                break      
        # check if we hit ball
        if self.checkcollision(ball.rect):
            ball.isAlive = False
            ball.isHit = True
            self.isAlive = False
            pygame.mixer.Sound.play(sound_life_lost)
            
        surface.blit(self.image, self.rect)

class Brick(pygame.sprite.Sprite):
    def __init__(self,type):
        pygame.sprite.Sprite.__init__(self)
        self.type = type.value
        self.requiredhit = self.type[0]
        self.image = pygame.image.load(os.path.join(find_data_file(self.type[1])))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.isAlive = True
        self.score = self.type[2]

    def update(self,surface):
        surface.blit(self.image, self.rect)
    
    def setNewConditions(self,type):
        self.type = type.value
        self.image = pygame.image.load(os.path.join(find_data_file(self.type[1])))

class Ball(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.xspeed = 0 # speed along X
        self.yspeed = 5 # speed along y
        self.speed = (self.xspeed ** 2 + self.yspeed **2) ** 0.5
        self.image = pygame.image.load(os.path.join(find_data_file('ball.png')))
        self.rect = self.image.get_rect()
        self.isAlive = True
        self.isOnPaddle = False
        self.isHit = False   # will be true if hit by ammo or bomb
   
    ## circle to rectangle collisions
    def checkcollision(self, rectobj):
        collision = [False] * 9

        collision[0] = rectobj.collidepoint(self.rect.midbottom)
        collision[1] = rectobj.collidepoint(self.rect.midtop)
        collision[2] = rectobj.collidepoint(self.rect.topleft)
        collision[3] = rectobj.collidepoint(self.rect.topright)
        collision[4] = rectobj.collidepoint(self.rect.bottomright)
        collision[5] = rectobj.collidepoint(self.rect.bottomleft)
        collision[6] = rectobj.collidepoint(self.rect.midleft)
        collision[7] = rectobj.collidepoint(self.rect.midright)
        collision[8] = rectobj.collidepoint(self.rect.center)

        if collision[0] or collision[1]:
            return DirectionChanges.VERTICAL
        elif collision[2] or collision[3] or collision[4] or collision[5] or collision[8]:
            return DirectionChanges.BOTH
        elif collision[6] or collision[7]:
            return DirectionChanges.HORIZONTAL
        else:
            return None
    
    def update(self,surface, state, board, bricks):
        if state == GameStates.NEW:
            # jump ball up and down
            self.rect.y = self.rect.y + self.yspeed
            r = Rect(board.rect.x, board.rect.y-200, board.rect.width, board.rect.height)
            if self.checkcollision(board.rect) == DirectionChanges.VERTICAL or self.checkcollision(r)==DirectionChanges.VERTICAL:
                self.yspeed = -self.yspeed
                pygame.mixer.Sound.play(sound_board_hit)
        elif  state == GameStates.SERVE:
            self.rect.y = board.rect.y - self.rect.height
            self.isOnPaddle = True
            self.xspeed = board.speed
            self.rect.x = self.rect.x + self.xspeed
        elif state == GameStates.PLAY:
            self.rect.x = self.rect.x + self.xspeed
            self.rect.y = self.rect.y + self.yspeed

            if self.rect.x <= playingarea['x']: 
                self.xspeed =  - self.xspeed
                self.rect.x = playingarea['x']
                pygame.mixer.Sound.play(sound_wall_hit)
            elif self.rect.x + self.rect.width >= playingarea['x'] + playingarea['w']:
                self.xspeed =  - self.xspeed
                self.rect.x = playingarea['x'] + playingarea['w'] - self.rect.width
                pygame.mixer.Sound.play(sound_wall_hit)

            if self.rect.y < playingarea['y']:
                self.yspeed = -self.yspeed
                self.rect.y = playingarea['y']
                pygame.mixer.Sound.play(sound_wall_hit)
            elif self.rect.y + self.rect.height > playingarea['y'] + playingarea['h']: # we are on the line with board
                c = self.checkcollision(board.rect)
                if c == DirectionChanges.VERTICAL: 
                     self.yspeed = -self.yspeed
                     self.xspeed +=  random.uniform(0,0.05)* board.speed
                     pygame.mixer.Sound.play(sound_board_hit)
                elif c == DirectionChanges.HORIZONTAL:
                    self.xspeed = -self.xspeed + random.uniform(0,0.05)* board.speed
                elif c == DirectionChanges.BOTH:
                    self.xspeed = -self.xspeed + random.uniform(0,0.05)* board.speed
                    self.yspeed = -self.yspeed
                    pygame.mixer.Sound.play(sound_board_hit)
                else:
                    pygame.mixer.Sound.play(sound_life_lost)
                    ammo.isAlive = False
                    bomb.isAlive = False
                    self.isAlive = False
    
            #check collision with bricks
            for b in bricks:
                collision = None
                collision = self.checkcollision(b.rect)
                if collision == DirectionChanges.VERTICAL and b.isAlive:
                    self.yspeed = -self.yspeed * 1.01
                    self.setBrickScoreandAlive(b, collision)
        
                elif collision == DirectionChanges.HORIZONTAL and b.isAlive:
                    self.xspeed = -self.xspeed * 1.01
                    self.setBrickScoreandAlive(b, collision)
                    
                elif collision == DirectionChanges.BOTH and b.isAlive:
                    self.yspeed = -self.yspeed * 1.01
                    self.xspeed = -self.xspeed * 1.01
                    self.setBrickScoreandAlive(b, collision)
                            
            # get brick count
            cnt = 0
            for i in Bricks:
                if i.isAlive: cnt += 1
            if cnt == 0: 
                if GameVars.LEVEL < len(GameVars.LEVELS):
                    GameVars.GAMESTATE = GameStates.LEVELUP
                    GameVars.LEVEL +=1
                    GameVars.LEVELOPTS = GameVars.LEVELS[GameVars.LEVEL]
                    if GameVars.AMMOCOUNT + GameVars.LEVELOPTS[4][1].get('ammo',0) <= GameVars.MAXAMMO:
                        GameVars.AMMOCOUNT = GameVars.AMMOCOUNT + GameVars.LEVELOPTS[4][1].get('ammo',0)
                    else:
                        GameVars.AMMOCOUNT = GameVars.MAXAMMO
                    
                    if GameVars.BOMBCOUNT + GameVars.LEVELOPTS[4][1].get('bomb',0)<= GameVars.MAXBOMB:
                        GameVars.BOMBCOUNT = GameVars.BOMBCOUNT + GameVars.LEVELOPTS[4][1].get('bomb',0)
                    else:
                        GameVars.BOMBCOUNT = GameVars.MAXBOMB

                    GameVars.AVAILABLEGIFTCOUNT = GameVars.LEVELOPTS[6] 
                else: GameVars.GAMESTATE = GameStates.GAMEWON
            
        surface.blit(self.image, self.rect)

    def setBrickScoreandAlive(self,b, collision):
        GameVars.SCORE += b.score
        if collision != None and b.isAlive and GameVars.AVAILABLEGIFTCOUNT > 0 and random.random()>0.9 and GameVars.ISGIFTAVAIL:
            gift = Gift(random.choice(b.type[3]))
            gift.rect.x = b.rect.x + b.rect.width // 2
            gift.rect.y = b.rect.y + b.rect.height
            gift.isAlive = True
            AllGifts.append(gift)
            GameVars.ISGIFTAVAIL = False
            GameVars.GIFTTIME = pygame.time.get_ticks()
            GameVars.AVAILABLEGIFTCOUNT -=1

        # check if brick is alive
        b.requiredhit -= 1
        if b.requiredhit == 0: 
            b.isAlive = False
            pygame.mixer.Sound.play(sound_brick_destroyed)
        else:
            pygame.mixer.Sound.play(sound_brick_hit)
            # get brick type that needs required hit number to be killed
            for t in BrickTypes:
                if t.value[0] == b.requiredhit: b.setNewConditions(t)

class Board(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(find_data_file('board.png')))
        self.rect = self.image.get_rect()
        self.speed = 0
        self.timer = 0
        self.state = 'normal'
    
    def update(self,surface):
        tmppos= self.rect.x + self.speed 
        if not (tmppos < playingarea['x'] or tmppos + self.rect.width > playingarea['x'] + playingarea['w']): # rigth side of playing area
            self.rect.x =tmppos
        else: self.speed = 0
        if self.timer == 0 and self.state == 'grow':
            self.image = pygame.image.load(os.path.join(find_data_file('board.png')))
            self.rect = Rect(self.rect.x, self.rect.y,self.image.get_rect().width, self.rect.height)
            self.state = 'normal'

        surface.blit(self.image, self.rect)

###################################################################
#                    FUNCTIONS                                    #
###################################################################

# font functions from
# https://nerdparadise.com/programming/pygame/part5

def make_font(fonts, size):
    available = pygame.font.get_fonts()
    # get_fonts() returns a list of lowercase spaceless font names
    choices = map(lambda x:x.lower().replace(' ', ''), fonts)
    for choice in choices:
        if choice in available:
            return pygame.font.SysFont(choice, size)
    return pygame.font.Font(None, size)
    
_cached_fonts = {}
def get_font(font_preferences, size):
    global _cached_fonts
    key = str(font_preferences) + '|' + str(size)
    font = _cached_fonts.get(key, None)
    if font == None:
        font = make_font(font_preferences, size)
        _cached_fonts[key] = font
    return font

_cached_text = {}
def create_text(text, fonts, size, color):
    global _cached_text
    key = '|'.join(map(str, (fonts, size, color, text)))
    image = _cached_text.get(key, None)
    if image == None:
        font = get_font(fonts, size)
        image = font.render(text, True, color)
        _cached_text[key] = image
    return image

def setScore():
    global score
    label = create_text('Score',font_preferences,32,(255,255,0))
    screen.blit(label, (scorearea['x'] + scorearea['w'] // 2  - label.get_width() //2,120))
    label = create_text(str(GameVars.SCORE),font_preferences,32,(255,255,255))
    screen.blit(label, (scorearea['x'] + scorearea['w'] // 2  - label.get_width() //2,160))

def LevelInfoUpdate():

    label = create_text('Level',font_preferences,32,(255,255,0))
    screen.blit(label, (scorearea['x'] + scorearea['w'] // 2  - label.get_width() //2,30))
    label = create_text(str(GameVars.LEVEL),font_preferences,32,(255,255,255))
    screen.blit(label, (scorearea['x'] + scorearea['w'] // 2  - label.get_width() //2,70))

    setScore()

    label = create_text('Lives',font_preferences,32,(255,255,0))
    screen.blit(label, (scorearea['x'] + scorearea['w'] // 2  - label.get_width() //2,210))
    label = create_text(str(GameVars.LIVES),font_preferences,32,(255,255,255))
    screen.blit(label, (scorearea['x'] + scorearea['w'] // 2  - label.get_width() //2,250))

    if GameVars.AMMOCOUNT > 0 or GameVars.BOMBCOUNT > 0:
        label = create_text('Arsenal',font_preferences,32,(255,255,0))
        screen.blit(label, (scorearea['x'] + scorearea['w'] // 2  - label.get_width() //2,300))
        img = pygame.image.load(os.path.join(find_data_file('ammo.png')))
        for a in range(GameVars.AMMOCOUNT):
            if a < 12:
                screen.blit(img, (scorearea['x'] + 12 +  a * (5 + img.get_width()),340))
            else:
                screen.blit(img, (scorearea['x'] + 20 +  (a - 12) * (5 + img.get_width()),360))

        img = pygame.image.load(os.path.join(find_data_file('bomb.png')))
        for a in range(GameVars.BOMBCOUNT):
            if a < 10:
                screen.blit(img, (scorearea['x'] + 15 +  a * (5 + img.get_width()),400))
            else:
                screen.blit(img, (scorearea['x'] + 15 +  (a - 10) * (5 + img.get_width()),430))

    label = create_text('Bahadir Urkmez',font_preferences,18,(255,255,255))
    screen.blit(label, (scorearea['x'] + scorearea['w'] // 2  - label.get_width() //2,550))

    label = create_text('Brick v0.1.2',font_preferences,18,(255,255,255))
    screen.blit(label, (scorearea['x'] + scorearea['w'] // 2  - label.get_width() //2,570))

def GenerateBricks():
    # First populate possible bricks
    possiblebricks = []
    for j in range(len(GameVars.LEVELOPTS[1])):
        for i in range(GameVars.LEVELOPTS[1][j][1]):
            possiblebricks.append(GameVars.LEVELOPTS[1][j][0])

    b = []
    cols = GameVars.LEVELOPTS[0][0]
    rows = GameVars.LEVELOPTS[0][1]
    if GameVars.LEVEL in [1,7]:
        left = (playingarea['w'] - cols * 60 - (cols-1)*5) // 2 + playingarea['x']
        top = 100
        b = linearbricks(cols,rows,left,top,possiblebricks)   
    elif GameVars.LEVEL in [2]:
        for i in diamondbricks(cols,rows,playingarea['x'] + 20, 100,(playingarea['w'] - 100) // 2,possiblebricks,True): b.append(i)
        for i in diamondbricks(cols,rows,playingarea['x'] + 230, 100,(playingarea['w'] -100),possiblebricks,True): b.append(i)
    elif GameVars.LEVEL in [6,8,11]: b = diamondbricks(cols,rows,playingarea['x'], 100,playingarea['w'],possiblebricks,True)
    elif GameVars.LEVEL in [4,9]: b = diamondbricks(cols,rows,playingarea['x'], 100,playingarea['w'],possiblebricks,False)
    elif GameVars.LEVEL in [3,5,10]:
        cols = rows = 2
        left = playingarea['x'] + 10
        top = playingarea['y'] + 10
        for i in linearbricks(cols,rows,left,top,possiblebricks): b.append(i)

        left = playingarea['x'] + 10
        top = playingarea['y'] + 210
        for i in linearbricks(cols,rows,left,top,possiblebricks): b.append(i)

        left = playingarea['x'] + playingarea['w'] - 15 - cols * 60
        top = playingarea['y'] + 10
        for i in linearbricks(cols,rows,left,top,possiblebricks): b.append(i)

        left = playingarea['x'] + playingarea['w'] - 15 - cols * 60
        top = playingarea['y'] + 210
        for i in linearbricks(cols,rows,left,top,possiblebricks): b.append(i)

        if GameVars.LEVEL != 5:
            cols = 7
            rows = 4
            left = (playingarea['w'] - cols * 60 - (cols-1)*5) // 2 + playingarea['x']
            top = playingarea['y'] + 85
            for i in linearbricks(cols,rows,left,top,possiblebricks): b.append(i)
        else:
            for i in diamondbricks(6,6,playingarea['x'], 40 ,playingarea['w'],possiblebricks,True): b.append(i)

    # remove all bricks left in possible bricks
    for pb in possiblebricks:
        pb  = None
    possiblebricks = []

    return b

def linearbricks(cols, rows, startleft, starttop, possiblebricks):
    b = []
    for i in range(cols):
        for j in range(rows):
            t = random.choice(possiblebricks)
            brick = Brick(t)
            possiblebricks.remove(t)
            brick.rect.x = startleft + i * (brick.rect.width + 5)
            brick.rect.y = starttop + j * (brick.rect.height + 5)
            b.append(brick) 
    return b

def diamondbricks(maxcols, maxrows,startleft, starttop, widthtocenter, possiblebricks, pyramid = False):
    b =[]
    for r in range(maxrows):
        if pyramid == True:
            rowcols = maxcols - maxrows + r + 1
        else:
            rowcols = maxcols - maxrows // 2 + r if r <= maxrows // 2 else maxcols + maxrows // 2 - r
        left = (widthtocenter - rowcols * 60 - (rowcols-1)*5) // 2 + startleft
        for c in range(rowcols):
            t = random.choice(possiblebricks)
            brick = Brick(t)
            possiblebricks.remove(t)
            brick.rect.x = left + c * (brick.rect.width + 5)
            brick.rect.y = starttop + r * (brick.rect.height + 5)
            b.append(brick)
    return b

def setScreen():
    global Bricks

    # blit background
    screen.blit(backdrop,backdropbox)
    if GameVars.GAMESTATE != GameStates.GAMEOVER and GameVars.GAMESTATE != GameStates.GAMEWON and GameVars.GAMESTATE != GameStates.PLAYERHIGHSCORED:
    # blit board
        board.update(screen)
        # blit ball
        ball.update(screen, GameVars.GAMESTATE, board, Bricks)

        if ammo.isAlive: ammo.update(screen, GameVars.GAMESTATE, ball, Bricks)
        if bomb.isAlive: bomb.update(screen, GameVars.GAMESTATE, ball, Bricks)
        
        # blit bricks
        if Bricks == []: Bricks = GenerateBricks()

        for b in Bricks:
            if b.isAlive: b.update(screen)
        
        if AllGifts != []:
            for g in AllGifts:
                if g.isAlive and GameVars.GAMESTATE == GameStates.PLAY: g.update(screen,ball,ammo, bomb, board)
                else: g.isAlive =False
            
        if GameVars.GAMESTATE ==GameStates.NEW:
            # write screen info
            label = create_text('Let\'s Break Some Bricks!', font_preferences, 36, (155, 155,155))
            screen.blit(label, (playingarea['w'] //2 - label.get_width() //2, 40))

            label = create_text('Press Any Key to Start', font_preferences, 36, (155, 155,155))
            screen.blit(label, (playingarea['w'] //2 - label.get_width() //2,300))

        elif GameVars.GAMESTATE == GameStates.SERVE:
            if ball.isHit:
                # write screen info
                label = create_text('Be careful not to hit ball', font_preferences, 28, (155, 155,155))
                screen.blit(label, (playingarea['w'] //2 - label.get_width() //2, 40))

            label = create_text('Press Space To Serve', font_preferences, 36, (155, 155,155))
            screen.blit(label, (playingarea['w'] //2 - label.get_width() //2,340))

        elif GameVars.GAMESTATE ==GameStates.LEVELUP:
            # write screen info
            label = create_text('GREAT YOU PASSED THE LEVEL!', font_preferences, 28, (155, 155,155))
            screen.blit(label, (playingarea['w'] //2 - label.get_width() //2, 290))

            label = create_text('Press Any Key to Continue', font_preferences, 36, (155, 155,155))
            screen.blit(label, (playingarea['w'] //2 - label.get_width() //2,340))    
    else:
        # write screen info
        if GameVars.GAMESTATE == GameStates.GAMEWON:
            label = create_text('YOU WIN!', font_preferences, 36, (155, 155,155))
        elif GameVars.GAMESTATE == GameStates.GAMEOVER:
            label = create_text('YOU LOOSE!', font_preferences, 36, (155, 155,155))
        elif GameVars.GAMESTATE == GameStates.PLAYERHIGHSCORED:
            label = create_text('HIGH SCORE!', font_preferences, 36, (155, 155,155))
        screen.blit(label, (playingarea['w'] //2 - label.get_width() //2, 40))

        # load the previous score if it exists
        label = create_text('HIGH SCORES!!', font_preferences, 32, (255, 255,155))
        screen.blit(label, (playingarea['w'] //2 - label.get_width() //2, 120))
      
        scores = GameVars.SCORES
        
        for i in range(len(scores)):
            c = (255, 5 + i* (20 + i * 6), 5 + i* 50)
            label = create_text('%s' % str(i + 1), font_preferences, 28, c)
            screen.blit(label, (playingarea['w'] //2 - label.get_width() //2 - 300, 130 + (i+1) * 40))
            label = create_text('%s' % scores[i][0], font_preferences, 28, c)
            screen.blit(label, (playingarea['w'] //2 - label.get_width() //2 - 200, 130 + (i+1) * 40))
            label = create_text('%s' % scores[i][1], font_preferences, 28, c)
            screen.blit(label, (playingarea['w'] //2 - label.get_width() //2, 130 + (i+1) * 40))
            label = create_text('LEVEL %s' % scores[i][2], font_preferences, 28, c)
            screen.blit(label, (playingarea['w'] //2 - label.get_width() //2 + 200, 130 + (i+1) * 40))


        if GameVars.GAMESTATE == GameStates.PLAYERHIGHSCORED:
            label = create_text('Enter your name then press Enter to record your name', font_preferences, 24, (255,255,255))
            screen.blit(label, (playingarea['w'] //2 - label.get_width() //2, 480))
        else:
            label = create_text('Press Q to QUIT or press N for NEW GAME', font_preferences, 24, (255,255,255))
            screen.blit(label, (playingarea['w'] //2 - label.get_width() //2, 550))

    # write level and other info
    LevelInfoUpdate()

#############################################
# SET GAME OPTIONS
#############################################
# Screen size
W = 900
H = 600
pygame.display.set_caption('ALARA\'s BRICK GAME')
screen = pygame.display.set_mode((W,H))
backdrop = pygame.image.load(os.path.join(find_data_file('stage.png')))
backdropbox = screen.get_rect()
playingarea = {'x':4,'y':4,'w':696, 'h':548}
scorearea = {'x':700,'y':0,'w':200, 'h':600}

Bricks = []
AllGifts = [] 

# create board
board = Board()
board.rect.x = (playingarea['w'] - playingarea['x']) // 2 - board.rect.width // 2
board.rect.y = playingarea['y'] + playingarea['h']

#create ball
ball = Ball()
ball.rect.y = board.rect.y - board.rect.height - 100
ball.rect.x = board.rect.x + board.rect.width // 2 - ball.rect.width // 2

ammo = Ammo()
bomb = Bomb()

def main():
    global Bricks, AllGifts
    main = True
    while main:
        es = pygame.event.get()
        pygame.event.set_blocked(pygame.MOUSEMOTION)
        pygame.mouse.set_visible(0)
        for event in es:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                main = False
            
            if GameVars.GAMESTATE == GameStates.NEW:
                if event.type == pygame.KEYDOWN: GameVars.GAMESTATE = GameStates.SERVE
            elif  GameVars.GAMESTATE == GameStates.SERVE:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # set ball speed
                        ball.yspeed = -5 * GameVars.LEVELOPTS[5]
                        ball.isHit = False
                        ball.xspeed = random.choice([-1,1]) * 5
                        GameVars.GAMESTATE = GameStates.PLAY
                        ball.isOnPaddle = False
                    elif event.key == pygame.K_LEFT:
                        if board.speed ==0: board.speed= -10
                        else: board.speed = -board.speed 
                    elif event.key == pygame.K_RIGHT:
                        if board.speed ==0: board.speed= 10
                        else: board.speed = -board.speed  
                elif event.type == pygame.KEYUP:
                    board.speed = 0
            elif GameVars.GAMESTATE == GameStates.PLAY:
                if board.timer > 0: board.timer -= 1
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if board.speed ==0: board.speed= -10
                        else: board.speed = -board.speed 
                    elif event.key == pygame.K_RIGHT:
                        if board.speed ==0: board.speed= 10
                        else: board.speed = -board.speed
                    elif event.key == pygame.K_a and GameVars.LEVELOPTS[4][0]:
                        if GameVars.AMMOCOUNT > 0 and not ammo.isAlive:
                            GameVars.AMMOCOUNT -= 1
                            ammo.isAlive = True
                            ammo.yspeed = -5
                            ammo.rect.x = board.rect.x + board.rect.width // 2
                            ammo.rect.y = board.rect.y - ammo.rect.height
                    
                    elif event.key == pygame.K_z and GameVars.LEVELOPTS[4][0]:
                        if GameVars.BOMBCOUNT > 0 and not bomb.isAlive:
                            GameVars.BOMBCOUNT -= 1
                            bomb.isAlive = True
                            bomb.yspeed = -5
                            bomb.rect.x = board.rect.x + board.rect.width // 2
                            bomb.rect.y = board.rect.y - bomb.rect.height                   
                elif event.type == pygame.KEYUP:
                    board.speed = 0
            elif GameVars.GAMESTATE == GameStates.LEVELUP and event.type == pygame.KEYDOWN: GameVars.GAMESTATE = GameStates.SERVE
            elif GameVars.GAMESTATE == GameStates.GAMEWON or GameVars.GAMESTATE == GameStates.GAMEOVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()
                            main = False
                    elif event.key == pygame.K_n:
                        # Set New Game
                        GameVars.GAMESTATE = GameStates.NEW
                        GameVars.SCORE = 0
                        GameVars.LIVES = 5
                        GameVars.LEVEL = 1
                        GameVars.LEVELOPTS = GameVars.LEVELS[GameVars.LEVEL]
                        GameVars.AVAILABLEGIFTCOUNT= GameVars.LEVELOPTS[6]
                        GameVars.AMMOCOUNT = GameVars.LEVELOPTS[4][1].get('ammo',0)
                        GameVars.BOMBCOUNT = GameVars.LEVELOPTS[4][1].get('bomb',0)
                        GameVars.MAXAMMO = 24
                        GameVars.MAXBOMB = 20
                        GameVars.ISSCORECHECKED = False
                        GameVars.PLAYERPLACE = 6
                        Bricks = []
                        AllGifts = []
                        ball.isAlive = True
                        
            elif GameVars.GAMESTATE == GameStates.PLAYERHIGHSCORED:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        with open(find_data_file('scores.dat'), 'wb') as file: pickle.dump(GameVars.SCORES, file)
                        GameVars.GAMESTATE = GameStates.GAMEOVER
                    elif event.key == pygame.K_BACKSPACE:
                        GameVars.SCORES[GameVars.PLAYERPLACE - 1][0] = GameVars.SCORES[GameVars.PLAYERPLACE - 1][0][:-1]
                    else:
                        if GameVars.SCORES[GameVars.PLAYERPLACE - 1][0]== '-----':
                            GameVars.SCORES[GameVars.PLAYERPLACE - 1][0] = ''
                        if len(GameVars.SCORES[GameVars.PLAYERPLACE - 1][0]) < 5:
                             GameVars.SCORES[GameVars.PLAYERPLACE - 1][0] += event.unicode

        if len(es) == 0 and not ball.isAlive and GameVars.GAMESTATE == GameStates.PLAY:
            GameVars.LIVES -= 1
            if GameVars.LIVES >0:
                GameVars.GAMESTATE =GameStates.SERVE
                ball.isAlive = True
            else:  
                GameVars.GAMESTATE = GameStates.GAMEOVER

            board.rect.x = (playingarea['w'] - playingarea['x']) // 2 - board.rect.width // 2
            board.rect.y = playingarea['y'] + playingarea['h']
            board.speed = 0
            ball.rect.y = board.rect.y - board.rect.height - 100
            ball.rect.x = board.rect.x + board.rect.width // 2 - ball.rect.width // 2

        elif GameVars.GAMESTATE == GameStates.LEVELUP:
            board.rect.x = (playingarea['w'] - playingarea['x']) // 2 - board.rect.width // 2
            board.rect.y = playingarea['y'] + playingarea['h']
            board.speed = 0
            ball.xspeed = ball.yspeed = 0
            ball.rect.y = board.rect.y - board.rect.height
            ball.rect.x = board.rect.x + board.rect.width // 2 - ball.rect.width // 2
            Bricks = []
            if ammo.isAlive: ammo.isAlive = False
            if bomb.isAlive: bomb.isAlive = False
            AllGifts = [] 
        elif GameVars.GAMESTATE == GameStates.SERVE and (ball.rect.y != board.rect.y - board.rect.height - 100 or
                                                ball.rect.x != board.rect.x + board.rect.width // 2 - ball.rect.width // 2):
            ball.rect.y = board.rect.y - board.rect.height - 100
            ball.rect.x = board.rect.x + board.rect.width // 2 - ball.rect.width // 2  
        elif GameVars.GAMESTATE == GameStates.GAMEWON or GameVars.GAMESTATE == GameStates.GAMEOVER:
            if not GameVars.ISSCORECHECKED:
                scores = GameVars.SCORES
                if len(scores) == 5: scores.append(['-----', GameVars.SCORE, GameVars.LEVEL])
                # do a bubble sort
                for i in range(len(scores) - 1):
                    for j in range(len(scores) - i - 1):
                        if scores[j][1] < scores[j+1][1]:
                            scores[j], scores[j+1] = scores[j+1], scores[j]
                for s in range(len(scores)):
                    if scores[s][1] == GameVars.SCORE and scores[s][0] == '-----':
                        GameVars.PLAYERPLACE = s + 1
                        break
                if GameVars.PLAYERPLACE < 6: GameVars.GAMESTATE = GameStates.PLAYERHIGHSCORED
                GameVars.SCORES = scores[:5]
                GameVars.ISSCORECHECKED = True
                with open(find_data_file('scores.dat'), 'wb') as file: pickle.dump(GameVars.SCORES, file)
        else:
            if pygame.time.get_ticks() - GameVars.GIFTTIME > 600: GameVars.ISGIFTAVAIL = True
        
        setScreen()
        pygame.display.flip()
        fpsClock.tick(fps) 

if __name__ == '__main__': main()
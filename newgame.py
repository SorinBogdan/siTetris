# WS2812 LED Matrix Gamecontrol (Tetris, Snake, Pong)
# by M Oehler
# https://hackaday.io/project/11064-raspberry-pi-retro-gaming-led-display
# ported from
# Tetromino (a Tetris clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import re
import time
import argparse
import pdb

from luma.led_matrix.device import max7219
from luma.core.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT

import RPi.GPIO as GPIO

import random, time, sys, socket, os

# If Pi = False the script runs in simulation mode using pygame lib
PI = True
DEBUG = False

BOARDWIDTH = 8
BOARDHEIGHT = 16
BLANK = '.'
MOVESIDEWAYSFREQ = 0.15
MOVEDOWNFREQ = 0.15
FALLING_SPEED = 0.4


SCORES =(0,40,100,300,1200)


TEMPLATEWIDTH = 5
TEMPLATEHEIGHT = 5


S_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '..OO.',
                     '.OO..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '...O.',
                     '.....']]

Z_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '.O...',
                     '.....']]

I_SHAPE_TEMPLATE = [['..O..',
                     '..O..',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     'OOOO.',
                     '.....',
                     '.....']]

O_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '.OO..',
                     '.....']]

J_SHAPE_TEMPLATE = [['.....',
                     '.O...',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..OO.',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '...O.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '.OO..',
                     '.....']]

L_SHAPE_TEMPLATE = [['.....',
                     '...O.',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '.O...',
                     '.....'],
                    ['.....',
                     '.OO..',
                     '..O..',
                     '..O..',
                     '.....']]

T_SHAPE_TEMPLATE = [['.....',
                     '..O..',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '..O..',
                     '.....']]

PIECES = {'S': S_SHAPE_TEMPLATE,
          'Z': Z_SHAPE_TEMPLATE,
          'I': I_SHAPE_TEMPLATE,
          'J': J_SHAPE_TEMPLATE,
          'L': L_SHAPE_TEMPLATE,
          'O': O_SHAPE_TEMPLATE,
          'T': T_SHAPE_TEMPLATE}

PIECES_ORDER = {'S': 0,'Z': 1,'I': 2,'J': 3,'L': 4,'O': 5,'T': 6}


n=2
block_orientation=90
# serial port pi #
# create matrix device
serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=n or 1, block_orientation=block_orientation)
#device = max7219(serial, width=BOARDWIDTH, height=BOARDHEIGHT)
print("Created device")

# key server for controller #

QKEYDOWN=0
QKEYUP=1
#myQueue = queue.Queue()
mask = bytearray([1,2,4,8,16,32,64,128])

#owm = pyowm.OWM('81a8e406e1e5466fddb0c7bbfc979a6b')

#class qEvent:
 #  def __init__(self, key, type):
  #      self.key = key
   #     self.type = type


# main #

def main():

    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT
    global a1_counter ,RUNNING
    a1_counter=0
    RUNNING=True

    #device.brightness(1)
    #device.show_message("Waiting for controller...", font=proportional(CP437_FONT),delay=0.015)

    # Port 0 means to select an arbitrary unused port

    HOST, PORT = '', 4711

    #drawClock(1)
    #device.show_message("Let's play", font=proportional(CP437_FONT),delay=0.03)

    while True:
        #msg = "Game is loading"
        #print(msg)
        #show_message(device, msg, fill="white", font=proportional(CP437_FONT))
        with canvas(device) as draw:
            draw.point( (0,0),1)
        time.sleep(1)
        #clearScreen()
        #drawSymbols()
        initButtons()
        
        runTetrisGame()
    terminate()

# gaming main routines #
def runTetrisGame():
    board = getBlankBoard()
    #for i in range (BOARDWIDTH):
    #        board[BOARDHEIGHT-1][i]=1
    #        board[BOARDHEIGHT-2][i]=1
    #print(board)
    lastMoveDownTime = time.time()
    lastMoveSidewaysTime = time.time()
    lastFallTime = time.time()
    movingDown = False # note: there is no movingUp variable
    movingLeft = False
    movingRight = False
    score = 0
    oldscore = -1
    oldpiece = 10
    lines = 0
    level, fallFreq = calculateLevelAndFallFreq(lines)

    fallingPiece = getNewPiece()
    print(fallingPiece)
    nextPiece = getNewPiece()


    while True: # game loop

        #if not myQueue.empty():
        #    print(myQueue.get().type)

        if fallingPiece == None:
            # No falling piece in play, so start a new piece at the top
            fallingPiece = nextPiece
            nextPiece = getNewPiece()
            lastFallTime = time.time() # reset lastFallTime

            if not isValidPosition(board, fallingPiece):
                print(fallingPiece)
                time.sleep(2)
                return # can't fit a new piece on the board, so game over

        pressedButton = getPressedButton() 
        if (pressedButton==BTN_LEFT and isValidPosition(board, fallingPiece, adjX=1) and not movingLeft):
            #fallingPiece['y'] += 1
            movingLeft = True
            movingRight = False
            lastMoveSidewaysTime = time.time()
        elif (pressedButton==BTN_RIGHT and isValidPosition(board, fallingPiece, adjX=-1) and not movingRight):
            #fallingPiece['y'] -= 1
            movingRight = True
            movingLeft = False
            lastMoveSidewaysTime = time.time()
        elif (pressedButton==BTN_ROTATE):
            fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(PIECES[fallingPiece['shape']])
            if not isValidPosition(board, fallingPiece):
                fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(PIECES[fallingPiece['shape']])
                
# handle moving the piece because of user input
        if (movingLeft or movingRight) and time.time() - lastMoveSidewaysTime > MOVESIDEWAYSFREQ:
            if movingLeft and isValidPosition(board, fallingPiece, adjX=1):
                fallingPiece['y'] += 1
            elif movingRight and isValidPosition(board, fallingPiece, adjX=-1):
                fallingPiece['y'] -= 1
            lastMoveSidewaysTime = time.time()
            movingLeft=False
            movingRight=False

        # let the piece fall if it is time to fall
        if time.time() - lastFallTime > fallFreq:
            # see if the piece has landed
            if not isValidPosition(board, fallingPiece, adjY=1):
                # falling piece has landed, set it on the board
                addToBoard(board, fallingPiece)
                print("added to board")
                remLine = removeCompleteLines(board)
                # count lines for level calculation
                lines += remLine
                # more lines, more points per line
                score += SCORES[remLine]*level
                level, fallFreq = calculateLevelAndFallFreq(lines)
                fallingPiece = None
                
            else:
                # piece did not land, just move the piece down
                fallingPiece['x'] += 1
                lastFallTime = time.time()
                
        drawBoard(board)

        if fallingPiece != None:
            drawPiece(fallingPiece)
        #time.sleep(.05)


# buttons logic #
BTN_LEFT    = 26
BTN_RIGHT   = 13
BTN_ROTATE  = 19
BTN_NOBUTTON= 0

def initButtons():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BTN_LEFT,GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BTN_RIGHT,GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BTN_ROTATE,GPIO.IN, pull_up_down=GPIO.PUD_UP)

def getPressedButton():
    if GPIO.input(BTN_LEFT)==False:
        return BTN_LEFT
    elif GPIO.input(BTN_RIGHT)==False:
        return BTN_RIGHT
    elif GPIO.input(BTN_ROTATE)==False:
        return BTN_ROTATE
    else:
        return BTN_NOBUTTON

# drawing #
def scrollText(text):
    if PI:
        device.show_message(text, font=proportional(CP437_FONT))
    else:
        titleSurf, titleRect = makeTextObjs(str(text), BASICFONT, TEXTCOLOR)
        titleRect.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 3)
        DISPLAYSURF.blit(titleSurf, titleRect)



def scoreTetris(score,level,nextpiece):
    if PI:
        device.clear()
    _score=score
    if _score>999999:
        _score = 999999

    # one point per level
    for i in range(0,level):
        drawScorePixel(i*2,7,1)

    # score as 6 digit value
    for i in range(0,6):
        drawnumberMAX7219(_score%10,i*4,0)
        _score //=10

    # draw next piece
    drawTetrisMAX7219(nextpiece,27,0)

    if PI:
        device.flush()


# program flow #

def terminate():
    RUNNING = False
    if not PI:
        pygame.quit()
    sys.exit()

def checkForQuit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back

# tetris subroutines #

def calculateLevelAndFallFreq(lines):
    # Based on the score, return the level the player is on and
    # how many seconds pass until a falling piece falls one space.
    level = int(lines / 10) + 1
    # limit level to 10
    if level >10:
        level = 10
    fallFreq = FALLING_SPEED - (level * 0.05)
    if fallFreq <= 0.05:
        fallFreq = 0.05
    return level, fallFreq

def getNewPiece():
    # return a random new piece in a random rotation and color
    shape = random.choice(list(PIECES.keys()))
    newPiece = {'shape': shape,
                'rotation': random.randint(0, len(PIECES[shape]) - 1),
                'y': int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2),
                'x': -2, # start it above the board (i.e. less than 0)
                'color': 1}
    return newPiece

def addToBoard(board, piece):
    # fill in the board based on piece's location, shape, and rotation
    for x in range(TEMPLATEHEIGHT):
        for y in range(TEMPLATEWIDTH):
            if PIECES[piece['shape']][piece['rotation']][x][y] != BLANK:
                board[(TEMPLATEHEIGHT-1-x) + piece['x']][(TEMPLATEWIDTH-1-y) + piece['y']] = piece['color']

def isOnBoard(x, y):
    return x >= 0 and x < BOARDWIDTH and y < BOARDHEIGHT and y>=0

def isValidPosition(board, piece, adjX=0, adjY=0):
    # Return True if the piece is within the board and not colliding
    #pdb.set_trace()
    for x in range(TEMPLATEHEIGHT):
        for y in range(TEMPLATEWIDTH):
            isAboveBoard = (TEMPLATEHEIGHT-1-x) + piece['x'] + adjY < 0
            
            if isAboveBoard or PIECES[piece['shape']][piece['rotation']][x][y] == BLANK:
                continue
            if not isOnBoard((TEMPLATEWIDTH-1-y) + piece['y'] + adjX, (TEMPLATEHEIGHT-1-x) + piece['x'] + adjY):
                print("is not on board")
                return False
            if board[(TEMPLATEHEIGHT-1-x) + piece['x'] + adjY][(TEMPLATEWIDTH-1-y) + piece['y'] + adjX] != BLANK:
                print("is not blank")
                return False
    return True

def isCompleteLine(board, y):
    # Return True if the line filled with boxes with no gaps.
    for x in range(BOARDWIDTH):
        if board[y][x] == BLANK:
            return False
    return True

def removeCompleteLines(board):
    # Remove any completed lines on the board, move everything above them down, and return the number of complete lines.
    numLinesRemoved = 0
    y = BOARDHEIGHT - 1 # start y at the bottom of the board
    while y >= 0:
        if isCompleteLine(board, y):
            # Remove the line and pull boxes down by one line.
            for pullDownY in range(y, 0, -1):
                for x in range(BOARDWIDTH):
                    board[pullDownY][x] = board[pullDownY-1][x]
            # Set very top line to blank.
            for x in range(BOARDWIDTH):
                board[0][x] = BLANK
            numLinesRemoved += 1
            # Note on the next iteration of the loop, y is the same.
            # This is so that if the line that was pulled down is also
            # complete, it will be removed.
        else:
            y -= 1 # move on to check next row up
    return numLinesRemoved

def drawBoard(matrix):
    with canvas(device) as draw:
        for i in range(0,BOARDHEIGHT):
            for j in range(0,BOARDWIDTH):
                if(matrix[i][j]!=BLANK):
                    draw.point((i,j),fill="white")
            #drawPixel(i,j,matrix[i][j])

def getBlankBoard():
    # create and return a new blank board data structure
    board = []
    for i in range(BOARDHEIGHT):
        board.append([BLANK] * BOARDWIDTH)
    return board

def drawPiece(piece, pixelx=None, pixely=None):
    shapeToDraw = PIECES[piece['shape']][piece['rotation']]
    if pixelx == None and pixely == None:
        # if pixelx & pixely hasn't been specified, use the location stored in the piece data structure
        pixelx=piece['x']
        pixely=piece['y']
    #print(pixelx,pixely)
    # draw each of the boxes that make up the piece
    with canvas(device) as draw:
        for x in range(TEMPLATEHEIGHT):
            for y in range(TEMPLATEWIDTH):
                if shapeToDraw[x][y] != BLANK:
                    draw.point( (pixelx+(TEMPLATEHEIGHT-1-x),pixely+(TEMPLATEWIDTH-1-y)), piece['color'])

if __name__ == '__main__':
    main()


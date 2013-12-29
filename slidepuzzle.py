#!/usr/bin/env python
# coding=utf-8

# Slide Puzzle
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Modded by brk0_0
# Creative Commons BY-NC-SA 3.0 US

import random
import sys
import pygame
from pygame.locals import *

# Constants
BOARDWIDTH = 3 # Number of rows in the board
BOARDHEIGHT = 3 # Number of columns in the board
TILESIZE = 80 
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FPS = 30
BLANK = None
SHUFMOVES = 80 # Number of moves when shuffling the board

# Colors           R    G    B
BLACK         = (  0,   0,   0)
WHITE         = (255, 255, 255)
BRIGHTBLUE    = (  0,  50, 255)
DARKTURQUOISE = (  3,  54,  73)
GREEN         = (  0, 255,   0)

BGCOLOR = DARKTURQUOISE
TILECOLOR = GREEN
TEXTCOLOR = WHITE
BORDERCOLOR = BRIGHTBLUE
BUTTONCOLOR = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = WHITE
BASICFONTSIZE = 20

XMARGIN = int((WINDOWWIDTH - (TILESIZE * BOARDWIDTH + (BOARDWIDTH - 1))) / 2)
YMARGIN = int((WINDOWHEIGHT - (TILESIZE * BOARDHEIGHT + (BOARDHEIGHT - 1))) / 2)

UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"

def main():
	# Global variables
	global FPSCLOCK, DISPLAYSURF, BASICFONT, RESET_SURF, RESET_RECT, NEW_SURF, NEW_RECT, SOLVE_SURF, SOLVE_RECT

	# Initiate PyGame and set primary variables
	pygame.init()
	FPSCLOCK = pygame.time.Clock()
	DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
	pygame.display.set_caption("Slide Puzzle")
	BASICFONT = pygame.font.Font("freesansbold.ttf", BASICFONTSIZE)

	# Store the option buttons and their rectangles in OPTIONS
	RESET_SURF, RESET_RECT = makeText("Reset", TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 90) 
	NEW_SURF  , NEW_RECT   = makeText("New Game", TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 60)
	SOLVE_SURF, SOLVE_RECT = makeText("Solve", TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 30)

	mainBoard, solutionSeq = generateNewPuzzle(SHUFMOVES)
	SOLVEDBOARD = getStartingBoard() # A solved board is the same as the board in start state, before shuffling
	allMoves = [] # List of moves made from the shuffled configuration
	message = "" # Contains the message displayed on the upper left corner

	# Main game loop
	while True:
		slideTo = None # The direction, if any, a tile should slide

		if mainBoard == SOLVEDBOARD:
			if message != "The Board is Already Solved!":
				message = "Solved!"
			allMoves = []
			solutionSeq = []
		else:
			message = "Click tile or press arrow keys to slide"

		drawBoard(mainBoard, message) # Draw the board to the screen
		checkForQuit() # Check for quit-like events and quit if any

		# Event handling loop
		for event in pygame.event.get():
			if event.type == MOUSEBUTTONUP: # If the event is a mouse click
				spotx, spoty = getSpotClicked(mainBoard, event.pos[0], event.pos[1])

				# If the player missed a tile, check if an option button was clicked
				if (spotx, spoty) == (None, None):
					# Clicked on RESET button
					if RESET_RECT.collidepoint(event.pos):
						resetAnimation(mainBoard, allMoves)
						allMoves = []
					# Clicked on NEW GAME button
					elif NEW_RECT.collidepoint(event.pos):
						mainBoard, solutionSeq = generateNewPuzzle(SHUFMOVES)
						allMoves = []
						message = ""
					# Clicked on SOLVE button
					elif SOLVE_RECT.collidepoint(event.pos):
						if mainBoard == SOLVEDBOARD:
							message = "The Board is Already Solved!"
						else:
							resetAnimation(mainBoard, solutionSeq + allMoves)
							solutionSeq = []
							allMoves = []
				# Else, check if the clicked tile was next to the blank spot
				else:
					blankx, blanky = getBlankPosition(mainBoard) # Get the blank spot's coordinates

					# Set the tile to move to the right direction
					if spotx == blankx + 1 and spoty == blanky:
						slideTo = LEFT
					elif spotx == blankx - 1 and spoty == blanky:
						slideTo = RIGHT
					elif spotx == blankx and spoty == blanky + 1:
						slideTo = UP
					elif spotx == blankx and spoty == blanky - 1:
						slideTo = DOWN


			elif event.type == KEYUP: # If the event is a key press
				if event.key in (K_LEFT, K_a) and isValidMove(mainBoard, LEFT):
					slideTo = LEFT
				elif event.key in (K_RIGHT, K_d) and isValidMove(mainBoard, RIGHT):
					slideTo = RIGHT
				elif event.key in (K_UP, K_w) and isValidMove(mainBoard, UP):
					slideTo = UP
				elif event.key in (K_DOWN, K_s) and isValidMove(mainBoard, DOWN):
					slideTo = DOWN
		
		# If a tile should be moved
		if slideTo:
			slideAnimation(mainBoard, slideTo, "Click tile or press arrow keys to slide", 8)
			makeMove(mainBoard, slideTo)
			allMoves.append(slideTo)

		# Update the display and wait for the clock to tick
		pygame.display.update()
		FPSCLOCK.tick(FPS)

def terminate():
	pygame.quit() # Quit PyGame
	sys.exit() # Exit program

def checkForQuit():
	for event in pygame.event.get(QUIT): # Get all QUIT events
		terminate() # End the game if there are any QUIT events
	for event in pygame.event.get(KEYUP): # Get all KEYUP events
		# If K_ESCAPE was pressed, terminate
		if event.key == K_ESCAPE:
			terminate()
		# Else, puts the event back in the list of events
		pygame.event.post(event)

def oppositeMove(move):
	if move == UP:
		return DOWN
	elif move == DOWN:
		return UP
	elif move == LEFT:
		return RIGHT
	elif move == RIGHT:
		return LEFT

def isValidMove(board, move):
	blankx, blanky = getBlankPosition(board)

	return (move == UP and blanky != len(board[0]) - 1) or \
	       (move == DOWN and blanky != 0) or \
	       (move == LEFT and blankx != len(board) - 1) or \
	       (move == RIGHT and blankx != 0)

def makeMove(board, move):
	blankx, blanky = getBlankPosition(board)

	if move == UP:
		board[blankx][blanky], board[blankx][blanky + 1] = board[blankx][blanky + 1], board[blankx][blanky]
	elif move == DOWN:
		board[blankx][blanky], board[blankx][blanky - 1] = board[blankx][blanky - 1], board[blankx][blanky]
	elif move == LEFT:
		board[blankx][blanky], board[blankx + 1][blanky] = board[blankx + 1][blanky], board[blankx][blanky]
	elif move == RIGHT:
		board[blankx][blanky], board[blankx - 1][blanky] = board[blankx - 1][blanky], board[blankx][blanky]

def getStartingBoard():
	# Return a board data structure with tiles in the solved state
	counter = 1
	board = []

	# Build the board
	for x in range(BOARDWIDTH):
		column = []
		for y in range(BOARDHEIGHT):
			column.append(counter)
			counter += BOARDWIDTH
		board.append(column)
		counter -= BOARDWIDTH * (BOARDHEIGHT - 1) + BOARDWIDTH - 1
	board[BOARDWIDTH - 1][BOARDHEIGHT - 1] = BLANK

	return board

def getBlankPosition(board):
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT):
			if board[x][y] == BLANK:
				return (x, y)

def getRandomMove(board, lastMove=None):
	allMoves = [UP, DOWN, LEFT, RIGHT]
	validMoves = []

	# Delete invalid moves from the list
	for move in allMoves:
		if move != oppositeMove(lastMove) and isValidMove(board, move):
			validMoves.append(move)

	# Return a random valid move
	return random.choice(validMoves)

def getLeftTopOfTile(tileX, tileY):
	left = XMARGIN + (tileX * TILESIZE) + (tileX - 1)
	top = YMARGIN + (tileY * TILESIZE) + (tileY - 1)

	return left, top

def getSpotClicked(board, x, y):
	# Go through the board checking if any tile collides with the (x,y) point
	for tileX in range(len(board)):
		for tileY in range(len(board[0])):
			left, top = getLeftTopOfTile(tileX, tileY)
			tileRect = pygame.Rect(left, top, TILESIZE, TILESIZE)
			# If collides, returns the coordinates of that tile
			if tileRect.collidepoint(x, y):
				return (tileX, tileY)

	# If none matched
	return (None, None)

def drawTile(tileX, tileY, number, adjx=0, adjy=0):
	left, top = getLeftTopOfTile(tileX, tileY) # Get left/top coordinates of the tile
	tileRect = pygame.draw.rect(DISPLAYSURF, TILECOLOR, (left + adjx, top + adjy, TILESIZE, TILESIZE)) # Draw the main rectangle
	textSurf = BASICFONT.render(str(number), True, TEXTCOLOR) # Create a text surface with the the number written on
	textRect = textSurf.get_rect() # Get the text surface's rectange
	textRect.center = left + int(TILESIZE / 2) + adjx, top + int(TILESIZE / 2) + adjy # Change the text surface's center
	DISPLAYSURF.blit(textSurf, textRect) # Blit the text surface on DISPLAYSURF

def drawBoard(board, message):
	# Fill the display with background color
	DISPLAYSURF.fill(BGCOLOR)

	# Display message, if any
	if message:
		textSurf, textRect = makeText(message, MESSAGECOLOR, BGCOLOR, 5, 5)
		DISPLAYSURF.blit(textSurf, textRect)

	# Display the tiles, one by one
	for tileX in range(len(board)):
		for tileY in range(len(board[0])):
			if board[tileX][tileY] != BLANK:
				drawTile(tileX, tileY, board[tileX][tileY])

	# Display the border
	left, top = getLeftTopOfTile(0,0)
	width = BOARDWIDTH * TILESIZE
	height = BOARDHEIGHT * TILESIZE
	pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left - 5, top - 5, width + 11, height + 11), 4)

	# Display the buttons
	DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
	DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
	DISPLAYSURF.blit(SOLVE_SURF, SOLVE_RECT)

def makeText(text, color, bgcolor, top, left):
	textSurf = BASICFONT.render(text, True, color, bgcolor) # Create a text surface with the the number written on
	textRect = textSurf.get_rect() # Get the text surface's rectange
	textRect.topleft = (top, left) # Change the text surface's center
	return (textSurf, textRect)

def slideAnimation(board, direction, message, animationSpeed):
	blankx, blanky = getBlankPosition(board)

	if direction == UP:
		movex, movey = blankx, blanky + 1
	elif direction == DOWN:
		movex, movey = blankx, blanky - 1
	elif direction == LEFT:
		movex, movey = blankx + 1, blanky
	elif direction == RIGHT:
		movex, movey = blankx - 1, blanky

	# Prepare the base surface	
	drawBoard(board, message)
	baseSurf = DISPLAYSURF.copy()

	# Delete the moving tile from the baseSurf surface
	moveLeft, moveTop = getLeftTopOfTile(movex, movey)
	pygame.draw.rect(baseSurf, BGCOLOR, (moveLeft, moveTop, TILESIZE, TILESIZE))

	for i in range(0, TILESIZE, animationSpeed):
		# Animate the tile sliding over
		checkForQuit()
		DISPLAYSURF.blit(baseSurf, (0,0))

		if direction == UP:
			drawTile(movex, movey, board[movex][movey], 0, -i)
		elif direction == DOWN:
			drawTile(movex, movey, board[movex][movey], 0, i)
		elif direction == LEFT:
			drawTile(movex, movey, board[movex][movey], -i, 0)
		elif direction == RIGHT:
			drawTile(movex, movey, board[movex][movey], i, 0)

		pygame.display.update()
		FPSCLOCK.tick(FPS)

def resetAnimation(board, allMoves):
	revAllMoves = allMoves[::-1] # Get a reversed list of moves

	for move in revAllMoves:
		checkForQuit()
		opposite = oppositeMove(move)
		slideAnimation(board, opposite, "", int(TILESIZE / 2))
		makeMove(board, opposite)

def generateNewPuzzle(numSlides):
	sequence = []
	board = getStartingBoard()
	drawBoard = (board, None)
	pygame.display.update()
	pygame.time.wait(500)
	lastMove = None

	for i in range(numSlides):
		move = getRandomMove(board, lastMove)
		slideAnimation(board, move, "Generating New Puzzle...", int(TILESIZE / 2))
		makeMove(board, move)
		sequence.append(move)
		lastMove = move

	return (board, sequence)

if __name__ == "__main__":
	main()

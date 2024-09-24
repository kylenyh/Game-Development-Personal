import pygame
import random
import time

pygame.init()

# game window dimensions and title
w_width = 800
w_height = 800
window = pygame.display.set_mode((w_width, w_height))
pygame.display.set_caption("Snake Game")
grid_size = 10

# color variables
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)
yellow = (255, 255, 0)
cyan = (0, 255, 255)

# snake coordinates and snake velocity
snake_x, snake_y = 200, 200
d_x, d_y = 10, 0 

# randomnized apple coordinates through the randint function
apple_x, apple_y = random.randint(0, (500//10))*10, random.randint(0, (500//10))*10

# body of the snake 
snake_body = [(snake_x, snake_y)]

clock = pygame.time.Clock()

# game over condition initially set as false when game is running
game_over = False

# font size of score text
font = pygame.font.SysFont("italic", 50)

grid_size = 100//10 # grid size of one square in the grid, 1 unit in game 
b = 800//10 # boundaries of game window 
l = b - 1 # boundaries of game window 

pygame.display.update()
    
# Snake class implementation    
class Snake:
    def __init__(self, w_width, w_height): 
        self.body = [[200,200]] # list of (x,y) coordinate pairs
        self.headX = 200 # x coordinate of snake's head 
        self.headY = 200 # y coordinate of snake's head 
        self.d_x = 10 # snake velocity in x direction
        self.d_y = 0 # snake velocity in y direction
        self.width = w_width # width parameter
        self.height = w_height # height parameter
        
    def changeDirection(self, direction): # direction method and conditions created to enable the snake to move in a different direction
        if direction == 'up': # snake upward direction 
            self.d_x = 0 
            self.d_y = -10
        elif direction == 'down': # snake downward direction 
            self.d_x = 0
            self.d_y = 10
        elif direction == 'left': # snake left direction 
            self.d_x = -10
            self.d_y = 0
        elif direction == 'right': # snake right direction 
            self.d_x = 10
            self.d_y = 0
        
    def normalMove(self): # movement method and the conditions created for its head coordinates allows the snake to move through walls
        self.headX = (self.headX + self.d_x) % self.width # % allows snake to move through walls horizontally
        self.headY = (self.headY + self.d_y) % self.height # % allows snake to move through walls vertically
        newHeadPos = [self.headX, self.headY] # new head position variable storing coordinates of snake's head 
        self.body.insert(0, newHeadPos) # new head position is added to snake's body
        self.body.pop(-1) # previous head position is removed from snake's body
        return self.body
    
    def grow(self):
        self.headX = (self.headX + self.d_x) % self.width # snake's head in x coordinate is able to move through the walls 
        self.headY = (self.headY + self.d_y) % self.height # snake's head in y coordinate is able to move through the walls 
        newHeadPos = [self.headX, self.headY] # head position of snake is defined 
        self.body.insert(0, newHeadPos) # new head position of snake is added to the snake body
        return self.body
    
    def getHead(self): # returns head position of the snake 
        return [self.headX, self.headY]
    
    def checkCollision(self): # collision detection condition that returns true if the snake's head collides with its body
        if [self.headX, self.headY] in self.body[1:]:
            return True
        else:
            return False
    
# Apple class implementation     
class Apple:
    def __init__(self):
        self.x = random.randint(0, (500//10))*10 # randomnized x coordinate of apple's position in given range on the grid
        self.y = random.randint(0, (500//10))*10 # randomnized y coordinate of apple's position in given range on the grid
        self.rect = pygame.Rect(200, 200, grid_size, grid_size) # object variable to draw the apple eventually

    def repositon(self): # setting the randomnized position (x, y) of the apple through the reposition method
        self.x = random.randint(0, (500//10))*10 # randomnized x coordinate of apple's position in given range on the grid
        self.y = random.randint(0, (500//10))*10 # randomnized y coordinate of apple's position in given range on the grid
        
    def getPosition(self): # returns the randomnized position of the apple
        return [self.x, self.y]

# In game-grid function
def drawGrid(): # Setting the grid in the horizontal and vertical direction
    window.fill((0, 0, 0))
    for i in range(0, 800, 10): # horizontal grid lines 
        pygame.draw.line(window, cyan, (0, i), (800, i), 1)
        for i in range(0, 800, 10): # vertical grid lines
            pygame.draw.line(window, cyan, (i, 0), (i, 800), 1)

# Scoreboard function
def drawScore():
    global score
    scoreText = font.render("Score: " + str(score),  True, (255, 255, 255)) # score text display
    window.blit(scoreText, [0, 0])
        
score = 0 # original score 
pygame.display.update()
snake = Snake(w_width, w_height)
snakedir = 'right' # default direction of snake's movement
apple = Apple()

pygame.display.update()

while True:
    if (game_over): # running over the game condition 
        window.fill((0, 0, 0))
        msg = font.render("GAME OVER!", True, yellow)
        window.blit(msg, [50, 50]) # game over message is displayed 
        pygame.display.update()
        pygame.quit()
        quit()
    events = pygame.event.get() # game loops through all events 
    for event in events:
        if (event.type == pygame.QUIT): 
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN: # pygame key press in built functions
                if event.key == pygame.K_LEFT:
                    if snakedir != 'right':
                        snakedir = 'left'
                        snake.changeDirection('left') # snake moves in left direction
                elif event.key == pygame.K_RIGHT:
                    if snakedir != 'left':
                        snakedir = 'right'
                        snake.changeDirection('right') # snake moves in right direction
                elif event.key == pygame.K_UP:
                    if snakedir != 'down':
                        snakedir = 'up'
                        snake.changeDirection('up') # snake moves in up direction
                elif event.key == pygame.K_DOWN:
                    if snakedir != 'up':
                        snakedir = 'down'
                        snake.changeDirection('down') # snake moves in down direction
                else:
                    continue

    drawGrid() # recalling the grid function
    drawScore() # recalling the score board function
    
    snakeHeadPos = snake.getHead() # calling to get the head function from the snake class to return it
    applePos = apple.getPosition() # calling to get apple position function from the apple class to return it
    
    # condition checking whether if the snake's head collides with the apple, affecting the snake's growth and the score addition
    if (snakeHeadPos == applePos):
        snakeBodyList = snake.grow()
        score += 1
        apple.repositon()
    else:
        snakeBodyList = snake.normalMove()
    
    # drawing the snake in the game
    for block in snakeBodyList:
        rect = pygame.Rect(block[0], block[1], 10, 10)
        pygame.draw.rect(window, green, rect)
    
    # checks whether the conditions of the snake collision is satisfied and if so, the game ends 
    snakeCollision = snake.checkCollision()
    if snakeCollision:
        game_over = True
        continue

    # drawing the apple in the game
    rect = pygame.Rect(applePos[0], applePos[1], 10, 10) 
    pygame.draw.rect(window, red, rect)
    
    pygame.display.update()
    
    clock.tick(300)

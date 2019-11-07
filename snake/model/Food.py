import pygame
from random import randrange
from snake.model.GameBoard import GameBoard
from snake.model.Snake import Snake

class Food:
    red = (219, 58, 52)
    def __init__(self):
        self.foodPosX = randrange(0, GameBoard.width, Snake.size)
        self.foodPosY = randrange(0, GameBoard.height, Snake.size)
        self.foodColor = Food.red

    def drawFood(self, surface):
        pygame.draw.rect(surface, self.foodColor, [self.foodPosX, self.foodPosY, Snake.size, Snake.size])

    def generateNewFood(self):
        self.foodPosX = randrange(0, GameBoard.width, Snake.size)
        self.foodPosY = randrange(0, GameBoard.height, Snake.size)

    def getFoodPosition(self):
        return (self.foodPosX, self.foodPosY)
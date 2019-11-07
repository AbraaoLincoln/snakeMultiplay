import pygame

from snake.model.Snake import Snake
from snake.model.GameBoard import GameBoard
from snake.model.Food import Food

class GameManeger:

    #Construtor
    def __init__(self, surface):
        self.snakeInGame = []
        self.foodsInGame = []
        self.food = Food()
        self.foodsInGame.append(self.food)
        self.gameSurface = surface

    #Adiciona uma nova snake no jogo
    def addSnakeInGame(self, newSnake):
        # self.snakeInGame.append(newSnake)
        # return len(self.snakeInGame) - 1
        #print("add snake")
        if len(self.snakeInGame) > 0:
            for i in range(len(self.snakeInGame)):
                if self.snakeInGame[i] == None:
                    self.snakeInGame[i] = newSnake
                    #print("add snake if")
                    return i
            #print("add snake if 2")
            self.snakeInGame.append(newSnake)
            return len(self.snakeInGame) - 1
        else:
            #print("add snake else")
            self.snakeInGame.append(newSnake)
            return 0 #len(self.snakeInGame) - 1

    #Deleta snake do jogo
    def romoveSnakeOnGame(self, snakeId):
        # del self.snakeInGame[idSnake]
        self.snakeInGame[snakeId] = None
        print(self.snakeInGame[snakeId])

    #Metodo usado para mandar comandos para a snake
    #Este metodo é usado no modo single play do jogo.
    def commandToSnake(self, userInput, idSnake):
        if userInput.type == pygame.KEYDOWN:
            if userInput.key == pygame.K_UP and self.snakeInGame[idSnake].getSpeedY() != Snake.size:
                self.snakeInGame[idSnake].incrementSpeedY(-Snake.size)
                self.snakeInGame[idSnake].incrementSpeedX(0)
            elif userInput.key == pygame.K_DOWN and self.snakeInGame[idSnake].getSpeedY() != -Snake.size:
                self.snakeInGame[idSnake].incrementSpeedY(Snake.size)
                self.snakeInGame[idSnake].incrementSpeedX(0)
            elif userInput.key == pygame.K_RIGHT and self.snakeInGame[idSnake].getSpeedX() != -Snake.size:
                self.snakeInGame[idSnake].incrementSpeedY(0)
                self.snakeInGame[idSnake].incrementSpeedX(Snake.size)
            elif userInput.key == pygame.K_LEFT and self.snakeInGame[idSnake].getSpeedX() != Snake.size:
                self.snakeInGame[idSnake].incrementSpeedY(0)
                self.snakeInGame[idSnake].incrementSpeedX(-Snake.size)

    #Atualiza a diecao que snake esta indo.
    def userCommand(self, userInput, idSnake):
        if userInput == pygame.K_UP and self.snakeInGame[idSnake].getSpeedY() != Snake.size:
            self.snakeInGame[idSnake].incrementSpeedY(-Snake.size)
            self.snakeInGame[idSnake].incrementSpeedX(0)
        elif userInput == pygame.K_DOWN and self.snakeInGame[idSnake].getSpeedY() != -Snake.size:
            self.snakeInGame[idSnake].incrementSpeedY(Snake.size)
            self.snakeInGame[idSnake].incrementSpeedX(0)
        elif userInput == pygame.K_RIGHT and self.snakeInGame[idSnake].getSpeedX() != -Snake.size:
            self.snakeInGame[idSnake].incrementSpeedY(0)
            self.snakeInGame[idSnake].incrementSpeedX(Snake.size)
        elif userInput == pygame.K_LEFT and self.snakeInGame[idSnake].getSpeedX() != Snake.size:
            self.snakeInGame[idSnake].incrementSpeedY(0)
            self.snakeInGame[idSnake].incrementSpeedX(-Snake.size)

    #Desennha as snakes na suas novas posições
    # def moveSnakes(self, surface):
    #     for snake in self.snakeInGame:
    #         snakeHead = snake.getHaedSnake()
    #         if snakeHead[0] > GameBoard.width:
    #             snake.throughTheBoard(True, True, None)
    #         elif snakeHead[0] < 0:
    #             snake.throughTheBoard(True, False, None)
    #         elif snakeHead[1] > GameBoard.height:
    #             snake.throughTheBoard(False, None, False)
    #         elif snakeHead[1] < 0:
    #             snake.throughTheBoard(False, None, True)
    #         snake.move()
    #         snake.drawSnake(surface)

    def moveSnakes(self):
        for snake in self.snakeInGame:
            if snake != None:
                snakeHead = snake.getSnakeHaed()
                if snakeHead[0] > GameBoard.width:
                    snake.throughTheBoard(True, True, None)
                elif snakeHead[0] < 0:
                    snake.throughTheBoard(True, False, None)
                elif snakeHead[1] > GameBoard.height:
                    snake.throughTheBoard(False, None, False)
                elif snakeHead[1] < 0:
                    snake.throughTheBoard(False, None, True)
                snake.move()

    def moveSnake(self, snakeId):
        snake = self.snakeInGame[snakeId]
        snakeHead = snake.getSnakeHaed()
        if snakeHead[0] > GameBoard.width:
            snake.throughTheBoard(True, True, None)
        elif snakeHead[0] < 0:
            snake.throughTheBoard(True, False, None)
        elif snakeHead[1] > GameBoard.height:
            snake.throughTheBoard(False, None, False)
        elif snakeHead[1] < 0:
            snake.throughTheBoard(False, None, True)
        snake.move()

    #Verifica snake por snake para saber se alguma comeu a comida.
    #deprecated
    def checksAllSnakeEatFood(self):
        for snake in self.snakeInGame:
            if snake != None:
                snakeHead = snake.getSnakeHaed()
                for food in self.foodsInGame:
                    foodPosition = food.getFoodPosition()
                    if snakeHead[0] == foodPosition[0] and snakeHead[1] == foodPosition[1]:
                        snake.increaseSnakeLength()
                        # self.food.generateNewFood()
                        self.foodsInGame.remove(food)
                        #self.addFoodInGame()
                        break

    #Verifica se a snake comeu a comida.
    def checkSnakeEatFood(self, snakeId):
        snakeHead = self.snakeInGame[snakeId].getSnakeHaed()
        foodPosition = self.food.getFoodPosition()
        if snakeHead[0] == foodPosition[0] and snakeHead[1] == foodPosition[1]:
            self.snakeInGame[snakeId].increaseSnakeLength()
            self.food.generateNewFood()

    #Desenha na tela a primeira comida
    # def initGame(self, surface):
    #     self.food.drawFood(surface)
    def initGame(self):
        self.food.drawFood(self.gameSurface)
        # for food in self.foodsInGame:
        #     food.drawFood(self.gameSurface)

    #Transforma a tela do jogo em string para ser envia pela rede.
    def sendSurface(self):
        return (pygame.image.tostring(self.gameSurface, "RGB"), self.gameSurface.get_size())

    #retorna uma lista de dicionarios com cada dicionario representando a snake e sua cor.
    def snakesToSend(self):
        snakeToSend = []
        for snake in self.snakeInGame:
            # snakeToSend.append({"snakeBody": snake.getSnake(), "snakeColors": snake.getSnakeColors()})
            if snake != None:
                #print("snake to send")
                snakeToSend.append({"snakeBody": snake.getSnake(), "snakeColors": snake.getSnakeColors()})
        return snakeToSend

    #retorna uma lista de tuplas que contem as coordenadas xy da comida na tela.
    def foodToSend(self):
        foods = []
        for food in self.foodsInGame:
            foods.append(food.getFoodPosition())
        return foods

    #verifica se a snake bateu nela mesma
    def snakeDie(self, snakeId):
        snake = self.snakeInGame[snakeId]
        if snake:
            snakeHead = snake.getSnakeHaed()
            snakeBody = snake.getSnake()
            for i in range(len(snakeBody) - 1):
                if snakeBody[i][0] == snakeHead[0] and snakeBody[i][1] == snakeHead[1]:
                    # self.snakeInGame.remove(snake)
                    self.snakeInGame[snakeId] = None
                    self.regenateFoodsFromSnake(len(snakeBody))
                    return True
            for i in range(len(self.snakeInGame)):
                if i != snakeId:
                    if self.snakeInGame[i]:
                        otherSnake = self.snakeInGame[i].getSnake()
                        for eachPeace in otherSnake:
                            if eachPeace[0] == snakeHead[0] and eachPeace[1] == snakeHead[1]:
                                self.snakeInGame[snakeId] = None
                                self.regenateFoodsFromSnake(len(snakeBody))
                                return True

    def regenateFoodsFromSnake(self, amount):
        for i in range(amount):
            newFood = Food()
            self.foodsInGame.append(newFood)

    def addFoodInGame(self):
        newFood = Food()
        self.foodsInGame.append(newFood)
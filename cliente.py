import pygame
import socket, pickle

from snake.model.GameBoard import GameBoard
from snake.model.Player import Player
from snake.model.Snake import Snake
newPlayer = Player()

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 15000        # The port used by the server

def drawSnakes(surface, snakes):
    for snake in snakes:
        snakeBody = snake["snakeBody"]
        snakeBodyColor = snake["snakeColors"][0]
        snakeHeadColor = snake["snakeColors"][1]
        for snakeBodypiece in snakeBody:
            pygame.draw.rect(surface, snakeBodyColor, [snakeBodypiece[0], snakeBodypiece[1], Snake.size, Snake.size])
        pygame.draw.rect(surface, snakeHeadColor, [snakeBody[-1][0], snakeBody[-1][1], Snake.size, Snake.size])

def drawFoods(surface, foods):
    for food in foods:
        pygame.draw.rect(surface, Snake.red, [food[0], food[1], Snake.size, Snake.size])

def gameOver(surface):
    font = pygame.font.SysFont(None, 70)
    msg_gameOver = font.render("Game Over", True, Snake.white)
    surface.blit(msg_gameOver, [ GameBoard.width / 4, GameBoard.height / 3])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketClient:
    buffer = []
    socketClient.connect((HOST, PORT))
    #Solicita id para o servidor
    socketClient.sendall(pickle.dumps({"id": newPlayer.getId()}))
    socketClient.settimeout(0.1)

    try:
        serverResponse = socketClient.recv(4096)
        buffer.append(serverResponse)
    except socket.timeout:
        print("timeout")

    if len(buffer) > 0:
        response = pickle.loads(b"".join(buffer))
        buffer.clear()
    #print(response)
    newPlayer.setId(response["id"])
    serverResponse = None
    if newPlayer.getId() != None:
        try:
            pygame.init()
        except:
            print("Não foi possivel iniciar o Pygame")

        gameScreen = pygame.display.set_mode((GameBoard.width, GameBoard.height))

        while newPlayer.getalive():

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    newPlayer.setAlive(False)
                    socketClient.sendall(pickle.dumps({"id": newPlayer.getId(), "key": None}))
                    socketClient.close()
                elif event.type == pygame.KEYDOWN:
                    socketClient.sendall(pickle.dumps({"id": newPlayer.getId(), "key": event.key}))

            if newPlayer.getalive():
                while True:
                    try:
                        serverResponse = socketClient.recv(4096)
                        #buffer.append(serverResponse)
                        #print(len(serverResponse))
                        break
                    except socket.timeout:
                        print("Waint for server...")
                        break

                if serverResponse:
                    response = pickle.loads(serverResponse)
                    if response["snakeStillInGame"]:
                        gameScreen.fill(Snake.black)
                        drawFoods(gameScreen, response["foods"])
                        drawSnakes(gameScreen, response["snakes"])
                        pygame.display.update()
                    else:
                        newPlayer.setAlive(False)
                        socketClient.sendall(pickle.dumps({"id": newPlayer.getId(), "key": None}))
                        gameOver(gameScreen)
                        pygame.display.update()
                        socketClient.close()
                        waitForUser = True
                        while waitForUser:
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    pygame.quit()
                                    waitForUser = False
                # if len(buffer) > 0:
                #     response = pickle.loads(b"".join(buffer))
                #     buffer.clear()
                #     if response["snakeStillInGame"]:
                #         gameScreen.fill(Snake.black)
                #         drawFoods(gameScreen, response["foods"])
                #         drawSnakes(gameScreen, response["snakes"])
                #         pygame.display.update()
                #     else:
                #         newPlayer.setAlive(False)
                #         socketClient.sendall(pickle.dumps({"id": newPlayer.getId(), "key": None}))
                #         gameOver(gameScreen)
                #         pygame.display.update()
                #         socketClient.close()
                #         waitForUser = True
                #         while waitForUser:
                #             for event in pygame.event.get():
                #                 if event.type == pygame.QUIT:
                #                     pygame.quit()
                #                     waitForUser = False
            else:
                print("Desconnect from the server!")


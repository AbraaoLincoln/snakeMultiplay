import pygame
import socket, pickle
import threading
import time
# import select
import signal
import os

from snake.model.Snake import Snake
from snake.model.GameBoard import GameBoard
from snake.controle.GameManeger import GameManeger

try:
    pygame.init()
except:
    print("Não foi possivel iniciar o pygame")

gameSurface = pygame.Surface((GameBoard.width, GameBoard.height))
manager = GameManeger(gameSurface)

port = 15000
address = "127.0.0.1"

inputs = []
outputs = []
clientsThreads = []
updateClients = False
data = []
newDataFromClients = 0
requireClient = {}
mutex = threading.Lock()


def interuptionHandler(sig_number, sig_stack):
    print("Servidor Encerrado")
    os.kill(os.getpid(), signal.SIGKILL)

signal.signal(signal.SIGINT, interuptionHandler)

def clientInput(clientSocket):
    global data
    global requireClient
    global newDataFromClients
    global outputs
    clientConnect = True

    while clientConnect:
        try:
            data = clientSocket.recv(4096)
            if data:
                requireClient_local = pickle.loads(data)
                # Verifica se o cliente fechou a tela do jogo
                if requireClient_local["id"] != None and requireClient_local["key"] == None:
                    clientConnect = False
                mutex.acquire()
                requireClient = {"socketClient": clientSocket, "clientData": requireClient_local}
                newDataFromClients += 1
                mutex.release()
            else:
                print("enceraa")
                clientConnect = False
        except BlockingIOError:
            print("waiting input")
    print("Thread encerrada!")

def gen_food():
    global activeThreads
    while True:
        if len(outputs) > 0:
            time.sleep(5)
            manager.addFoodInGame()

thread_food = threading.Thread(target=gen_food, args=())
thread_food.start()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketServer:
    socketServer.setblocking(False)
    socketServer.bind(('', port))
    socketServer.listen()
    inputs.append(socketServer)

    while True:
        try:
            conn, info = socketServer.accept()
            conn.setblocking(False)
            outputs.append(conn)
            t = threading.Thread(target=clientInput, args=([conn]))
            t.start()
        except BlockingIOError:
            if newDataFromClients > 0:
                if data:
                    print("Client:", requireClient["clientData"]["id"], "send data!")
                    if requireClient["clientData"]["id"] == None:
                        newSnake = Snake()
                        idPlayer = manager.addSnakeInGame(newSnake)
                        requireClient["socketClient"].sendall(pickle.dumps({"id": idPlayer}))
                    else:
                        if requireClient["clientData"]["key"] != None:
                            manager.userCommand(requireClient["clientData"]["key"], requireClient["clientData"]["id"])
                            manager.moveSnakes()
                            if manager.snakeDie(requireClient["clientData"]["id"]):
                                requireClient["socketClient"].sendall(pickle.dumps({"snakeStillInGame": False}))
                            else:
                                manager.checksAllSnakeEatFood()
                        else:
                            manager.romoveSnakeOnGame(requireClient["clientData"]["id"])
                            outputs.remove(requireClient["socketClient"])
                            requireClient["socketClient"].close()
                    updateClients = True
                    newDataFromClients = False

            # Envia para os usuarios a tela do jogo atualizada.
            if updateClients:
                for sockets in outputs:
                    sockets.sendall(pickle.dumps({"snakes": manager.snakesToSend(), "foods": manager.foodToSend(), "snakeStillInGame": True}))
                updateClients = False
                #r, w, err = select.select(inputs, [], [], 0.1)

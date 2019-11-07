import pygame
import socket, pickle
import select
import time

from snake.model.Snake import Snake
from snake.model.GameBoard import GameBoard
from snake.controle.GameManeger import GameManeger
import threading
import time
import signal
import os

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
updateClients = False

def interuptionHandler(sig_number, sig_stack):
    print("Servidor Encerrado")
    os.kill(os.getpid(), signal.SIGKILL)
    thread_food.join()

signal.signal(signal.SIGINT, interuptionHandler)

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
        readable, writable, errs = select.select(inputs, outputs, [])
        for socks in readable:
            if socks is socketServer:
                try:
                    conn, info = socks.accept()
                    conn.setblocking(False)
                    inputs.append(conn)
                    outputs.append(conn)
                except BlockingIOError:
                    print("Wainting connections")
            else:
                data = socks.recv(4096)
                if data:
                    requireClient = pickle.loads(data)
                    #print("Client:", requireClient["id"], "send data!")
                    if requireClient["id"] == None:
                        newSnake = Snake()
                        idPlayer = manager.addSnakeInGame(newSnake)
                        socks.sendall(pickle.dumps({"id": idPlayer}))
                    else:
                        if requireClient["key"] != None:
                            manager.userCommand(requireClient["key"], requireClient["id"])
                            manager.moveSnakes()
                            if manager.snakeDie(requireClient["id"]):
                                socks.sendall(pickle.dumps({"snakeStillInGame": False}))
                            else:
                                manager.checksAllSnakeEatFood()
                        else:
                            manager.romoveSnakeOnGame(requireClient["id"])
                            inputs.remove(socks)
                            outputs.remove(socks)
                            writable.remove(socks)
                            socks.close()
                    updateClients = True
                else:
                    inputs.remove(socks)
                    outputs.remove(socks)
                    socks.close()

        # Envia para os usuarios a tela do jogo atualizada.
        if updateClients:
            for sockets in writable:
                sockets.sendall(pickle.dumps({"snakes": manager.snakesToSend(), "foods": manager.foodToSend(), "snakeStillInGame": True}))
            updateClients = False
            #r, w, err = select.select(inputs, [], [], 0.1)

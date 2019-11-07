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
star = time.time()
try:
    pygame.init()
except:
    print("Não foi possivel iniciar o pygame")

gameSurface = pygame.Surface((GameBoard.width, GameBoard.height))
manager = GameManeger(gameSurface)
#gameSurface.fill((9, 10, 13))

port = 15000
address = "127.0.0.1"

inputs = []
outputs = []
updateClients = False
doingLogicOfGame = 0
doingIO = 0
clientesConectados = 0
def interuptionHandler(sig_number, sig_stack):
    print("Servidor Encerrado")
    print("Tempo ativo:", (time.time() - star))
    print("Tempo gasto com o processamento da logica do jogo:", doingLogicOfGame, "segundos.")
    print("Tempo gasto com o processamento da I/O do jogo:", doingIO, "segundos.")
    print("cliente conectados:", clientesConectados)
    os.kill(os.getpid(), signal.SIGKILL)
    thread_food.join()

signal.signal(signal.SIGINT, interuptionHandler)

def gen_food():
    global activeThreads
    global doingLogicOfGame
    while True:
        if len(outputs) > 0:
            time.sleep(5)
            star_time = time.time()
            manager.addFoodInGame()
            doingLogicOfGame += (time.time() - star_time)

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
                    clientesConectados += 1
                except BlockingIOError:
                    print("Wainting connections")
            else:
                start_timeIO = time.time()
                data = socks.recv(4096)
                doingIO += (time.time() - start_timeIO)
                if data:
                    requireClient = pickle.loads(data)
                    #print("Client:", requireClient["id"], "send data!")
                    start_time_gameLogic = time.time()
                    if requireClient["id"] == None:
                        newSnake = Snake()
                        idPlayer = manager.addSnakeInGame(newSnake)
                        socks.sendall(pickle.dumps({"id": idPlayer}))
                    else:
                        if requireClient["key"] != None:
                            manager.userCommand(requireClient["key"], requireClient["id"])
                            manager.moveSnakes()
                            if manager.snakeDie(requireClient["id"]):
                                start_timeIO = time.time()
                                socks.sendall(pickle.dumps({"snakeStillInGame": False}))
                                doingIO += (time.time() - start_timeIO)
                            else:
                                manager.checksAllSnakeEatFood()
                        else:
                            manager.romoveSnakeOnGame(requireClient["id"])
                            inputs.remove(socks)
                            outputs.remove(socks)
                            writable.remove(socks)
                            socks.close()
                    doingLogicOfGame += (time.time() - start_time_gameLogic)
                    updateClients = True
                else:
                    inputs.remove(socks)
                    outputs.remove(socks)
                    socks.close()

        # Envia para os usuarios a tela do jogo atualizada.
        if updateClients:
            # start_timeIO = time.time()
            # manager.checksAllSnakeEatFood()
            # manager.moveSnakes()
            # doingIO += (time.time() - start_timeIO)
            start_timeIO = time.time()
            for sockets in writable:
                sockets.sendall(pickle.dumps({"snakes": manager.snakesToSend(), "foods": manager.foodToSend(), "snakeStillInGame": True}))
            doingIO += (time.time() - start_timeIO)
            updateClients = False
            #r, w, err = select.select(inputs, [], [], 0.1)

        if (time.time() - star) > 60.0:
            print("Servidor Encerrado")
            print("Tempo ativo:", (time.time() - star))
            print("Tempo gasto com o processamento da logica do jogo:", doingLogicOfGame, "segundos.")
            print("Tempo gasto com o processamento da I/O do jogo:", doingIO, "segundos.")
            print("cliente conectados:", clientesConectados)
            os.kill(os.getpid(), signal.SIGKILL)
            thread_food.join()
import pygame
import socket, pickle
import select
import threading
import time
import signal
import os

from snake.model.Snake import Snake
from snake.model.GameBoard import GameBoard
from snake.controle.GameManeger import GameManeger
start = time.time()
try:
    pygame.init()
except:
    print("Não foi possivel iniciar o pygame")

gameSurface = pygame.Surface((GameBoard.width, GameBoard.height))
manager = GameManeger(gameSurface)
gameSurface.fill((9, 10, 13))

port = 15000
address = "127.0.0.1"

inputs = []
outputs = []
clientsThreads = []
updateClients = False
data = []
newDataFromClients = False
requireClient = {}
mutex = threading.Lock()
doingLogicOfGame = 0
doingIO = 0
clientesConectados = 0
def interuptionHandler(sig_number, sig_stack):
    print("Servidor Encerrado")
    print("Tempo ativo:", (time.time() - start))
    print("Tempo gasto com o processamento da logica do jogo:", doingLogicOfGame, "segundos.")
    print("Tempo gasto com o processamento da I/O do jogo:", doingIO, "segundos.")
    print("cliente conectados:", clientesConectados)
    os.kill(os.getpid(), signal.SIGKILL)
    thread_food.join()

signal.signal(signal.SIGINT, interuptionHandler)

def clientInput(clientSocket):
    global data
    global requireClient
    global newClient
    global newDataFromClients
    global outputs
    global doingIO
    clientConnect = True

    while clientConnect:
        try:
            readable, writable, errs = select.select([clientSocket], [], [])
            for socks in readable:
                #star_time = time.time()
                data = socks.recv(4096)
                #doingIO += (time.time() - star_time)
            if data:
                requireClient_local = pickle.loads(data)
                #Verifica se o cliente fechou a tela do jogo
                if requireClient_local["id"] != None and requireClient_local["key"] == None:
                    clientConnect = False
                mutex.acquire()
                requireClient = {"socketClient": clientSocket, "clientData": requireClient_local}
                newDataFromClients = True
                mutex.release()
            else:
                print("enceraa")
                clientConnect = False
            # print("data lenght:", len(data))
        except ValueError:
            clientConnect = False
        except OSError:
            clientConnect = False
    print("Thread encerrada!")

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
        newClient, writable, erros = select.select([socketServer], outputs, [])

        for socket in newClient:
            try:
                conn, info = socket.accept()
                conn.setblocking(False)
                outputs.append(conn)
                t = threading.Thread(target=clientInput, args=([conn]))
                t.start()
                clientesConectados += 1
            except BlockingIOError:
                print("no connections!")

        if newDataFromClients:
            star_time = time.time()
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
                            start_io = time.time()
                            requireClient["socketClient"].sendall(pickle.dumps({"snakeStillInGame": False}))
                            doingIO += (time.time() - start_io)
                        else:
                            manager.checksAllSnakeEatFood()
                    else:
                        manager.romoveSnakeOnGame(requireClient["clientData"]["id"])
                        outputs.remove(requireClient["socketClient"])
                        writable.remove(requireClient["socketClient"])
                        requireClient["socketClient"].close()
                doingLogicOfGame += (time.time() - star_time)
                updateClients = True
                newDataFromClients = False
        # Envia para os usuarios a tela do jogo atualizada.
        if updateClients:
            start_io = time.time()
            for sockets in writable:
                sockets.sendall(pickle.dumps({"snakes": manager.snakesToSend(), "foods": manager.foodToSend(), "snakeStillInGame": True}))
            doingIO += (time.time() - start_io)
            updateClients = False
            #r, w, err = select.select(inputs, [], [], 0.1)

        if (time.time() - start) > 60.0:
            print("Servidor Encerrado")
            print("Tempo ativo:", (time.time() - start))
            print("Tempo gasto com o processamento da logica do jogo:", doingLogicOfGame, "segundos.")
            print("Tempo gasto com o processamento da I/O do jogo:", doingIO, "segundos.")
            print("cliente conectados:", clientesConectados)
            os.kill(os.getpid(), signal.SIGKILL)
            thread_food.join()
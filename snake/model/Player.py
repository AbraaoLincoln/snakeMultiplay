
class Player:

    def __init__(self):
        self.id = None
        self.alive = True

    def getId(self):
        return self.id

    def setId(self, newId):
        self.id = newId

    def getalive(self):
        return self.alive

    def setAlive(self, newValueAlive):
        self.alive = newValueAlive


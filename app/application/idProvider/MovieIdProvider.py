from app.application.idProvider.idProvider import IdProvider

class MemoryIdProvider(IdProvider):
    def __init__(self):
        self.__seq = 0

    def next_id(self):
        self.__seq += 1
        return self.__seq
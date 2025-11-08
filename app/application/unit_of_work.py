from abc import ABC, abstractmethod


class UnitOfWork(ABC):
    movies = None

    @abstractmethod
    def __enter__(self): ...

    @abstractmethod
    def __exit__(self, *args): ...

    @abstractmethod
    def commit(self): ...

    @abstractmethod
    def rollback(self): ...
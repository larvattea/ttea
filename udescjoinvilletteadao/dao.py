from abc import ABC, abstractmethod

class DAO(ABC):
    @abstractmethod
    def insert(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def select(self):
        pass

    @abstractmethod
    def list(self):
        pass
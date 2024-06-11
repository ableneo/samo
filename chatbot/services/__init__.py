from abc import ABC, abstractmethod


class ServiceInterface(ABC):
    """Interface definition for Services."""

    @abstractmethod
    def index(self):
        pass

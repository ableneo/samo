from abc import ABC, abstractmethod


class ExecutableInterface(ABC):
    """Interface definition for executable classes"""

    @abstractmethod
    def execute(self):
        pass


class SerializableInterface(ABC):
    """Interface definition for serializable classes"""

    @abstractmethod
    def serialize(self) -> str:
        pass

    @abstractmethod
    def deserialize(self, data: dict):
        pass

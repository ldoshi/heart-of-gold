import abc 

class Plugin(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def command(self, command: str) -> None:
        pass

    @abc.abstractmethod
    def reset(self) -> None:
        pass

    

import abc


class Plugin(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def command(self, command: str) -> None:
        pass

    @abc.abstractmethod
    def reset(self) -> None:
        pass

    # TODO(lyric): Implement a plugin schedule.
    def is_active(self) -> bool:
        return True

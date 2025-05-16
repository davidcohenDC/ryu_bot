from abc import ABC, abstractmethod
import aiosqlite

class BaseRepository(ABC):
    def __init__(self, connection: aiosqlite.Connection):
        self._db = connection

    @abstractmethod
    async def get_all(self, *args, **kwargs):
        pass

    @abstractmethod
    async def exists(self, *args, **kwargs) -> bool:
        pass

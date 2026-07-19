from abc import ABC, abstractmethod


class BaseProcessor(ABC):
    def __init__(self):
        ...

    @abstractmethod
    def __call__(self, *args, **kwargs):
        ...

from abc import ABCMeta, abstractmethod


class SingletonMeta(ABCMeta):
    """
    Metaclass for singleton classes with an abstract `__init__` method.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Singleton pattern implementation. If the class was not instantiated yet, create a new instance, initialize and
        store it.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
            instance.__init__(*args, **kwargs)
        return cls._instances[cls]

    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Abstract method that must be implemented by every singleton class.
        """
        pass

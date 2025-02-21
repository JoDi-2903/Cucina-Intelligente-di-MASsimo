from abc import abstractmethod

from dash import Dash

from meta_classes.singleton import SingletonMeta


class CallbackRegistrarMeta(SingletonMeta):
    """Singleton metaclass for callback registrars."""

    @staticmethod
    @abstractmethod
    def register_callbacks(app: Dash):
        """
        Abstract method that must be implemented by every singleton class.
        """
        pass

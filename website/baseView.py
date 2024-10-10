from abc import ABC, abstractmethod

# setup base view class so other classes can inherit from this one
# this will act as the abstract super parent class
class baseView(ABC):
    def __init__(self, flaskApp):
        self._flaskApp = flaskApp

    # setup abstract methods (IMPORTANT: these need to be defined in the child classes)
    @abstractmethod
    def _setupRoutes(self):
        pass
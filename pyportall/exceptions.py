class PyPortallException(Exception):
    pass


class PreFlightException(PyPortallException):
    def __init__(self, credits, *args) -> None:
        self.credits = credits

        super().__init__(*args)

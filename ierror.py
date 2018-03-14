
class IError(Exception):
    def __init__(self, error):
        self.__error = error

    def __str__(self):
        return self.__error
# Copyright 2024 Recursive AI


class ApplicationException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class DoesNotExistError(ApplicationException):
    pass


class AlreadyExistsError(ApplicationException):
    pass

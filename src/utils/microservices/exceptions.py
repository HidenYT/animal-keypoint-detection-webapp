class MicroserviceRequestException(Exception):
    def __init__(self, msg) -> None:
        super().__init__(msg)

class RequestSendingError(MicroserviceRequestException):
    pass

class ConnectionError(MicroserviceRequestException):
    pass
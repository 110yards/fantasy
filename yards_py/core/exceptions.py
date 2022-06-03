class ApiException(Exception):
    def __init__(self, message):
        self.message = message


class InvalidPushException(ApiException):
    def __init__(self):
        ApiException.__init__(self, "Push body was empty or invalid")


class NotSupportedException(ApiException):
    def __init__(self, message):
        ApiException.__init__(self, message)

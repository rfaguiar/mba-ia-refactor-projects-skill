class ApiError(Exception):
    def __init__(self, message, status=400, include_success=False):
        super().__init__(message)
        self.message = message
        self.status = status
        self.include_success = include_success

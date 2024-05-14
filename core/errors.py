from fastapi import HTTPException, status


class DatabaseConnectionError(Exception):
    """Exception raised when unable to establish a database connection."""

    def __init__(self, message="Failed to establish a database connection."):
        self.message = message
        super().__init__(self.message)


class MissingResource(HTTPException):
    def __init__(self, message=""):
        return super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)


class ResourcesExist(HTTPException):
    def __init__(self, message=""):
        return super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=message)

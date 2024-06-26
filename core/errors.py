from fastapi import HTTPException, status


class DatabaseConnectionError(Exception):
    """Exception raised when unable to establish a database connection."""

    def __init__(self, message="Failed to establish a database connection."):
        self.message = message
        super().__init__(self.message)


class MissingResources(HTTPException):

    def __init__(
        self, message="Missing Resource: No such resource by that UUID, name, or email"
    ):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)


class ResourcesExist(HTTPException):
    def __init__(self, message="Resources with that ID, name or Email Exist"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=message)


class InvalidRequest(HTTPException):
    def __init__(self, message="Invalid Request"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=message)


class CredentialException(HTTPException):
    def __init__(self, detail: str = "Invalid Credentials"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

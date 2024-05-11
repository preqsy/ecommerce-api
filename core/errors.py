class DatabaseConnectionError(Exception):
    """Exception raised when unable to establish a database connection."""

    def __init__(self, message="Failed to establish a database connection."):
        self.message = message
        super().__init__(self.message)

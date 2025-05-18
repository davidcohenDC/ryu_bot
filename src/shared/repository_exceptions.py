class RepositoryError(Exception):
    """Base class for all repository exceptions."""
    def __init__(self, message: str = "An error occurred in the repository.", code: int = 1000):
        self.message = message
        self.code = code
        super().__init__(f"[{self.code}] {self.message}")


class NotFoundError(RepositoryError):
    """Exception raised when an entity is not found."""
    def __init__(self, entity: str = "Entity", code: int = 1001):
        message = f"{entity} not found."
        super().__init__(message, code)


class InsertError(RepositoryError):
    """Exception raised when an insert operation fails."""
    def __init__(self, entity: str = "Entity", code: int = 1002):
        message = f"Failed to insert {entity}."
        super().__init__(message, code)

class UpdateError(RepositoryError):
    """Exception raised when an update operation fails."""
    def __init__(self, entity: str = "Entity", code: int = 1003):
        message = f"Failed to update {entity}."
        super().__init__(message, code)

class DeleteError(RepositoryError):
    """Exception raised when a delete operation fails."""
    def __init__(self, entity: str = "Entity", code: int = 1004):
        message = f"Failed to delete {entity}."
        super().__init__(message, code)


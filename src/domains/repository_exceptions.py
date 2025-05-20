class RepositoryError(Exception):
    """Base class for all repository exceptions."""
    def __init__(self, message: str = "An error occurred in the repository.", code: int = 1000):
        self.message = message
        self.code = code
        super().__init__(f"[{self.code}] {self.message}")

class EntityNotFoundRepositoryError(RepositoryError):
    """Exception raised when an entity is not found."""
    def __init__(self, entity: str = "Entity", code: int = 1001):
        message = f"{entity} not found."
        super().__init__(message, code)

class DuplicateEntityRepositoryError(RepositoryError):
    """Exception raised when a duplicate entity is found."""
    def __init__(self, entity: str = "Entity", code: int = 1002):
        message = f"Failed to insert {entity}."
        super().__init__(message, code)


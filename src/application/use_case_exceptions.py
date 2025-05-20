
class UseCaseError(Exception):
    """Base class for all use case exceptions."""
    def __init__(self, message: str = "An error occurred in the use case.", code: int = 2000):
        self.message = message
        self.code = code
        super().__init__(self.message)

class EntityNotFoundUseCaseError(UseCaseError):
    """Exception raised when an entity is not found."""
    def __init__(self, entity: str = "Entity", code: int = 2001):
        message = f"{entity} not found."
        super().__init__(message, code)

class OperationNotAllowedUseCaseError(UseCaseError):
    """Exception raised when an operation is not allowed."""
    def __init__(self, entity: str = "Entity", code: int = 2002):
        message = f"Operation not allowed for {entity}."
        super().__init__(message, code)

class ValidationUseCaseError(UseCaseError):
    """Exception raised for validation errors."""
    def __init__(self, message: str = "Validation error.", code: int = 2003):
        super().__init__(message, code)

class ConflictUseCaseError(UseCaseError):
    """Exception raised for conflict errors."""
    def __init__(self, message: str = "Conflict error.", code: int = 2004):
        super().__init__(message, code)
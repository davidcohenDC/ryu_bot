from functools import wraps

from src.application.use_case_exceptions import EntityNotFoundUseCaseError, ConflictUseCaseError, UseCaseError
from src.domains.repository_exceptions import EntityNotFoundRepositoryError, DuplicateEntityRepositoryError, \
    RepositoryError

def wrap_use_cases_exceptions(func):
    """
    Decorator to wrap use case methods with error handling.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        """
        Wrapper function to handle exceptions and raise custom use case errors.
        """
        try:
            return await func(*args, **kwargs)
        except EntityNotFoundRepositoryError as e:
            raise EntityNotFoundUseCaseError(str(e)) from e
        except DuplicateEntityRepositoryError as e:
            raise ConflictUseCaseError(str(e)) from e
        except RepositoryError as e:
            raise UseCaseError("Internal service error") from e
        # except RequestException as e:
        #     # Qualsiasi errore HTTP (timeout, connessione, 5xx…)
        #     raise ExternalServiceError(f"Errore esterno: {e}") from e
        # except TimeoutError as e:
        #     # Timeout generico di libreria async, DB, rete…
        #     raise ExternalServiceError(f"Timeout esterno: {e}") from e
        # except GatewayError as e:
        #     raise ExternalServiceError("Pagamento fallito") from e
    return wrapper
from functools import wraps
from sqlalchemy.exc import NoResultFound, IntegrityError, SQLAlchemyError

from src.domains.repository_exceptions import EntityNotFoundRepositoryError, DuplicateEntityRepositoryError, \
    RepositoryError


def wrap_repo_exceptions(func):
    """
    Decorator to wrap repository methods with error handling.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        """
        Wrapper function to handle exceptions and raise custom repository errors.
        """
        try:
            return await func(*args, **kwargs)
        except NoResultFound as e:
            raise EntityNotFoundRepositoryError(f"Entity not found: {e}") from e
        except IntegrityError as e:
            raise DuplicateEntityRepositoryError(f"Duplicate entity: {e}") from e
        except SQLAlchemyError as e:
            raise RepositoryError(f"Repository error: {e}") from e
    return wrapper

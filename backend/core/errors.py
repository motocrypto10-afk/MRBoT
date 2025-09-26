"""
Typed errors and error mappers for consistent API responses
"""
from typing import Dict, Any, Optional
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class BotMRException(Exception):
    """Base exception for BotMR application"""
    
    def __init__(self, message: str, code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(BotMRException):
    """Data validation error"""
    pass

class NotFoundError(BotMRException):
    """Resource not found error"""
    pass

class ConflictError(BotMRException):
    """Resource conflict error"""
    pass

class AuthenticationError(BotMRException):
    """Authentication error"""
    pass

class AuthorizationError(BotMRException):
    """Authorization error"""
    pass

class ExternalServiceError(BotMRException):
    """External service error"""
    pass

class ProcessingError(BotMRException):
    """Data processing error"""
    pass

class StorageError(BotMRException):
    """Storage/database error"""
    pass

class QueueError(BotMRException):
    """Job queue error"""
    pass

# Error code to HTTP status mapping
ERROR_STATUS_MAP = {
    'ValidationError': 400,
    'NotFoundError': 404,
    'ConflictError': 409,
    'AuthenticationError': 401,
    'AuthorizationError': 403,
    'ExternalServiceError': 502,
    'ProcessingError': 422,
    'StorageError': 500,
    'QueueError': 500,
    'BotMRException': 500
}

def map_exception_to_http(exc: Exception) -> HTTPException:
    """Map application exceptions to HTTP exceptions"""
    
    if isinstance(exc, BotMRException):
        status_code = ERROR_STATUS_MAP.get(exc.code, 500)
        
        detail = {
            "error": exc.code,
            "message": exc.message,
            "details": exc.details
        }
        
        logger.error(f"Application error: {exc.code} - {exc.message}", 
                    extra={"error_details": exc.details})
        
        return HTTPException(status_code=status_code, detail=detail)
    
    # Handle standard exceptions
    elif isinstance(exc, ValueError):
        logger.error(f"Validation error: {str(exc)}")
        return HTTPException(
            status_code=400, 
            detail={
                "error": "ValidationError", 
                "message": str(exc),
                "details": {}
            }
        )
    
    elif isinstance(exc, KeyError):
        logger.error(f"Missing key error: {str(exc)}")
        return HTTPException(
            status_code=400, 
            detail={
                "error": "MissingFieldError", 
                "message": f"Missing required field: {str(exc)}",
                "details": {}
            }
        )
    
    else:
        # Generic server error
        logger.exception(f"Unhandled error: {str(exc)}")
        return HTTPException(
            status_code=500, 
            detail={
                "error": "InternalServerError", 
                "message": "An unexpected error occurred",
                "details": {}
            }
        )

def create_error_response(
    error_code: str, 
    message: str, 
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create standardized error response"""
    return {
        "error": error_code,
        "message": message,
        "details": details or {},
        "timestamp": None  # Will be added by logging middleware
    }
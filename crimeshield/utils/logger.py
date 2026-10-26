"""
Logging utilities for CRIMESHIELD.
Demonstrates: Decorators, function wrapping, and logging setup.
"""

import logging
import functools
from typing import Callable, Any
from flask import request
import time


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with consistent formatting.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create console handler with formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Format: timestamp - name - level - message
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


def log_request(func: Callable) -> Callable:
    """
    Decorator to log API requests and responses.
    Demonstrates: Function decorator with wrapping and closure.
    
    This decorator:
    1. Logs incoming requests with method and path
    2. Times the request execution
    3. Logs the response status code
    4. Handles exceptions gracefully
    
    Args:
        func: Flask route function to decorate
        
    Returns:
        Wrapped function
    """
    @functools.wraps(func)  # Preserves function metadata
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """
        Wrapper function that adds logging.
        Demonstrates: Closure - inner function accessing outer function's variables.
        """
        logger = logging.getLogger(__name__)
        
        # Log request details (without sensitive data)
        logger.info(f"REQUEST: {request.method} {request.path}")
        
        # Track execution time
        start_time = time.time()
        
        try:
            # Execute the actual route function
            response = func(*args, **kwargs)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Extract status code from response
            if isinstance(response, tuple):
                status_code = response[1] if len(response) > 1 else 200
            else:
                status_code = 200
            
            logger.info(
                f"RESPONSE: {request.method} {request.path} - "
                f"Status: {status_code} - Time: {execution_time:.3f}s"
            )
            
            return response
        
        except Exception as e:
            # Log errors without exposing sensitive details
            execution_time = time.time() - start_time
            logger.error(
                f"ERROR: {request.method} {request.path} - "
                f"{type(e).__name__} - Time: {execution_time:.3f}s"
            )
            raise
    
    return wrapper


def log_execution_time(func: Callable) -> Callable:
    """
    Decorator to log function execution time.
    Demonstrates: Another example of decorator pattern.
    
    Args:
        func: Function to decorate
        
    Returns:
        Wrapped function
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = logging.getLogger(__name__)
        start_time = time.time()
        
        result = func(*args, **kwargs)
        
        execution_time = time.time() - start_time
        logger.debug(f"{func.__name__} executed in {execution_time:.3f}s")
        
        return result
    
    return wrapper

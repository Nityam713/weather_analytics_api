"""
Input validation utilities.
"""
import re
from datetime import datetime
from typing import Optional


def validate_city_name(city: str) -> str:
    """
    Validates and sanitizes city name.
    
    Args:
        city: City name to validate
    
    Returns:
        Sanitized city name
    
    Raises:
        ValueError: If city name is invalid
    """
    if not city:
        raise ValueError("City name cannot be empty")
    
    # Strip whitespace
    city = city.strip()
    
    if len(city) < 2:
        raise ValueError("City name must be at least 2 characters")
    
    if len(city) > 100:
        raise ValueError("City name must be less than 100 characters")
    
    # Allow letters, spaces, hyphens, apostrophes (for names like "New York", "O'Brien")
    if not re.match(r"^[a-zA-Z\s\-']+$", city):
        raise ValueError("City name contains invalid characters")
    
    return city


def validate_date_format(date_str: str) -> datetime:
    """
    Validates date string format (YYYY-MM-DD).
    
    Args:
        date_str: Date string to validate
    
    Returns:
        Parsed datetime object
    
    Raises:
        ValueError: If date format is invalid
    """
    if not date_str:
        raise ValueError("Date cannot be empty")
    
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD (e.g., 2026-01-19)")


def validate_days(days: Optional[int], min_days: int = 1, max_days: int = 365) -> Optional[int]:
    """
    Validates number of days parameter.
    
    Args:
        days: Number of days to validate
        min_days: Minimum allowed days
        max_days: Maximum allowed days
    
    Returns:
        Validated days value
    
    Raises:
        ValueError: If days is invalid
    """
    if days is None:
        return None
    
    if not isinstance(days, int):
        raise ValueError("Days must be an integer")
    
    if days < min_days:
        raise ValueError(f"Days must be at least {min_days}")
    
    if days > max_days:
        raise ValueError(f"Days must be at most {max_days}")
    
    return days


def validate_weeks(weeks: int, min_weeks: int = 1, max_weeks: int = 52) -> int:
    """
    Validates number of weeks parameter.
    
    Args:
        weeks: Number of weeks to validate
        min_weeks: Minimum allowed weeks
        max_weeks: Maximum allowed weeks
    
    Returns:
        Validated weeks value
    
    Raises:
        ValueError: If weeks is invalid
    """
    if not isinstance(weeks, int):
        raise ValueError("Weeks must be an integer")
    
    if weeks < min_weeks:
        raise ValueError(f"Weeks must be at least {min_weeks}")
    
    if weeks > max_weeks:
        raise ValueError(f"Weeks must be at most {max_weeks}")
    
    return weeks


def validate_months(months: int, min_months: int = 1, max_months: int = 24) -> int:
    """
    Validates number of months parameter.
    
    Args:
        months: Number of months to validate
        min_months: Minimum allowed months
        max_months: Maximum allowed months
    
    Returns:
        Validated months value
    
    Raises:
        ValueError: If months is invalid
    """
    if not isinstance(months, int):
        raise ValueError("Months must be an integer")
    
    if months < min_months:
        raise ValueError(f"Months must be at least {min_months}")
    
    if months > max_months:
        raise ValueError(f"Months must be at most {max_months}")
    
    return months


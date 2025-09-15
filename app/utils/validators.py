"""
Validation utilities for the voting system.

This module provides comprehensive validation functions for voters, candidates, 
votes, and other election-related data to ensure data integrity and business rules.
"""

import re
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timezone
from fastapi import HTTPException, status


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_voter_id(voter_id: int) -> bool:
    """
    Validate voter ID format and constraints.
    
    Args:
        voter_id: The voter ID to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If voter ID is invalid
    """
    if not isinstance(voter_id, int):
        raise ValidationError("Voter ID must be an integer")
    
    if voter_id <= 0:
        raise ValidationError("Voter ID must be a positive integer")
    
    if voter_id > 999999999:  # Max 9 digits
        raise ValidationError("Voter ID must be less than 10 digits")
    
    return True


def validate_candidate_id(candidate_id: int) -> bool:
    """
    Validate candidate ID format and constraints.
    
    Args:
        candidate_id: The candidate ID to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If candidate ID is invalid
    """
    if not isinstance(candidate_id, int):
        raise ValidationError("Candidate ID must be an integer")
    
    if candidate_id <= 0:
        raise ValidationError("Candidate ID must be a positive integer")
    
    if candidate_id > 999999:  # Max 6 digits
        raise ValidationError("Candidate ID must be less than 7 digits")
    
    return True


def validate_voter_age(age: int) -> bool:
    """
    Validate voter age meets legal requirements.
    
    Args:
        age: The voter's age
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If age is invalid
    """
    if not isinstance(age, int):
        raise ValidationError("Age must be an integer")
    
    if age < 18:
        raise ValidationError(f"Invalid age: {age}, must be 18 or older")
    
    if age > 150:
        raise ValidationError(f"Invalid age: {age}, age seems unrealistic")
    
    return True


def validate_name(name: str, field_name: str = "Name") -> bool:
    """
    Validate name format and constraints.
    
    Args:
        name: The name to validate
        field_name: The field name for error messages
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If name is invalid
    """
    if not isinstance(name, str):
        raise ValidationError(f"{field_name} must be a string")
    
    if not name or not name.strip():
        raise ValidationError(f"{field_name} cannot be empty")
    
    if len(name.strip()) < 2:
        raise ValidationError(f"{field_name} must be at least 2 characters long")
    
    if len(name.strip()) > 100:
        raise ValidationError(f"{field_name} must be less than 100 characters")
    
    # Allow letters, spaces, hyphens, apostrophes, and periods
    if not re.match(r"^[a-zA-Z\s\-'\.]+$", name.strip()):
        raise ValidationError(f"{field_name} contains invalid characters")
    
    return True


def validate_party_name(party: str) -> bool:
    """
    Validate political party name.
    
    Args:
        party: The party name to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If party name is invalid
    """
    if not isinstance(party, str):
        raise ValidationError("Party name must be a string")
    
    if not party or not party.strip():
        raise ValidationError("Party name cannot be empty")
    
    if len(party.strip()) < 2:
        raise ValidationError("Party name must be at least 2 characters long")
    
    if len(party.strip()) > 50:
        raise ValidationError("Party name must be less than 50 characters")
    
    return True


def validate_vote_weight(weight: int) -> bool:
    """
    Validate vote weight for weighted voting systems.
    
    Args:
        weight: The vote weight to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If weight is invalid
    """
    if not isinstance(weight, int):
        raise ValidationError("Vote weight must be an integer")
    
    if weight < 1:
        raise ValidationError("Vote weight must be at least 1")
    
    if weight > 10:  # Reasonable upper limit
        raise ValidationError("Vote weight cannot exceed 10")
    
    return True


def validate_timestamp(timestamp: str) -> bool:
    """
    Validate timestamp format.
    
    Args:
        timestamp: The timestamp string to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If timestamp is invalid
    """
    if not isinstance(timestamp, str):
        raise ValidationError("Timestamp must be a string")
    
    try:
        # Try multiple common formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ]
        
        parsed = None
        for fmt in formats:
            try:
                parsed = datetime.strptime(timestamp, fmt)
                break
            except ValueError:
                continue
        
        if parsed is None:
            raise ValidationError(f"Invalid timestamp format: {timestamp}")
        
        # Check if timestamp is not in the future (with some tolerance)
        now = datetime.now()
        if parsed > now:
            raise ValidationError("Timestamp cannot be in the future")
        
        return True
        
    except Exception as e:
        raise ValidationError(f"Invalid timestamp: {str(e)}")


def validate_election_id(election_id: str) -> bool:
    """
    Validate election ID format.
    
    Args:
        election_id: The election ID to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If election ID is invalid
    """
    if not isinstance(election_id, str):
        raise ValidationError("Election ID must be a string")
    
    if not election_id or not election_id.strip():
        raise ValidationError("Election ID cannot be empty")
    
    if len(election_id.strip()) < 3:
        raise ValidationError("Election ID must be at least 3 characters long")
    
    if len(election_id.strip()) > 50:
        raise ValidationError("Election ID must be less than 50 characters")
    
    # Allow alphanumeric, hyphens, and underscores
    if not re.match(r"^[a-zA-Z0-9\-_]+$", election_id.strip()):
        raise ValidationError("Election ID contains invalid characters")
    
    return True


def validate_ranking_list(ranking: List[int], available_candidates: List[int]) -> bool:
    """
    Validate ranked choice voting ranking.
    
    Args:
        ranking: List of candidate IDs in order of preference
        available_candidates: List of available candidate IDs
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If ranking is invalid
    """
    if not isinstance(ranking, list):
        raise ValidationError("Ranking must be a list")
    
    if len(ranking) == 0:
        raise ValidationError("Ranking cannot be empty")
    
    if len(ranking) != len(set(ranking)):
        raise ValidationError("Ranking cannot contain duplicate candidates")
    
    for candidate_id in ranking:
        if not isinstance(candidate_id, int):
            raise ValidationError("All candidate IDs in ranking must be integers")
        
        if candidate_id not in available_candidates:
            raise ValidationError(f"Candidate ID {candidate_id} is not available for this election")
    
    return True


def validate_risk_limit(risk_limit_alpha: float) -> bool:
    """
    Validate risk limit for audit plans.
    
    Args:
        risk_limit_alpha: The risk limit alpha value
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If risk limit is invalid
    """
    if not isinstance(risk_limit_alpha, (int, float)):
        raise ValidationError("Risk limit alpha must be a number")
    
    if risk_limit_alpha <= 0 or risk_limit_alpha >= 1:
        raise ValidationError("Risk limit alpha must be between 0 and 1 (exclusive)")
    
    return True


def validate_epsilon_value(epsilon: float) -> bool:
    """
    Validate epsilon value for differential privacy.
    
    Args:
        epsilon: The privacy budget epsilon value
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If epsilon is invalid
    """
    if not isinstance(epsilon, (int, float)):
        raise ValidationError("Epsilon must be a number")
    
    if epsilon <= 0:
        raise ValidationError("Epsilon must be positive")
    
    if epsilon > 10:  # Reasonable upper bound
        raise ValidationError("Epsilon value seems too high for meaningful privacy")
    
    return True


def validate_query_parameters(start: Optional[str] = None, end: Optional[str] = None, 
                            limit: Optional[int] = None, offset: Optional[int] = None) -> bool:
    """
    Validate common query parameters.
    
    Args:
        start: Start timestamp for range queries
        end: End timestamp for range queries
        limit: Limit for pagination
        offset: Offset for pagination
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If parameters are invalid
    """
    if start is not None:
        validate_timestamp(start)
    
    if end is not None:
        validate_timestamp(end)
    
    if start and end:
        start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
        if start_dt >= end_dt:
            raise ValidationError("Start time must be before end time")
    
    if limit is not None:
        if not isinstance(limit, int):
            raise ValidationError("Limit must be an integer")
        if limit < 1:
            raise ValidationError("Limit must be at least 1")
        if limit > 1000:  # Reasonable upper bound
            raise ValidationError("Limit cannot exceed 1000")
    
    if offset is not None:
        if not isinstance(offset, int):
            raise ValidationError("Offset must be an integer")
        if offset < 0:
            raise ValidationError("Offset cannot be negative")
    
    return True


def safe_validate_voter_id(voter_id: int) -> Union[bool, HTTPException]:
    """
    Safely validate voter ID and return HTTPException if invalid.
    
    Args:
        voter_id: The voter ID to validate
        
    Returns:
        bool if valid, HTTPException if invalid
    """
    try:
        return validate_voter_id(voter_id)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


def safe_validate_candidate_id(candidate_id: int) -> Union[bool, HTTPException]:
    """
    Safely validate candidate ID and return HTTPException if invalid.
    
    Args:
        candidate_id: The candidate ID to validate
        
    Returns:
        bool if valid, HTTPException if invalid
    """
    try:
        return validate_candidate_id(candidate_id)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


def safe_validate_voter_age(age: int) -> Union[bool, HTTPException]:
    """
    Safely validate voter age and return HTTPException if invalid.
    
    Args:
        age: The voter's age
        
    Returns:
        bool if valid, HTTPException if invalid
    """
    try:
        return validate_voter_age(age)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


def safe_validate_name(name: str, field_name: str = "Name") -> Union[bool, HTTPException]:
    """
    Safely validate name and return HTTPException if invalid.
    
    Args:
        name: The name to validate
        field_name: The field name for error messages
        
    Returns:
        bool if valid, HTTPException if invalid
    """
    try:
        return validate_name(name, field_name)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Helper function to validate complete voter data
def validate_voter_data(voter_id: int, name: str, age: int) -> bool:
    """
    Validate complete voter data.
    
    Args:
        voter_id: The voter ID
        name: The voter's name
        age: The voter's age
        
    Returns:
        bool: True if all data is valid
        
    Raises:
        ValidationError: If any validation fails
    """
    validate_voter_id(voter_id)
    validate_name(name, "Voter name")
    validate_voter_age(age)
    return True


# Helper function to validate complete candidate data
def validate_candidate_data(candidate_id: int, name: str, party: str) -> bool:
    """
    Validate complete candidate data.
    
    Args:
        candidate_id: The candidate ID
        name: The candidate's name
        party: The candidate's party
        
    Returns:
        bool: True if all data is valid
        
    Raises:
        ValidationError: If any validation fails
    """
    validate_candidate_id(candidate_id)
    validate_name(name, "Candidate name")
    validate_party_name(party)
    return True


# Helper function to validate vote data
def validate_vote_data(voter_id: int, candidate_id: int, weight: int = 1) -> bool:
    """
    Validate complete vote data.
    
    Args:
        voter_id: The voter ID
        candidate_id: The candidate ID
        weight: The vote weight (optional, defaults to 1)
        
    Returns:
        bool: True if all data is valid
        
    Raises:
        ValidationError: If any validation fails
    """
    validate_voter_id(voter_id)
    validate_candidate_id(candidate_id)
    validate_vote_weight(weight)
    return True

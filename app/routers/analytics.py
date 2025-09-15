from fastapi import APIRouter, HTTPException, status
from app.models import DPAnalyticsRequest, DPAnalyticsResponse
from app.storage import storage
import random
import uuid

router = APIRouter()

@router.post("/analytics/dp", response_model=DPAnalyticsResponse, status_code=status.HTTP_200_OK)
async def differential_privacy_analytics(request: DPAnalyticsRequest):
    """
    Perform differential privacy analytics on voting data.
    
    Supports histogram queries with differential privacy guarantees.
    """
    # Validate epsilon and delta parameters
    if request.epsilon <= 0 or request.epsilon > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Epsilon must be between 0 and 10"
        )
    
    if request.delta <= 0 or request.delta >= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Delta must be between 0 and 1"
        )
    
    # Validate query type
    if request.query.type != "histogram":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only histogram queries are currently supported"
        )
    
    # Validate dimension
    if request.query.dimension != "voter_age_bucket":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only voter_age_bucket dimension is currently supported"
        )
    
    # Get analytics result from storage
    result = storage.get_dp_analytics(
        election_id=request.election_id,
        query_type=request.query.type,
        dimension=request.query.dimension,
        buckets=request.query.buckets,
        filter_criteria=request.query.filter,
        epsilon=request.epsilon,
        delta=request.delta
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"]
        )
    
    # Generate unique query ID
    query_id = str(uuid.uuid4())
    
    # Track total epsilon spent (simplified tracking)
    total_epsilon_spent = storage.track_epsilon_usage(request.election_id, request.epsilon)
    
    return DPAnalyticsResponse(
        election_id=request.election_id,
        query_id=query_id,
        result=result["data"],
        privacy_parameters={
            "epsilon": request.epsilon,
            "delta": request.delta
        },
        noise_mechanism="gaussian",
        total_epsilon_spent=total_epsilon_spent
    )
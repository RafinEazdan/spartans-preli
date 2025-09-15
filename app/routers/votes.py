from fastapi import APIRouter, HTTPException, status, Query
from app.models import VoteRequest, WeightedVoteRequest, VoteTimeline
from app.storage import storage
from typing import Optional

router = APIRouter()

# Q8: Cast Vote
@router.post("/votes", status_code=status.HTTP_201_CREATED)
async def cast_vote(vote: VoteRequest):
    result = storage.cast_vote(vote.voter_id, vote.candidate_id)
    if "error" in result:
        if "not found" in result["error"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])
    return {"message": "Vote recorded."}

# Q13: Vote Timeline
@router.get("/votes/timeline", response_model=VoteTimeline)
async def get_vote_timeline(candidate_id: int = Query(...)):
    timeline = storage.get_vote_timeline(candidate_id)
    return {
        "candidate_id": candidate_id,
        "timeline": timeline
    }

# Q14: Weighted Vote
@router.post("/votes/weighted", status_code=status.HTTP_201_CREATED)
async def cast_weighted_vote(vote: WeightedVoteRequest):
    result = storage.cast_vote(vote.voter_id, vote.candidate_id, vote.weight)
    if "error" in result:
        if "not found" in result["error"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])
    return {
        "vote_id": result["vote_id"],
        "voter_id": vote.voter_id,
        "candidate_id": vote.candidate_id,
        "weight": vote.weight
    }

# Q15: Range Vote Queries
@router.get("/votes/range")
async def get_votes_range(
    start: str = Query(..., description="Start timestamp"),
    end: str = Query(..., description="End timestamp")
):
    votes = storage.get_votes_in_range(start, end)
    return {"votes": votes}
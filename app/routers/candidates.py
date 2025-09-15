from fastapi import APIRouter, HTTPException, status
from app.models import CandidateCreate, Candidate
from app.storage import storage

router = APIRouter()

# Q6: Register Candidate
@router.post("/candidates", response_model=Candidate, status_code=status.HTTP_201_CREATED)
async def register_candidate(candidate: CandidateCreate):
    result = storage.add_candidate(candidate.candidate_id, candidate.name, candidate.party)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"candidate with id: {candidate.candidate_id} already exists"
        )
    return result

# Q7: List Candidates
@router.get("/candidates")
async def list_candidates():
    candidates = storage.get_all_candidates()
    return {"candidates": candidates}

# Get Candidate Votes
@router.get("/candidates/{candidate_id}/votes")
async def get_candidate_votes(candidate_id: int):
    result = storage.get_candidate_votes(candidate_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"candidate with id: {candidate_id} was not found"
        )
    return result
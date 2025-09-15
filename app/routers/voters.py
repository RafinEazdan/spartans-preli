from fastapi import APIRouter, HTTPException, status
from app.models import VoterCreate, VoterUpdate, Voter
from app.storage import storage

router = APIRouter()

# Q1: Create Voter
@router.post("/voters", status_code=status.HTTP_201_CREATED)
async def create_voter(voter: VoterCreate):
    if voter.age < 18:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"invalid age: {voter.age}, must be 18 or older"
        )
    
    result = storage.add_voter(voter.voter_id, voter.name, voter.age)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"voter with id: {voter.voter_id} already exists"
        )
    
    return {"message": "Voter created."}

# Q2: Get Voter Info
@router.get("/voters/{voter_id}", response_model=Voter)
async def get_voter(voter_id: int):
    voter = storage.get_voter(voter_id)
    if voter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"voter with id: {voter_id} was not found"
        )
    return voter

# Q3: List All Voters
@router.get("/voters")
async def list_voters():
    voters = storage.get_all_voters()
    return {"voters": voters}

# Q4: Update Voter Info
@router.put("/voters/{voter_id}", response_model=Voter)
async def update_voter(voter_id: int, voter_update: VoterUpdate):
    if voter_update.age is not None and voter_update.age < 18:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"invalid age: {voter_update.age}, must be 18 or older"
        )
    
    updated_voter = storage.update_voter(voter_id, voter_update.name, voter_update.age)
    if updated_voter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"voter with id: {voter_id} was not found"
        )
    return updated_voter

# Q5: Delete Voter
@router.delete("/voters/{voter_id}")
async def delete_voter(voter_id: int):
    success = storage.delete_voter(voter_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"voter with id: {voter_id} was not found"
        )
    return {"message": f"voter with id: {voter_id} deleted successfully"}
from fastapi import APIRouter, HTTPException
from app.models import ElectionResults, Winner, HomomorphicTallyRequest, HomomorphicTallyResponse
from app.storage import storage

router = APIRouter()

# Q11: Election Results (assumed from pattern)
@router.get("/results", response_model=ElectionResults)
async def get_results():
    return storage.get_results()

# Q12: Winning Candidate
@router.get("/results/winner", response_model=Winner)
async def get_winner():
    winners = storage.get_winner()
    return {"winners": winners}

# Homomorphic Tally With Verifiable Decryption
@router.post("/results/homomorphic", response_model=HomomorphicTallyResponse)
async def homomorphic_tally(request: HomomorphicTallyRequest):
    """
    Tally encrypted ballots without decryption and publish verifiable results.
    Uses threshold Paillier cryptography with NIZK proofs for verifiable decryption.
    """
    try:
        result = storage.homomorphic_tally(
            election_id=request.election_id,
            trustee_shares=request.trustee_decrypt_shares
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Homomorphic tally failed: {str(e)}")
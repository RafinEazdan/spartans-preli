from fastapi import APIRouter, HTTPException, status
from app.models import RankedBallot, EncryptedBallotRequest, EncryptedBallotResponse
from app.storage import storage
from datetime import datetime, timezone

router = APIRouter()

# Q19: Ranked-Choice (Schulze)
@router.post("/ballots/ranked", status_code=status.HTTP_201_CREATED)
async def submit_ranked_ballot(ballot: RankedBallot):
    ballot_id = storage.add_ranked_ballot(
        ballot.election_id,
        ballot.voter_id,
        ballot.ranking,
        ballot.timestamp
    )
    
    return {
        "ballot_id": ballot_id,
        "status": "accepted"
    }

# End-to-End Verifiable Encrypted Ballot
@router.post("/ballots/encrypted", response_model=EncryptedBallotResponse, status_code=status.HTTP_201_CREATED)
async def submit_encrypted_ballot(ballot: EncryptedBallotRequest):
    """
    Submit an end-to-end verifiable encrypted ballot.
    
    Validates zero-knowledge proofs, signatures, and nullifiers to prevent double voting.
    """
    try:
        # Validate the encrypted ballot
        result = storage.submit_encrypted_ballot(
            election_id=ballot.election_id,
            ciphertext=ballot.ciphertext,
            zk_proof=ballot.zk_proof,
            voter_pubkey=ballot.voter_pubkey,
            nullifier=ballot.nullifier,
            signature=ballot.signature
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        # Generate timestamp
        anchored_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        return EncryptedBallotResponse(
            ballot_id=result["ballot_id"],
            status=result["status"],
            nullifier=ballot.nullifier,
            anchored_at=anchored_at
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
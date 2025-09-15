from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# Voter Models
class VoterCreate(BaseModel):
    voter_id: int
    name: str
    age: int
    
    @validator('age')
    def validate_age(cls, v):
        if v < 18:
            raise ValueError(f"invalid age: {v}, must be 18 or older")
        return v

class VoterUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    
    @validator('age')
    def validate_age(cls, v):
        if v is not None and v < 18:
            raise ValueError(f"invalid age: {v}, must be 18 or older")
        return v

class Voter(BaseModel):
    voter_id: int
    name: str
    age: int
    has_voted: bool = False

# Candidate Models
class CandidateCreate(BaseModel):
    candidate_id: int
    name: str
    party: str

class Candidate(BaseModel):
    candidate_id: int
    name: str
    party: str
    votes: int = 0

# Vote Models
class VoteRequest(BaseModel):
    voter_id: int
    candidate_id: int

class WeightedVoteRequest(BaseModel):
    voter_id: int
    candidate_id: int
    weight: int = 1

class Vote(BaseModel):
    vote_id: int
    voter_id: int
    candidate_id: int
    timestamp: str
    weight: int = 1

# Results Models
class ElectionResults(BaseModel):
    total_votes: int
    candidates: List[Dict[str, Any]]

class Winner(BaseModel):
    winners: List[Dict[str, Any]]

# Timeline Models
class VoteTimeline(BaseModel):
    candidate_id: int
    timeline: List[Dict[str, Any]]

# Ranked Choice Models
class RankedBallot(BaseModel):
    election_id: str
    voter_id: int
    ranking: List[int]
    timestamp: str

# Audit Models
class AuditPlan(BaseModel):
    election_id: str
    reported_tallies: List[Dict[str, Any]]
    risk_limit_alpha: float
    audit_type: str

# Differential Privacy Analytics Models
class DPQuery(BaseModel):
    type: str
    dimension: str
    buckets: List[str]
    filter: Dict[str, Any]

class DPAnalyticsRequest(BaseModel):
    election_id: str
    query: DPQuery
    epsilon: float
    delta: float = 1e-6

class DPAnalyticsResponse(BaseModel):
    election_id: str
    query_id: str
    result: Dict[str, Any]
    privacy_parameters: Dict[str, float]
    noise_mechanism: str
    total_epsilon_spent: float

# End-to-End Verifiable Encrypted Ballot Models
class EncryptedBallotRequest(BaseModel):
    election_id: str
    ciphertext: str  # base64(Paillier_or_ElGamal_cipher)
    zk_proof: str    # base64(Groth16_or_Plonk_proof)
    voter_pubkey: str  # hex(P-256)
    nullifier: str   # hex(keccak256(signal))
    signature: str   # base64(Ed25519 signature over payload)

class EncryptedBallotResponse(BaseModel):
    ballot_id: str
    status: str
    nullifier: str
    anchored_at: str

class EncryptedBallotError(BaseModel):
    message: str

# Homomorphic Tally Models
class TrusteeDecryptShare(BaseModel):
    trustee_id: str
    share: str  # base64 encoded threshold decrypt share
    proof: str  # base64 encoded NIZK proof

class HomomorphicTallyRequest(BaseModel):
    election_id: str
    trustee_decrypt_shares: List[TrusteeDecryptShare]

class CandidateTally(BaseModel):
    candidate_id: int
    votes: int

class TransparencyInfo(BaseModel):
    ballot_merkle_root: str
    tally_method: str
    threshold: str

class HomomorphicTallyResponse(BaseModel):
    election_id: str
    encrypted_tally_root: str
    candidate_tallies: List[CandidateTally]
    decryption_proof: str
    transparency: TransparencyInfo
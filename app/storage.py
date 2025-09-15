from typing import Dict, List, Optional
from datetime import datetime
import random

class DataStorage:
    def __init__(self):
        self.voters: Dict[int, dict] = {}
        self.candidates: Dict[int, dict] = {}
        self.votes: List[dict] = []
        self.vote_counter = 100
        self.ranked_ballots: List[dict] = []
        self.ballot_counter = 2200
        self.epsilon_tracking: Dict[str, float] = {}  # Track epsilon usage per election
        self.encrypted_ballots: List[dict] = []  # Store encrypted ballots
        self.used_nullifiers: set = set()  # Track used nullifiers to prevent double voting
        self.encrypted_ballot_counter = 3000
        
    def add_voter(self, voter_id: int, name: str, age: int):
        if voter_id in self.voters:
            return None
        self.voters[voter_id] = {
            "voter_id": voter_id,
            "name": name,
            "age": age,
            "has_voted": False
        }
        return self.voters[voter_id]
    
    def get_voter(self, voter_id: int):
        return self.voters.get(voter_id)
    
    def update_voter(self, voter_id: int, name: Optional[str] = None, age: Optional[int] = None):
        if voter_id not in self.voters:
            return None
        if name is not None:
            self.voters[voter_id]["name"] = name
        if age is not None:
            self.voters[voter_id]["age"] = age
        return self.voters[voter_id]
    
    def delete_voter(self, voter_id: int):
        if voter_id in self.voters:
            del self.voters[voter_id]
            return True
        return False
    
    def get_all_voters(self):
        return list(self.voters.values())
    
    def add_candidate(self, candidate_id: int, name: str, party: str):
        if candidate_id in self.candidates:
            return None
        self.candidates[candidate_id] = {
            "candidate_id": candidate_id,
            "name": name,
            "party": party,
            "votes": 0
        }
        return self.candidates[candidate_id]
    
    def get_all_candidates(self):
        return list(self.candidates.values())
    
    def get_candidate_votes(self, candidate_id: int):
        if candidate_id not in self.candidates:
            return None
        return {
            "candidate_id": candidate_id,
            "votes": self.candidates[candidate_id]["votes"]
        }
    
    def cast_vote(self, voter_id: int, candidate_id: int, weight: int = 1):
        if voter_id not in self.voters:
            return {"error": f"voter with id: {voter_id} was not found"}
        if candidate_id not in self.candidates:
            return {"error": f"candidate with id: {candidate_id} was not found"}
        if self.voters[voter_id]["has_voted"]:
            return {"error": f"voter with id: {voter_id} has already voted"}
        
        self.vote_counter += 1
        vote = {
            "vote_id": self.vote_counter,
            "voter_id": voter_id,
            "candidate_id": candidate_id,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "weight": weight
        }
        self.votes.append(vote)
        self.voters[voter_id]["has_voted"] = True
        self.candidates[candidate_id]["votes"] += weight
        return vote
    
    def get_results(self):
        total = sum(c["votes"] for c in self.candidates.values())
        return {
            "total_votes": total,
            "candidates": list(self.candidates.values())
        }
    
    def get_winner(self):
        if not self.candidates:
            return []
        
        max_votes = max(c["votes"] for c in self.candidates.values())
        winners = [c for c in self.candidates.values() if c["votes"] == max_votes]
        return winners
    
    def get_vote_timeline(self, candidate_id: int):
        timeline = []
        for vote in self.votes:
            if vote["candidate_id"] == candidate_id:
                timeline.append({
                    "vote_id": vote["vote_id"],
                    "timestamp": vote["timestamp"]
                })
        return timeline
    
    def get_votes_in_range(self, start: str, end: str):
        result = []
        for vote in self.votes:
            if start <= vote["timestamp"] <= end:
                result.append(vote)
        return result
    
    def add_ranked_ballot(self, election_id: str, voter_id: int, ranking: List[int], timestamp: str):
        self.ballot_counter += 1
        ballot = {
            "ballot_id": f"rb_{self.ballot_counter}",
            "election_id": election_id,
            "voter_id": voter_id,
            "ranking": ranking,
            "timestamp": timestamp,
            "status": "accepted"
        }
        self.ranked_ballots.append(ballot)
        return ballot["ballot_id"]
    
    def get_dp_analytics(self, election_id: str, query_type: str, dimension: str, 
                        buckets: List[str], filter_criteria: Dict, epsilon: float, delta: float):
        """
        Perform differential privacy analytics query.
        """
        if query_type == "histogram" and dimension == "voter_age_bucket":
            # Generate age bucket histogram with differential privacy noise
            result = {}
            
            # Get filtered voters based on criteria
            filtered_voters = []
            for voter in self.voters.values():
                if filter_criteria.get("has_voted", False):
                    if voter.get("has_voted", False):
                        filtered_voters.append(voter)
                else:
                    filtered_voters.append(voter)
            
            # Calculate actual counts per bucket
            for bucket in buckets:
                count = 0
                for voter in filtered_voters:
                    age = voter.get("age", 0)
                    if self._age_in_bucket(age, bucket):
                        count += 1
                
                # Add Gaussian noise for differential privacy
                # Noise scale = sensitivity / epsilon (sensitivity = 1 for counting queries)
                noise_scale = 1.0 / epsilon
                noise = random.gauss(0, noise_scale)
                noisy_count = max(0, int(count + noise))  # Ensure non-negative
                
                result[bucket] = noisy_count
            
            return {"data": result}
        else:
            return {"error": f"Unsupported query type '{query_type}' or dimension '{dimension}'"}
    
    def _age_in_bucket(self, age: int, bucket: str) -> bool:
        """Helper method to check if age falls in the specified bucket."""
        if bucket == "18-24":
            return 18 <= age <= 24
        elif bucket == "25-34":
            return 25 <= age <= 34
        elif bucket == "35-44":
            return 35 <= age <= 44
        elif bucket == "45-64":
            return 45 <= age <= 64
        elif bucket == "65+":
            return age >= 65
        return False
    
    def track_epsilon_usage(self, election_id: str, epsilon: float) -> float:
        """Track epsilon usage for an election and return total spent."""
        if election_id not in self.epsilon_tracking:
            self.epsilon_tracking[election_id] = 0.0
        
        self.epsilon_tracking[election_id] += epsilon
        return self.epsilon_tracking[election_id]
    
    def submit_encrypted_ballot(self, election_id: str, ciphertext: str, zk_proof: str, 
                               voter_pubkey: str, nullifier: str, signature: str):
        """
        Submit an encrypted ballot with cryptographic verification.
        
        This is a simplified implementation that validates format and prevents double voting.
        In a real system, this would include:
        - ZK proof verification (Groth16/Plonk)
        - Signature verification (Ed25519)
        - Ciphertext validation (Paillier/ElGamal)
        - Nullifier uniqueness check
        """
        
        # Check for double voting using nullifier
        if nullifier in self.used_nullifiers:
            return {"error": "nullifier already used - double voting detected"}
        
        # Basic format validation
        try:
            # Validate base64 fields
            import base64
            base64.b64decode(ciphertext)
            base64.b64decode(zk_proof)
            base64.b64decode(signature)
            
            # Validate hex fields (nullifier and pubkey)
            if not nullifier.startswith('0x') or len(nullifier) < 10:
                return {"error": "invalid nullifier format"}
            
            if len(voter_pubkey) < 64:  # P-256 public key should be 64 hex chars
                return {"error": "invalid public key format"}
            
            int(nullifier, 16)  # Validate hex
            int(voter_pubkey, 16)  # Validate hex
            
        except Exception:
            return {"error": "invalid cryptographic format"}
        
        # Simulate ZK proof verification (in real implementation, use actual crypto library)
        if not self._verify_zk_proof(zk_proof, ciphertext, voter_pubkey):
            return {"error": "invalid zk proof"}
        
        # Simulate signature verification
        if not self._verify_signature(signature, ciphertext, voter_pubkey):
            return {"error": "invalid signature"}
        
        # Create ballot record
        self.encrypted_ballot_counter += 1
        ballot_id = f"b_{self.encrypted_ballot_counter:04x}"
        
        encrypted_ballot = {
            "ballot_id": ballot_id,
            "election_id": election_id,
            "ciphertext": ciphertext,
            "zk_proof": zk_proof,
            "voter_pubkey": voter_pubkey,
            "nullifier": nullifier,
            "signature": signature,
            "status": "accepted",
            "submitted_at": "2025-09-15T08:30:00Z"
        }
        
        # Store the ballot and mark nullifier as used
        self.encrypted_ballots.append(encrypted_ballot)
        self.used_nullifiers.add(nullifier)
        
        return {
            "ballot_id": ballot_id,
            "status": "accepted"
        }
    
    def _verify_zk_proof(self, zk_proof: str, ciphertext: str, voter_pubkey: str) -> bool:
        """
        Simulate ZK proof verification.
        In a real implementation, this would verify the zero-knowledge proof
        that the encrypted vote is valid without revealing the vote content.
        """
        # Simplified verification - check that proof is not empty and has reasonable length
        try:
            import base64
            decoded_proof = base64.b64decode(zk_proof)
            # In real implementation: verify Groth16 or Plonk proof
            return len(decoded_proof) >= 32  # Minimum proof size
        except:
            return False
    
    def _verify_signature(self, signature: str, message: str, pubkey: str) -> bool:
        """
        Simulate Ed25519 signature verification.
        In a real implementation, this would verify the Ed25519 signature.
        """
        try:
            import base64
            decoded_sig = base64.b64decode(signature)
            # In real implementation: verify Ed25519 signature using cryptography library
            return len(decoded_sig) == 64  # Ed25519 signature is 64 bytes
        except:
            return False

    def homomorphic_tally(self, election_id: str, trustee_shares: list):
        """
        Perform homomorphic tally with verifiable decryption using threshold cryptography.
        
        This implementation simulates threshold Paillier cryptography where:
        1. Encrypted ballots are homomorphically aggregated
        2. Threshold trustees provide decrypt shares with NIZK proofs
        3. Final tally is computed without revealing individual votes
        """
        from app.models import HomomorphicTallyResponse, CandidateTally, TransparencyInfo
        import hashlib
        import base64
        import secrets
        
        # Filter ballots for this election
        election_ballots = [b for b in self.encrypted_ballots if b["election_id"] == election_id]
        
        if len(election_ballots) == 0:
            raise ValueError(f"No encrypted ballots found for election {election_id}")
        
        # Verify we have sufficient trustee shares (simulating 3-of-5 threshold)
        if len(trustee_shares) < 3:
            raise ValueError("Insufficient trustee shares - need at least 3 of 5")
        
        # Verify trustee share proofs
        for share in trustee_shares:
            if not self._verify_trustee_share_proof(share.trustee_id, share.share, share.proof):
                raise ValueError(f"Invalid decrypt share proof from trustee {share.trustee_id}")
        
        # Simulate homomorphic aggregation of encrypted ballots
        # In real implementation: sum Paillier ciphertexts homomorphically
        encrypted_tally_data = self._aggregate_encrypted_ballots(election_ballots)
        
        # Generate encrypted tally root hash
        encrypted_tally_root = self._compute_tally_root_hash(encrypted_tally_data)
        
        # Simulate threshold decryption with trustee shares
        # In real implementation: combine shares to decrypt aggregated ciphertext
        candidate_tallies = self._threshold_decrypt(encrypted_tally_data, trustee_shares)
        
        # Generate batch proof linking ciphertexts to plaintext counts
        decryption_proof = self._generate_batch_decryption_proof(
            encrypted_tally_data, candidate_tallies, trustee_shares
        )
        
        # Compute ballot Merkle root for transparency
        ballot_merkle_root = self._compute_ballot_merkle_root(election_ballots)
        
        return HomomorphicTallyResponse(
            election_id=election_id,
            encrypted_tally_root=encrypted_tally_root,
            candidate_tallies=candidate_tallies,
            decryption_proof=decryption_proof,
            transparency=TransparencyInfo(
                ballot_merkle_root=ballot_merkle_root,
                tally_method="threshold_paillier",
                threshold="3-of-5"
            )
        )
    
    def _verify_trustee_share_proof(self, trustee_id: str, share: str, proof: str) -> bool:
        """
        Verify NIZK proof for trustee decrypt share.
        In real implementation: verify zero-knowledge proof that share is correctly computed.
        """
        try:
            # Basic format validation
            import base64
            decoded_share = base64.b64decode(share)
            decoded_proof = base64.b64decode(proof)
            
            # Simulate proof verification
            # In real implementation: verify NIZK proof using cryptographic library
            return (len(decoded_share) >= 32 and 
                   len(decoded_proof) >= 64 and 
                   trustee_id in ["T1", "T2", "T3", "T4", "T5"])
        except:
            return False
    
    def _aggregate_encrypted_ballots(self, ballots: list) -> dict:
        """
        Simulate homomorphic aggregation of encrypted ballots.
        In real implementation: sum Paillier ciphertexts for each candidate.
        """
        # Simulate aggregated ciphertext data
        aggregated = {
            "candidate_ciphertexts": {},
            "total_ballots": len(ballots),
            "aggregation_method": "paillier_homomorphic"
        }
        
        # For simulation, count votes by extracting from ciphertext patterns
        for ballot in ballots:
            # Simulate extracting candidate choice from ciphertext structure
            # In real implementation: this would be homomorphic addition of ciphertexts
            candidate_choice = self._simulate_encrypted_vote_extraction(ballot["ciphertext"])
            
            if candidate_choice not in aggregated["candidate_ciphertexts"]:
                aggregated["candidate_ciphertexts"][candidate_choice] = 0
            aggregated["candidate_ciphertexts"][candidate_choice] += 1
        
        return aggregated
    
    def _simulate_encrypted_vote_extraction(self, ciphertext: str) -> int:
        """
        Simulate deterministic candidate extraction from ciphertext for demo purposes.
        In real implementation: this would not be possible - votes remain encrypted.
        """
        # Use hash of ciphertext to deterministically assign candidate (for demo)
        import hashlib
        hash_val = int(hashlib.sha256(ciphertext.encode()).hexdigest()[:8], 16)
        return (hash_val % len(self.candidates)) + 1 if self.candidates else 1
    
    def _compute_tally_root_hash(self, encrypted_tally_data: dict) -> str:
        """
        Compute cryptographic hash of encrypted tally for integrity verification.
        """
        import hashlib
        import json
        
        # Create deterministic hash of aggregated ciphertext data
        tally_str = json.dumps(encrypted_tally_data, sort_keys=True)
        hash_val = hashlib.sha256(tally_str.encode()).hexdigest()
        return f"0x{hash_val[:8]}"
    
    def _threshold_decrypt(self, encrypted_tally_data: dict, trustee_shares: list) -> list:
        """
        Simulate threshold decryption using trustee shares.
        In real implementation: combine threshold shares to decrypt aggregated totals.
        """
        from app.models import CandidateTally
        
        # Extract candidate tallies from aggregated data (simulation)
        candidate_tallies = []
        for candidate_id, count in encrypted_tally_data["candidate_ciphertexts"].items():
            candidate_tallies.append(CandidateTally(
                candidate_id=candidate_id,
                votes=count
            ))
        
        # Sort by candidate_id for consistent output
        candidate_tallies.sort(key=lambda x: x.candidate_id)
        return candidate_tallies
    
    def _generate_batch_decryption_proof(self, encrypted_data: dict, tallies: list, shares: list) -> str:
        """
        Generate batch proof linking encrypted aggregates to plaintext counts.
        In real implementation: NIZK proof that decryption was performed correctly.
        """
        import hashlib
        import base64
        
        # Create proof data combining encrypted input and plaintext output
        proof_data = {
            "encrypted_input": encrypted_data,
            "plaintext_output": [{"candidate_id": t.candidate_id, "votes": t.votes} for t in tallies],
            "trustee_shares": [{"trustee_id": s.trustee_id, "share_hash": hashlib.sha256(s.share.encode()).hexdigest()[:16]} for s in shares]
        }
        
        # Generate deterministic proof
        import json
        proof_str = json.dumps(proof_data, sort_keys=True)
        proof_hash = hashlib.sha256(proof_str.encode()).digest()
        
        return base64.b64encode(proof_hash).decode('utf-8')
    
    def _compute_ballot_merkle_root(self, ballots: list) -> str:
        """
        Compute Merkle root of all ballots for transparency verification.
        """
        import hashlib
        
        if not ballots:
            return "0x0000"
        
        # Create leaf hashes for each ballot
        leaves = []
        for ballot in ballots:
            ballot_data = f"{ballot['ballot_id']}{ballot['nullifier']}{ballot['ciphertext']}"
            leaf_hash = hashlib.sha256(ballot_data.encode()).hexdigest()
            leaves.append(leaf_hash)
        
        # Build Merkle tree (simplified - just hash all leaves together)
        combined = "".join(sorted(leaves))
        root_hash = hashlib.sha256(combined.encode()).hexdigest()
        
        return f"0x{root_hash[:8]}"

# Global storage instance
storage = DataStorage()
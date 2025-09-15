from fastapi import APIRouter, status
from app.models import AuditPlan
import random
import math

router = APIRouter()

# Q20: Risk-Limiting Audit
@router.post("/audits/plan", status_code=status.HTTP_201_CREATED)
async def create_audit_plan(audit: AuditPlan):
    # Simulate audit plan generation
    total_votes = sum(t["votes"] for t in audit.reported_tallies)
    
    # Calculate sample size based on risk limit
    # This is a simplified calculation
    sample_size = int(math.ceil(-math.log(audit.risk_limit_alpha) * total_votes / 100))
    sample_size = min(sample_size, total_votes)  # Can't sample more than total
    
    # Generate random ballot indices for sampling
    ballot_indices = random.sample(range(1, total_votes + 1), min(sample_size, 100))
    
    return {
        "audit_id": f"audit_{audit.election_id}_{random.randint(1000, 9999)}",
        "election_id": audit.election_id,
        "sample_size": sample_size,
        "ballot_indices": sorted(ballot_indices)[:20],  # Return first 20 for brevity
        "risk_limit": audit.risk_limit_alpha,
        "audit_type": audit.audit_type,
        "status": "planned"
    }
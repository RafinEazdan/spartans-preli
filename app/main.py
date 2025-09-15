from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import voters, candidates, votes, results, audits, ballots, analytics

app = FastAPI(title="HackTheAI Voting API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(voters.router, prefix="/api", tags=["voters"])
app.include_router(candidates.router, prefix="/api", tags=["candidates"])
app.include_router(votes.router, prefix="/api", tags=["votes"])
app.include_router(results.router, prefix="/api", tags=["results"])
app.include_router(audits.router, prefix="/api", tags=["audits"])
app.include_router(ballots.router, prefix="/api", tags=["ballots"])
app.include_router(analytics.router, prefix="/api", tags=["analytics"])

@app.get("/")
async def root():
    return {"message": "HackTheAI Voting API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
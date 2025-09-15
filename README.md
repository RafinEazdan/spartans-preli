# Spartans Voting API

A FastAPI-based voting system with comprehensive validation and audit capabilities.

## Quick Start with Docker

```bash
# Extract and run the application
unzip -o spartans.zip -d spartans
cd spartans
docker compose up -d --build
```

The API will be available at:
- **Main API**: 0.0.0.0:8000
- **API Documentation**: 0.0.0.0:8000/docs
- **Health Check**: 0.0.0.0:8000/health

## Testing the API

After the container starts, you can test the API:

```bash
# Run the test script
python test_api.py

# Or test manually
curl http://localhost:8000/health
```

## API Features

- ✅ **Voter Management**: Create, read, update, delete voters
- ✅ **Candidate Management**: Register and manage candidates  
- ✅ **Vote Casting**: Standard and weighted voting
- ✅ **Election Results**: Real-time results and analytics
- ✅ **Audit Trail**: Vote timeline and verification
- ✅ **Ranked Choice Voting**: Ballot support for complex elections
- ✅ **End-to-End Verifiable Voting**: Encrypted ballots with ZK proofs
- ✅ **Differential Privacy**: Privacy-preserving analytics with noise
- ✅ **Input Validation**: Comprehensive data validation
- ✅ **CORS Support**: Ready for web frontend integration

## Key Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation
- `POST /api/voters` - Create voter
- `POST /api/candidates` - Register candidate
- `GET /api/candidates/{candidate_id}/votes` - Get candidate vote count
- `POST /api/votes` - Cast vote
- `POST /api/ballots/encrypted` - Submit encrypted verifiable ballot
- `POST /api/analytics/dp` - Differential privacy analytics
- `GET /api/results` - Get election results

## Stop the Service

```bash
docker compose down
```

## Technical Details

- **Framework**: FastAPI with automatic OpenAPI documentation
- **Python**: 3.12
- **Port**: 8000
- **Storage**: In-memory (for demonstration)
- **Validation**: Custom validators for data integrity
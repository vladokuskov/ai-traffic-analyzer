from fastapi import APIRouter, FastAPI
from app.db import collection

# Initialize the API router for routing the API endpoints
router = APIRouter()


@router.get("/anomalies")
def get_anomalies():
    """
    Endpoint to retrieve all anomalies from the database.
    It queries the 'detections' collection and excludes the '_id' field in the result.

    Returns:
    A list of anomalies from the MongoDB collection without the '_id' field.
    """
    return list(collection.find({}, {'_id': 0}))


@router.get("/anomalies/latest")
def get_latest_anomaly():
    """
    Endpoint to retrieve the latest anomaly from the database.
    It fetches the most recent document (sorted by _id in descending order)
    and excludes the '_id' field in the result.

    Returns:
    The latest anomaly document from the MongoDB collection without the '_id' field.
    """
    return collection.find_one(sort=[("_id", -1)], projection={'_id': 0})


# Create the FastAPI app instance
app = FastAPI()

# Include the router with the appropriate prefix in the FastAPI application
app.include_router(router)

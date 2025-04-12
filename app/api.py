from fastapi import APIRouter, FastAPI
from app.db import collection

router = APIRouter()


@router.get("/anomalies")
def get_anomalies():
    return list(collection.find({}, {'_id': 0}))


@router.get("/anomalies/latest")
def get_latest_anomaly():
    return collection.find_one(sort=[("_id", -1)], projection={'_id': 0})


# Create the FastAPI app instance
app = FastAPI()

# Include the router with the appropriate prefix
app.include_router(router)

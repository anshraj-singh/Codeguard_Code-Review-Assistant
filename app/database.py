from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.config import MONGODB_URL, DATABASE_NAME


client = None
reviews_collection = None

if MONGODB_URL:
    try:
        client = MongoClient(
            MONGODB_URL,
            serverSelectionTimeoutMS=5000
        )

        database = client[DATABASE_NAME]
        reviews_collection = database["reviews"]

        # Check connection
        client.admin.command("ping")

        print("MongoDB connected successfully")

    except PyMongoError as error:
        print(f"MongoDB connection failed: {error}")
        client = None
        reviews_collection = None


def save_review(review: dict):
    if reviews_collection is None:
        raise RuntimeError("MongoDB is not connected")

    reviews_collection.insert_one(review)


def get_all_reviews():
    if reviews_collection is None:
        raise RuntimeError("MongoDB is not connected")

    return list(
        reviews_collection.find(
            {},
            {"_id": 0}
        ).sort("created_at", -1)
    )


def get_review_by_id(review_id: str):
    if reviews_collection is None:
        raise RuntimeError("MongoDB is not connected")

    return reviews_collection.find_one(
        {"review_id": review_id},
        {"_id": 0}
    )
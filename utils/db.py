import os
import hashlib
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:

    raise ValueError(
        "MONGODB_URI is missing from .env"
    )
client = MongoClient(
    MONGODB_URI
)


db = client["safar"]
trips_collection = db["trips"]
expenses_collection = db["expenses"]
journal_collection = db["journal"]
users_collection = db["users"]

# -----------------------------
# Trips
# -----------------------------

def save_trip(trip):

    result = trips_collection.insert_one(
        trip
    )

    return str(
        result.inserted_id
    )

def get_trips(user_id):

    return list(
        trips_collection.find(
            {"user_id": user_id}
        ).sort(
            "_id",
            -1
        )
    )

# -----------------------------
# Journal
# -----------------------------

def save_journal(entry):

    result = journal_collection.insert_one(
        entry
    )

    return str(
        result.inserted_id
    )


def get_journal_entries(trip_id):

    return list(
        journal_collection.find(
            {
                "trip_id": trip_id
            }
        ).sort(
            "_id",
            -1
        )
    )


def count_journal_entries(trip_id):

    return journal_collection.count_documents(
        {
            "trip_id": trip_id
        }
    )


# -----------------------------
# Expenses
# -----------------------------

def save_expense(expense):

    result = expenses_collection.insert_one(
        expense
    )

    return str(
        result.inserted_id
    )


def get_expenses(trip_id):

    return list(
        expenses_collection.find(
            {
                "trip_id": trip_id
            }
        ).sort(
            "_id",
            -1
        )
    )
def delete_expense(expense_id):

    from bson import ObjectId

    result = expenses_collection.delete_one(
        {
            "_id": ObjectId(expense_id)
        }
    )

    return result.deleted_count
def register_user(name, email, password):

    existing_user = users_collection.find_one(
        {"email": email}
    )

    if existing_user:
        return False

    password_hash = hashlib.sha256(
        password.encode()
    ).hexdigest()

    users_collection.insert_one({
        "name": name,
        "email": email,
        "password": password_hash
    })

    return True


def login_user(email, password):

    password_hash = hashlib.sha256(
        password.encode()
    ).hexdigest()

    user = users_collection.find_one({
        "email": email,
        "password": password_hash
    })

    return user
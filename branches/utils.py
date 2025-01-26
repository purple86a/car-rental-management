from pymongo import MongoClient
from dotenv import load_dotenv
import os
import utils
from typing import Optional

mongo_client = MongoClient(os.getenv("MONGODB_URL"))

load_dotenv()

sysdb = mongo_client[os.getenv("DATABASE_NAME")]
branches = sysdb[os.getenv("BRANCH_COLLECTION")]

vechiles = sysdb[os.getenv("VECHILE_COLLECTION")]
rentals = sysdb[os.getenv("RENTAL_COLLECTION")]
branches = sysdb[os.getenv("BRANCH_COLLECTION")]


class branch:

    def __init__(self, name: str, location: str, contact_number: str):
        self._branch_id = "branch" + utils.generate_id()
        self._name = name
        self._location = location
        self._contact_number = contact_number

    def save_to_collection(self):
        branches.insert_one({
            "branch_id": self._branch_id,
            "name": self._name,
            "location": self._location,
            "contact_number": self._contact_number,
        })
        return {
            "message":
            f"Branch with branch id {self._branch_id} created successfully!"
        }

    @staticmethod
    def create_branch(name: str, location: str, contact_number: str):
        branch_id = "branch" + utils.generate_id()
        branches.insert_one({
            "branch_id": branch_id,
            "name": name,

            "location": location,
            "contact_number": contact_number,
        })
        return {
            "message":
            f"Branch with branch id {branch_id} created successfully!"
        }

    @staticmethod
    def update_branch_id(old_branch_id: str, new_branch_id: str):
        if branches.find_one({"branch_id": new_branch_id}):
            raise Exception(
                f"Branch with branch id {new_branch_id} already exists")
        branches.update_one({"branch_id": old_branch_id},
                            {"$set": {
                                "branch_id": new_branch_id
                            }})
        rentals.update_many({"location": old_branch_id},
                            {"$set": {
                                "branch_id": new_branch_id
                            }})
        return {
            "message":
            f"Branch with branch id {old_branch_id} updated to {new_branch_id} successfully!"
        }

    @staticmethod
    def update_name(branch_id: str, name: str):
        branches.update_one({"branch_id": branch_id}, {"$set": {"name": name}})
        rentals.update_many({"location": name}, {"$set": {"name": name}})
        return {
            "message":
            f"Branch with branch id {branch_id} name updated to {name} successfully!"
        }

    @staticmethod
    def update_location(branch_id: str, location: str):
        branches.update_one({"branch_id": branch_id},
                            {"$set": {
                                "location": location
                            }})
        return {
            "message":
            f"Branch with branch id {branch_id} location updated to {location} successfully!"
        }

    @staticmethod
    def update_contact_number(branch_id: str, contact_number: str):
        branches.update_one({"branch_id": branch_id},
                            {"$set": {
                                "contact_number": contact_number
                            }})
        return {
            "message":
            f"Branch with branch id {branch_id} contact number updated to {contact_number} successfully!"
        }

    @staticmethod
    def delete_branch(branch_id: str, name: Optional[str] = None):
        branches.delete_one({"branch_id": branch_id})
        vechiles.delete_many({"location": branch_id})
        if name is not None:
            vechiles.delete_many({"location": name})
        return {
            "message":
            f"Branch with branch id {branch_id} deleted successfully!"
        }


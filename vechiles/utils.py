from datetime import datetime
from typing import Optional
import utils
from dotenv import load_dotenv
import os
from enum import Enum
from pymongo import MongoClient
from bson.json_util import dumps
import json


mongo_client = MongoClient(os.getenv("MONGODB_URL"))

load_dotenv()

sysdb = mongo_client[os.getenv("DATABASE_NAME")]
branches = sysdb[os.getenv("BRANCH_COLLECTION")]

users = sysdb[os.getenv("USER_COLLECTION")]
vechiles = sysdb[os.getenv("VECHILE_COLLECTION")]
rentals = sysdb[os.getenv("RENTAL_COLLECTION")]
rental_requests = sysdb[os.getenv("RENTAL_REQUEST_COLLECTION")]
branches = sysdb[os.getenv("BRANCH_COLLECTION")]



class vechiletype(Enum):
    CAR = "CAR"
    TRUCK = "TRUCK"
    VAN = "VAN"
    MOTORCYCLE = "MOTORCYCLE"


class availability_status(Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"



class vechile:

    def __init__(
        self,
        make: str,
        model: str,
        type: vechiletype,
        availability_status: availability_status,
        location: str,
        rental_per_day: Optional[float] = 0.0,
    ):
        
        if (not branches.find_one({"branch_id": location})) and (not branches.find_one({"name": location})):
            raise Exception(f"Entered branch does not exist")
        
        self._vechile_id = "vec" + utils.generate_id()
        self._make = make
        self._model = model
        self._type = type
        self._availability_status = availability_status
        self._location = location
        self._rental_per_day = rental_per_day

    def save_to_collection(self):
        vechiles.insert_one({
            "vechile_id": self._vechile_id,
            "make": self._make,
            "model": self._model,
            "type": self._type.value,
            "rental_per_day": self._rental_per_day,
            "availability_status": self._availability_status.value,
            "location": self._location,
        })
        return {
            "message":
            f"Vechile with vechile id {self._vechile_id} created successfully!"
        }

    def update_status(self, new_availability_status: availability_status):
        vechiles.update_one(
            {"vechile_id": self._vechile_id},
            {"$set": {
                "availability_status": new_availability_status.value
            }},
        )
        return {
            "message":
            f"Vechile with vechile id {self._vechile_id} availability status updated successfully!"
        }

    @staticmethod
    def create_vechile(
        make: str,
        model: str,
        type: vechiletype,
        availability_status: availability_status,
        location: str,
        rental_per_day: Optional[float] = 0.0,
    ):
        
        if (not branches.find_one({"branch_id": location})) and (not branches.find_one({"name": location})):
            raise Exception(f"Entered branch does not exist")
        
        vechile_id = "vec" + utils.generate_id()
        vechiles.insert_one({
            "vechile_id": vechile_id,
            "make": make,
            "model": model,
            "type": type.value,
            "rental_per_day": rental_per_day,
            "availability_status": availability_status.value,
            "location": location,
        })
        return {
            "message":
            f"Vechile with vechile id {vechile_id} created successfully!"
        }

    @staticmethod
    def update_vechile_id(new_vechile_id: str, old_vechile_id: str):
        if vechiles.find_one({"vechile_id": new_vechile_id}):
            raise Exception(
                f"Vechile with vechile id {new_vechile_id} already exists")
        vechiles.update_one({"vechile_id": old_vechile_id},
                            {"$set": {
                                "vechile_id": new_vechile_id
                            }})
        rentals.update_many({"vechile_id": old_vechile_id},
                            {"$set": {
                                "vechile_id": new_vechile_id
                            }})
        return {
            "message":
            f"Vechile with vechile id {old_vechile_id} updated to {new_vechile_id} successfully!"
        }

    @staticmethod
    def update_make(vechile_id: str, new_make: str):
        vechiles.update_one({"vechile_id": vechile_id},
                            {"$set": {
                                "make": new_make
                            }})
        return {
            "message":
            f"Vechile with vechile id {vechile_id} make updated successfully!"
        }

    @staticmethod
    def update_model(vechile_id: str, new_model: str):
        vechiles.update_one({"vechile_id": vechile_id},
                            {"$set": {
                                "model": new_model
                            }})

    @staticmethod
    def update_type(vechile_id: str, new_type: vechiletype):
        vechiles.update_one({"vechile_id": vechile_id},
                            {"$set": {
                                "type": new_type.value
                            }})

    @staticmethod
    def update_rental_per_day(vechile_id: str, new_rental_per_day: float):
        if new_rental_per_day < 0:
            raise Exception("Rental per day cannot be negative")
        vechiles.update_one({"vechile_id": vechile_id},
                            {"$set": {
                                "rental_per_day": new_rental_per_day
                            }})
        return {
            "message":
            f"Vechile with vechile id {vechile_id} rental per day updated successfully!"
        }

    @staticmethod
    def update_availability_status(
            vechile_id: str, new_availability_status: availability_status):
        vechiles.update_one(
            {"vechile_id": vechile_id},
            {"$set": {
                "availability_status": new_availability_status.value
            }},
        )
        return {
            "message":
            f"Vechile with vechile id {vechile_id} availability status updated successfully!"
        }

    @staticmethod
    def update_location(vechile_id: str, location: str):
        
        if (not branches.find_one({"branch_id": location})) and (not branches.find_one({"name": location})):
            raise Exception(f"Entered branch does not exist")
        
        vechiles.update_one({"vechile_id": vechile_id},
                            {"$set": {
                                "location": location
                            }})
        return {
            "message":
            f"Vechile with vechile id {vechile_id} location updated successfully!"
        }

    @staticmethod
    def delete_vechile(vechile_id: str):
        vechiles.delete_one({"vechile_id": vechile_id})
        rentals.delete_many({"vechile_id": vechile_id})
        return {
            "message":
            f"Vechile with vechile id {vechile_id} deleted successfully!"
        }

    @staticmethod
    def browse_vechiles(
        type: Optional[str] = None,
        price: Optional[float] = None,
        location: Optional[str] = None,
    ):
        if type and price and location:
            return json.loads(
                dumps(
                    vechiles.find({
                        "type": type,
                        "rental_per_day": price,
                        "location": location
                    })))
        elif type and price:
            return json.loads(
                dumps(vechiles.find({
                    "type": type,
                    "rental_per_day": price
                })))
        elif type and location:
            return json.loads(
                dumps(vechiles.find({
                    "type": type,
                    "location": location
                })))
        elif price and location:
            return json.loads(
                dumps(
                    vechiles.find({
                        "rental_per_day": price,
                        "location": location
                    })))
        elif type:
            return json.loads(dumps(vechiles.find({"type": type})))
        elif price:
            return json.loads(dumps(vechiles.find({"rental_per_day": price})))
        elif location:
            return json.loads(dumps(vechiles.find({"location": location})))
        else:
            return json.loads(dumps(vechiles.find()))

    @staticmethod
    def calculate_total_cost(vechile_id: str, rental_start_date: str,
                             rental_end_date: str):
        
        if not vechiles.find_one({"vechile_id": vechile_id}):
            return {
                "message":
                f"Vechile with vechile id {vechile_id} does not exist"
            }
        return (
            vechiles.find_one({"vechile_id": vechile_id})["rental_per_day"] *
            (rental_end_date - rental_start_date).days)

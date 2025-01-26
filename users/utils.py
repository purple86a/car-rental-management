from datetime import datetime, timedelta, timezone
from typing import Optional
import utils
from dotenv import load_dotenv
import os
from enum import Enum
from pymongo import MongoClient
from bson.json_util import dumps
import json
from passlib.context import CryptContext
import bcrypt
from fastapi import HTTPException, status
from jose import jwt


mongo_client = MongoClient(os.getenv("MONGODB_URL"))

load_dotenv()

sysdb = mongo_client[os.getenv("DATABASE_NAME")]
branches = sysdb[os.getenv("BRANCH_COLLECTION")]

users = sysdb[os.getenv("USER_COLLECTION")]
vechiles = sysdb[os.getenv("VECHILE_COLLECTION")]
rentals = sysdb[os.getenv("RENTAL_COLLECTION")]


SECRET_KEY = os.getenv("SECRET_KEY") # run `openssl rand -hex 32`
ALGORITHM = os.getenv("ALGORITHM")




class usertype(Enum):
    CUSTOMER = "CUSTOMER"
    EMPLOYEE = "EMPLOYEE"


class user:
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        password = password.encode('utf-8')
        return bcrypt.hashpw(password, bcrypt.gensalt())
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        plain_password = plain_password.encode('utf-8')
        return bcrypt.checkpw(plain_password, hashed_password)
    

    def __init__(self, name: str, password: str, role: usertype):
        self._user_id = [
            ("cust" + utils.generate_id() if role == usertype.CUSTOMER.value else "emp" +
             utils.generate_id())
        ]
        self._name = name
        self._password = user.get_password_hash(password)
        self._role = role
        self._is_active = True

    def save_to_collection(self):
        users.insert_one({
            "user_id": self._user_id,
            "name": self._name,
            "password": user.get_password_hash(self._password),
            "role": self._role.value,
            "is_active": self._is_active
        })
        return {
            "message":
            f"User with user id {self._user_id} created successfully!"
        }


    def is_obj_customer(self):
        return self._role == usertype.CUSTOMER

    def is_obj_employee(self):
        return self._role == usertype.EMPLOYEE

    @staticmethod
    def create_user(name: str, password: str, role: usertype):
        user_id = [
            ("cust" + utils.generate_id() if role == usertype.CUSTOMER else "emp" +
             utils.generate_id())
        ]
        users.insert_one({
            "user_id": user_id,
            "name": name,
            "password": user.get_password_hash(password),
            "role": role.value,
            "is_active": True
        })
        return {
            "message": f"User with user id {user_id} created successfully! Please note it down for logging in later :)"
        }
        
    @staticmethod
    def get_user(user_id: str):
        return users.find_one({"user_id": user_id})

    @staticmethod
    def update_user_id(old_user_id: str, new_user_id: str):
        if users.find_one({"user_id": new_user_id}):
            raise Exception(f"User with user id {new_user_id} already exists")
        users.update_one({"user_id": old_user_id},
                         {"$set": {
                             "user_id": new_user_id
                         }})
        rentals.update_many({"user_id": old_user_id},
                            {"$set": {
                                "user_id": new_user_id
                            }})
        return {
            "message":
            f"User with user id {old_user_id} updated to {new_user_id} successfully!"
        }

    @staticmethod
    def update_name(new_name: str, old_name: str):
        users.update_one({"name": old_name}, {"$set": {"name": new_name}})
        return {
            "message":
            f"User with name {old_name} updated to {new_name} successfully!"
        }

    @staticmethod
    def update_password(user_id, password: str):
        users.update_one({"user_id": user_id},
                         {"$set": {
                             "password": user.get_password_hash(password)
                         }})
        return {
            "message":
            f"User with user id {user_id} password updated successfully!"
        }

    @staticmethod
    def update_role(user_id, role: usertype):
        users.update_one({"user_id": user_id},
                         {"$set": {
                             "role": role.value
                         }})
        return {
            "message":
            f"User with user id {user_id} role updated successfully!"
        }
        

    @staticmethod
    def update_is_active(user_id, is_active: bool):
        users.update_one({"user_id": user_id},
                         {"$set": {
                             "is_active": is_active
                         }})
        return {
            "message":
            f"User with user id {user_id} is_active updated successfully!"
        }
    @staticmethod
    def delete_user(user_id: str):
        users.delete_one({"user_id": user_id})
        rentals.delete_many({"user_id": user_id})
        return {
            "message": f"User with user id {user_id} deleted successfully!"
        }


    @staticmethod
    def is_employee(user_id: str):
        return users.find_one({"user_id":
                               user_id})["role"] == usertype.EMPLOYEE.value

    @staticmethod
    def is_customer(user_id: str):
        return users.find_one({"user_id":
                               user_id})["role"] == usertype.CUSTOMER.value
        
        
    @staticmethod
    def create_access_token(user_id: str, expires_delta: timedelta):
        encode = {"sub": user_id, "customer": user.is_customer(user_id), "employee": user.is_employee(user_id)}
        expires = datetime.now(timezone.utc) + expires_delta
        encode.update({"exp": expires})
        return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

        
    @staticmethod
    def authenticate_user(user_id: str, password: str):
        user_doc = users.find_one({"user_id": user_id})
        if not user_doc or not user.verify_password(password, user_doc["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        token = user.create_access_token(user_id, timedelta(minutes=20))
        
        return {"access_token": token, "token_type": "bearer"} 
    
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends, status

from rentals.utils import rental as rentalClass
from rentals.utils import rental_request as rental_requestClass
from vechiles.utils import vechile as vechileClass
from vechiles.utils import vechiletype, availability_status
from users.auth import get_current_user
from notification_routes import push_to_connected_customer_websockets, push_to_connected_employee_websockets

from typing import Annotated, Literal



user_dependency = Annotated[dict, Depends(get_current_user)]

employees_router = APIRouter()



@employees_router.get("/rentals/view_rental_requests")
async def view_rental_requests(user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication Failed")
    if user["is_customer"] is True:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not an employee")
    return rental_requestClass.view_rental_requests()


@employees_router.put(
    "/rentals/update_rental_request_status/{rental_request_id}")
async def update_rental_request_status(rental_request_id: str,
                                       status: Literal["ACCEPT", "REJECT"],
                                       user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication Failed")
    if user["is_customer"] is True:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not an employee")
    if status == "ACCEPT":
        results = rental_requestClass.accept_rental_request(rental_request_id)
        await push_to_connected_employee_websockets(f"Rental Request With ID {rental_request_id} Accepted by {user['id']} !!!")
        return results
    elif status == "REJECT":
        return rental_requestClass.reject_rental_request(rental_request_id)


@employees_router.get("/vechiles/view_rental_history/{vechile_id}")
async def view_rental_history(vechile_id: str, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication Failed")
    if user["is_customer"] is True:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not an employee")
    return rentalClass.view_rental_history(vechile_id)
    
    
@employees_router.post("/vechiles/add_vechile")
async def add_vechile(make: str, model: str, type: Literal["CAR", "TRUCK", "VAN", "MOTORCYCLE"], 
                      status: Literal["AVAILABLE", "UNAVAILABLE"], location: str, 
                      rental_per_day: float, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication Failed")
    if user["is_customer"] is True:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not an employee")
        
    if type == "CAR":
        type = vechiletype.CAR
    elif type == "TRUCK":
        type = vechiletype.TRUCK
    elif type == "VAN":
        type = vechiletype.VAN
    elif type == "MOTORCYCLE":
        type = vechiletype.MOTORCYCLE
    

    if status == "AVAILABLE":
        status = availability_status.AVAILABLE
    elif status == "UNAVAILABLE":
        status = availability_status.UNAVAILABLE

    rental_per_day = float(rental_per_day)

    return vechileClass.create_vechile(make, model, type, status, location, rental_per_day)


@employees_router.put("/vechiles/update_vechile_info/{vechile_id}")
async def update_vechile_info(vechile_id: str,
                              field: Literal["vechile_id", "make", "model",
                                             "type", "rental_per_day",
                                             "availability_status",
                                             "location"], new_value,
                              user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication Failed")
    if user["is_customer"] is True:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not an employee")

    if field == "vechile_id":
        if type(new_value) == str:
            return vechileClass.update_vechile_id(vechile_id, new_value)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="vechile_id must be a string")

    elif field == "make":
        if type(new_value) == str:
            return vechileClass.update_make(vechile_id, new_value)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="make must be a string")

    elif field == "model":
        if type(new_value) == str:
            return vechileClass.update_model(vechile_id, new_value)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="model must be a string")

    elif field == "type":
        if type(new_value) == str:
            if new_value == "CAR":
                return vechileClass.update_type(vechile_id, vechiletype.CAR)
            elif new_value == "TRUCK":
                return vechileClass.update_type(vechile_id, vechiletype.TRUCK)
            elif new_value == "VAN":
                return vechileClass.update_type(vechile_id, vechiletype.VAN)
            elif new_value == "MOTORCYCLE":
                return vechileClass.update_type(vechile_id,
                                                vechiletype.MOTORCYCLE)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="type must be one of CAR, TRUCK, VAN, MOTORCYCLE")

    elif field == "rental_per_day":
        if float(new_value):
            return vechileClass.update_rental_per_day(vechile_id,
                                                      float(new_value))

    elif field == "availability_status":
        if type(new_value) == str:
            if new_value == "AVAILABLE":
                result = vechileClass.update_availability_status(vechile_id, availability_status.AVAILABLE)
                await push_to_connected_customer_websockets(f"Vechile {vechile_id} status has been updated to {new_value}")
                return result
            elif new_value == "UNAVAILABLE":
                result = vechileClass.update_availability_status(vechile_id, availability_status.UNAVAILABLE)
                await push_to_connected_customer_websockets(f"Vechile {vechile_id} status has been updated to {new_value}")
                return result
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=
                    "availability_status must be one of AVAILABLE, UNAVAILABLE"
                )
        

    elif field == "location":
        if type(new_value) == str:
            return vechileClass.update_location(vechile_id, new_value)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="location must be a string")


@employees_router.delete("/vechiles/delete_vechile/{vechile_id}")
async def delete_vechile(vechile_id: str, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication Failed")
    if user["is_customer"] is True:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not an employee")
    return vechileClass.delete_vechile(vechile_id)

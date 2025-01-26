from fastapi import APIRouter, HTTPException, Depends, status
from users.auth import get_current_user
from typing import Annotated, Literal, Optional
from vechiles.utils import vechile as vechileClass
from rentals.utils import rental_request as rental_requestClass
from notification_routes import push_to_connected_employee_websockets


user_dependency =  Annotated[dict, Depends(get_current_user)]


customers_router = APIRouter()

@customers_router.get("/vechiles/browse_vechiles")
async def browse_vechiles(user: user_dependency, 
                          type: Optional[Literal["CAR", "TRUCK", "VAN", "MOTORCYCLE"]] = None, 
                          price: Optional[float] = None, location: Optional[str] = None):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication Failed")
    if user["is_customer"] is False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not a customer")
        
    return vechileClass.browse_vechiles(type, price, location)


@customers_router.post("/vechiles/{vechile_id}/request_rental")
async def request_rental(vechile_id: str, rental_start_date: str, 
                         rental_end_date: str, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication Failed")
    if user["is_customer"] is False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not a customer")
    customer_id = user["id"]
    results = rental_requestClass.create_rental_request(vechile_id, customer_id, rental_start_date, rental_end_date)
    await push_to_connected_employee_websockets(f"A New Rental Request Was Just Created by {customer_id} !!!")
    return results





from fastapi import FastAPI, Request
import time
from users.auth import users_router
from users.employees.routes import employees_router
from users.customers.routes import customers_router
from notification_routes import notification_router
from kafka_producer import KafkaEventProducer
from dotenv import load_dotenv
import os

load_dotenv()
version = os.getenv('VERSION')

description = """
This is a Real-Time Vehicle Rental Management System REST API. The system is a role-based
system that allows users to register, login, access different endpoints based on their role
and logout. Other features include recieving rea-time notifications for different events
based on the users role. The system also uses Kafka for event logging. The system supports
two roles: Customers and Employees. The endpoints each role can access are below. The user
must first sign in or register and sign in to use these endpoints. As for the notification
endpoint the following is to be done: \n
1- sign in or register then sign in \n
2- copy your token under the autherization endpoints \n
3- paste the token to reciecve the notification page URL \n
4- access the URL and recieve life notifications if any of the actions have been done that you are to be informed about. \n
Users of different roles recieve different notifications. For employees: if new rental 
requests or a rental request is accepted a notification is to be recieved. As for customers:
if a vechile status is changed a notification is to be recieved. \n

PLEASE MAKE SURE YOU ARE RUNNING MONGODB FOR THE SYSTEM TO WORK \n
To run MongoDB paste the following in file explorer: `C:\\DEVEL\\stage\\var\\scripts\\start-mongodb.bat`

## Endpoints

### Authentication Endpoints

- *`/api/{version}/auth/register`*: enter name, password and role to register in database. user_id will be generated and returned for the user. \n
- *`/api/{version}/auth/token`*: enter user_id (username) and password (password) to get access token and be autherized to use other endpoints. \n

### Employee Endpoints
Only works if user has been authenticated and is an employee. \n
- *`/api/{version}/employees/rentals/view_rental_requests`*: view all the rental requests. This endpoint does not require input. \n
- *`/api/{version}/employees/vechiles/view_rental_history/{vechile_id}`*: view the rental history of a vechile. A valid vechile id must be entered for this to work.\n
- *`/api/{version}/employees/vechiles/update_vechile_info/{vechile_id}`*: update the information of a vechile. A valid vechile id must be entered, the field to update must be chosen
and the new value must be entered for this to work. The entered value must follow a pattern for some of the fields for that an appropriate error is returned with the allowed values. \n
- *`/api/{version}/employees/vechiles/delete_vechile/{vechile_id}`*: delete a vechile. A valid vechile id must be entered for this to work. \n

### Customer Endpoints
Only works if user has been authenticated and is a customer. \n
- *`/api/{version}/customers/vechiles/browse_vechiles`*: view all the vechiles. This endpoint does not require input. \n
- *`/api/{version}/customers/vechiles/{vechile_id}/request_rental`*: send a rental request for a specific vechile. A valid vechile id must be entered, the rental start date and the rental end date must be entered for this to work. \n

### Notification Endpoints
Only works if user has been authenticated. \n
- *`/notifications/{token}`*: get and view live notifications. A valid token must be entered for the URL to be generated. \n

## Kafka
When starting the system make sure to have the Kafka server running. To run Kafka Apache for system log events please do the following: \n
1- Start Kafka Zookeeper with the following command: `C:\\kafka_2.12-3.9.0\\bin\\windows\\zookeeper-server-start.bat C:\\kafka_2.12-3.9.0\\config\\zookeeper.properties` (if virtual env active please deactivate) \n
2- Start Kafka Server with the following command: `C:\\kafka_2.12-3.9.0\\bin\\windows\\kafka-server-start.bat C:\\kafka_2.12-3.9.0\\config\\server.properties` \n
Make sure the config files are changed to the correct paths for the log folders. The `kafka_listener_for_log_checking.py` script can be used to check the logs.

"""


app = FastAPI(
    title="Real-Time Vehicle Rental Management System REST API",
    description=description,
    version=version,
    swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"}, 
    deepLinking = True)



producer = KafkaEventProducer(topic="system-events")


@app.middleware("http")
async def log_event_middleware(request: Request, call_next):
    """
    Middleware to log system events for each endpoint access.
    """
    start_time = time.time()
    
    # Process the request
    response = await call_next(request)
    
    # Log event after processing the request
    event = {
        "event_name": "endpoint_accessed",
        "endpoint": request.url.path,
        "method": request.method,
        "timestamp": int(start_time),
    }
    producer.send_event(event)
    return response



# activate env in cmd terminal then run `.\.venv\Scripts\uvicorn main:app --reload`   PS sometimes doesnt work in powershell


app.include_router(users_router, prefix="/api/{version}/auth", tags=["Authentication"])
app.include_router(employees_router, prefix="/api/{version}/employees", tags=["Employees"])
app.include_router(customers_router, prefix="/api/{version}/customers", tags=["Customers"])
app.include_router(notification_router, tags=["Notification"])




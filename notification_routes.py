
from typing import List, Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.responses import HTMLResponse
# from starlette.websockets import WebSocketDisconnect

from users.auth import get_current_user

user_dependency =  Annotated[dict, Depends(get_current_user)]


notification_router = APIRouter()

employee_html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Employees Notifications</title>
        <style>
        html, body {
            background-color: #2e2e2e; 
            color: white; 
            font-family: monospace;
        }
        ul {
            font-family: monospace;
            list-style: none;
            padding-left: 0;
        }

        li {
            font-size: 1.3em;
            line-height: 1.5em;
            display: flex;
            align-items: center;
        }

        li::before {
            content: '⭐';
            font-size: 1.5em;
            vertical-align: middle; 
            margin-right: 0.5em; 
        }

    </style>
    </head>
    <body>
        <h1>Employees Notifications</h1>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws/employees?token=${token}");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
                
                if (messages.firstChild) {
                    messages.insertBefore(message, messages.firstChild);
                } else {
                    messages.appendChild(message);
                }
            };
        </script>
    </body>
</html>
"""

customer_html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Customers Notifications</title>
        <style>
        
        html, body {
            background-color: #2e2e2e; 
            color: white; 
            font-family: monospace;
        }
        
        ul {
            list-style: none;
            padding-left: 0;
        }

        li {
            font-size: 1.3em;
            line-height: 1.5em;
            display: flex;
            align-items: center;
        }

        li::before {
            content: '⭐';
            font-size: 1.5em;
            vertical-align: middle; 
            margin-right: 0.5em; 
        }

    </style>
    </head>
    <body>
        <h1>Customers Notifications</h1>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws/customers?token=${token}");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
                
                if (messages.firstChild) {
                    messages.insertBefore(message, messages.firstChild);
                } else {
                    messages.appendChild(message);
                }
            };
        </script>
    </body>
</html>
"""


@notification_router.get("/notifications/{token}")
async def get(token:str):
    user = await get_current_user(token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication Failed")
    if user["is_customer"]:
        return HTMLResponse(customer_html, headers={"token": token})
    
    if user["is_employee"]:
        return HTMLResponse(employee_html, headers={"token": token})
    


class Notifier:
    def __init__(self):
        self.connections: List[WebSocket] = []
        self.generator = self.get_notification_generator()

    async def get_notification_generator(self):
        while True:
            message = yield
            await self._notify(message)

    async def push(self, msg: str):
        await self.generator.asend(msg)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def remove(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def _notify(self, message: str):
        living_connections = []
        while len(self.connections) > 0:
            # Looping like this is necessary in case a disconnection is handled
            # during await websocket.send_text(message)
            websocket = self.connections.pop()
            await websocket.send_text(message)
            living_connections.append(websocket)
        self.connections = living_connections


customer_notifier = Notifier()
employee_notifier = Notifier()


@notification_router.websocket("/ws/customers")
async def websocket_endpoint(websocket: WebSocket):
    await customer_notifier.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        customer_notifier.remove(websocket)
        
@notification_router.websocket("/ws/employees")
async def websocket_endpoint(websocket: WebSocket):
    await employee_notifier.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        employee_notifier.remove(websocket)
        
        
async def push_to_connected_customer_websockets(message: str):
    await customer_notifier.push(f"New notification! : {message}")
    
async def push_to_connected_employee_websockets(message: str):
    await employee_notifier.push(f"New notification! : {message}")


@notification_router.on_event("startup")
async def startup():
    # Prime the push notification generator
    await customer_notifier.generator.asend(None)
    await employee_notifier.generator.asend(None)

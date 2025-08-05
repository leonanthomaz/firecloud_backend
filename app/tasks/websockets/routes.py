# app/websockets/routes.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.tasks.websockets.ws_manager import payment_ws_manager

router = APIRouter()

# Mapeia os pagamentos aprovados por pix
@router.websocket("/ws/payment/{transaction_code}")
async def websocket_payment(websocket: WebSocket):
    await payment_ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        payment_ws_manager.disconnect(websocket)
    
# Mapeia todos os pagamentos por empresa   
@router.websocket("/ws/payments/{company_id}")
async def websocket_endpoint(websocket: WebSocket, company_id: int):
    await websocket.accept()
    active_connections = {}
    
    if company_id not in active_connections:
        active_connections[company_id] = []
    active_connections[company_id].append(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections[company_id].remove(websocket)

import asyncio
import json
import websockets
from datetime import datetime
import os

# Magazyn danych
active_clients = {}  # {client_id: websocket}
message_queue = {}   # {client_id: [list_of_messages]}
# Rejestr urządzeń: {client_id: {"hwid": hwid, "username": username}}
user_registry = {} 

async def retry_pending_messages(client_id, websocket):
    if client_id in message_queue and message_queue[client_id]:
        print(f"[LOG] Wysyłanie zaległych ({len(message_queue[client_id])}) do: {client_id}")
        for msg in message_queue[client_id][:]:
            try:
                await websocket.send(json.dumps(msg))
                message_queue[client_id].remove(msg)
            except: break

async def handler(websocket):
    client_id = None
    try:
        # Rejestracja rozszerzona o login i hwid
        auth_data = await websocket.recv()
        data = json.loads(auth_data)
        client_id = data.get("id")
        username = data.get("username", "Anon")
        hwid = data.get("hwid")

        if not client_id or len(client_id) != 3:
            await websocket.close()
            return

        # Blokada urządzenia (HWID)
        if client_id in user_registry:
            if user_registry[client_id]["hwid"] != hwid:
                await websocket.send(json.dumps({"type": "system", "content": "BŁĄD: To ID należy do innego urządzenia!"}))
                await websocket.close()
                return
        else:
            user_registry[client_id] = {"hwid": hwid, "username": username}

        active_clients[client_id] = websocket
        print(f"[ONLINE] {username} ({client_id}) połączony.")
        await retry_pending_messages(client_id, websocket)

        async for message in websocket:
            msg_data = json.loads(message)
            targets = msg_data.get("to")
            
            # Budowanie paczki
            payload = {
                "from": username,
                "from_id": client_id,
                "content": msg_data.get("content"),
                "type": msg_data.get("type", "text"),
                "filename": msg_data.get("filename", ""),
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }

            # Logika adresowania (Global / Grupa / Solo)
            if targets == "ALL":
                dest_list = [cid for cid in active_clients if cid != client_id]
            elif isinstance(targets, list):
                dest_list = targets
            else:
                dest_list = [targets]

            for target in dest_list:
                if target in active_clients:
                    try:
                        await active_clients[target].send(json.dumps(payload))
                    except:
                        message_queue.setdefault(target, []).append(payload)
                else:
                    message_queue.setdefault(target, []).append(payload)

    except websockets.ConnectionClosed:
        print(f"[OFFLINE] {client_id} rozłączony.")
    finally:
        if client_id in active_clients:
            del active_clients[client_id]

async def main():
    port = int(os.environ.get("PORT", 8080))
    # Zwiększony max_size dla plików
    async with websockets.serve(handler, "0.0.0.0", port, max_size=10*1024*1024):
        print(f"Serwer działa na porcie {port}...")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

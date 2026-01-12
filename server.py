import asyncio
import json
import websockets
from datetime import datetime

# Magazyn danych w pamięci
active_clients = {}  # {client_id: websocket}
message_queue = {}   # {client_id: [list_of_messages]}

async def retry_pending_messages(client_id, websocket):
    """Próbuje wysłać zaległe wiadomości po podłączeniu klienta."""
    if client_id in message_queue and message_queue[client_id]:
        print(f"[LOG] Wysyłanie zaległych wiadomości do: {client_id}")
        for msg in message_queue[client_id][:]:
            try:
                await websocket.send(json.dumps(msg))
                message_queue[client_id].remove(msg)
            except:
                break

async def handler(websocket):
    client_id = None
    try:
        # Pierwsza wiadomość to zawsze rejestracja: {"type": "register", "id": "123"}
        auth_data = await websocket.recv()
        data = json.loads(auth_data)
        client_id = data.get("id")

        if not client_id or len(client_id) != 3:
            await websocket.close()
            return

        active_clients[client_id] = websocket
        print(f"[ONLINE] Użytkownik {client_id} połączony.")
        
        # Sprawdź kolejowane wiadomości
        await retry_pending_messages(client_id, websocket)

        async for message in websocket:
            msg_data = json.loads(message) # {"to": "456", "content": "Cześć!"}
            target_id = msg_data.get("to")
            payload = {
                "from": client_id,
                "content": msg_data.get("content"),
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }

            if target_id in active_clients:
                try:
                    await active_clients[target_id].send(json.dumps(payload))
                except:
                    # Jeśli wysyłka zawiedzie, wrzuć do kolejki
                    message_queue.setdefault(target_id, []).append(payload)
            else:
                print(f"[QUEUE] Odbiorca {target_id} offline. Kolejkuję wiadomość.")
                message_queue.setdefault(target_id, []).append(payload)

    except websockets.ConnectionClosed:
        print(f"[OFFLINE] Użytkownik {client_id} rozłączony.")
    finally:
        if client_id in active_clients:
            del active_clients[client_id]

async def main():
    # Koyeb przypisuje port dynamicznie przez zmienną środowiskową PORT
    import os
    port = int(os.environ.get("PORT", 8080))
    async with websockets.serve(handler, "0.0.0.0", port):
        print(f"Serwer uruchomiony na porcie {port}...")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())

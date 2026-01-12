import asyncio
import websockets
import json

# Słownik przechowujący połączonych użytkowników {user_id: websocket}
connected_users = {}


async def handle_client(websocket):
    user_id = None
    try:
        # Pierwsza wiadomość od klienta to jego ID
        auth = await websocket.recv()
        data = json.loads(auth)
        user_id = data.get("user_id")
        connected_users[user_id] = websocket
        print(f"✅ Połączono użytkownika: {user_id}")

        async for message in websocket:
            # Format wiadomości: {"target_id": "123", "msg": "010101...", "key": "ziarno"}
            payload = json.loads(message)
            target_id = payload.get("target_id")

            if target_id in connected_users:
                await connected_users[target_id].send(json.dumps({
                    "from": user_id,
                    "msg": payload["msg"],
                    "key_hint": "Wiadomość zaszyfrowana"
                }))
            else:
                await websocket.send(json.dumps({"error": "Użytkownik offline"}))

    except Exception as e:
        print(f"Błąd: {e}")
    finally:
        if user_id in connected_users:
            del connected_users[user_id]


start_server = websockets.serve(handle_client, "0.0.0.0", 8000)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


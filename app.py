import asyncio
import websockets
import json
import os

# Słownik przechowujący połączonych użytkowników
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
            # Format wiadomości: {"target_id": "123", "msg": "010101..."}
            payload = json.loads(message)
            target_id = payload.get("target_id")

            if target_id in connected_users:
                await connected_users[target_id].send(json.dumps({
                    "from": user_id,
                    "msg": payload["msg"],
                    "key_hint": "Wiadomość zaszyfrowana"
                }))
                print(f"🔄 Przesłano wiadomość od {user_id} do {target_id}")
            else:
                await websocket.send(json.dumps({"error": f"Użytkownik {target_id} jest offline"}))

    except Exception as e:
        print(f"⚠️ Błąd połączenia ({user_id}): {e}")
    finally:
        if user_id in connected_users:
            del connected_users[user_id]
            print(f"❌ Użytkownik {user_id} rozłączony.")

async def main():
    # Pobieramy port z ustawień Koyeb (zmienna PORT) lub używamy 8000
    port = int(os.environ.get("PORT", 8000))
    
    # Start serwera
    async with websockets.serve(handle_client, "0.0.0.0", port):
        print(f"🚀 Tłusty serwer ruszył na porcie {port}")
        await asyncio.Future()  # Trzyma serwer przy życiu (nieskończona pętla)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Zatrzymano serwer.")

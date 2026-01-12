import asyncio
import websockets
import json
from koder import WinterCoder  # Twój kod z pliku koder.py


async def chat():
    uri = "wss://twoja-nazwa-aplikacji.koyeb.app"  # Adres z Koyeb
    my_id = input("Podaj swoje ID: ")

    async with websockets.connect(uri) as websocket:
        # Rejestracja
        await websocket.send(json.dumps({"user_id": my_id}))

        print("--- POŁĄCZONO ---")

        while True:
            choice = input("1. Wyślij | 2. Odbierz (czekaj): ")

            if choice == '1':
                target = input("ID odbiorcy: ")
                key = input("Klucz szyfrowania: ")
                text = input("Wiadomość: ")

                coder = WinterCoder(key)
                binary_msg = coder.encode(text)

                payload = json.dumps({"target_id": target, "msg": binary_msg})
                await websocket.send(payload)
                print("Wysłano!")

            elif choice == '2':
                print("Czekam na wiadomość...")
                response = await websocket.recv()
                data = json.loads(response)
                print(f"\n📩 Od: {data['from']}")
                print(f"Binarne: {data['msg']}")

                key = input("Podaj klucz do odkodowania: ")
                coder = WinterCoder(key)
                print(f"Odkodowano: {coder.decode(data['msg'])}")


if __name__ == "__main__":
    try:
        asyncio.run(chat())
    except KeyboardInterrupt:
        print("\nZamykanie...")
    except Exception as e:
        print(f"Błąd krytyczny: {e}")
        input("Naciśnij Enter, aby wyjść...")
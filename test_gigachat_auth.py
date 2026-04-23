# test_gigachat_auth.py
import asyncio
import httpx
import base64
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("GIGACHAT_CLIENT_ID")
CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET")
SCOPE = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
TOKEN_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

async def test_token():
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    credentials = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
    
    print(f"🔑 Отправляю запрос с ID: {CLIENT_ID[:8]}...")
    
    async with httpx.AsyncClient(verify=False, timeout=30) as client:
        try:
            resp = await client.post(
                TOKEN_URL,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": f"Basic {credentials}",
                    "RqUID": "00000000-0000-0000-0000-000000000000"
                },
                data={"scope": SCOPE}
            )
            print(f"📡 Статус: {resp.status_code}")
            if resp.status_code == 200:
                token = resp.json()["access_token"]
                print(f"✅ Токен получен: {token[:20]}...")
            else:
                print(f"❌ Ошибка: {resp.text}")
        except Exception as e:
            print(f"💥 Исключение: {e}")

if __name__ == "__main__":
    asyncio.run(test_token())
import asyncio
import json
import sys
from nats.aio.client import Client as NATS


async def test_publish_event():
    """Тест опубликации события"""
    try:
        nc = NATS()
        await nc.connect('nats://localhost:4222')
        print("✓ Подключено к NATS")
        
        payload = {
            'user_id': '035b4c6f-c074-4eb6-b4b0-2324867a20a9',
            'success': False
        }
        await nc.publish('workout.completed', json.dumps(payload).encode())
        await nc.flush()
        print("✓ Event опубликовано в 'workout.completed'")
        
        await nc.close()
    except Exception as e:
        print(f"✗ Ошибка в test_publish_event: {e}")
        sys.exit(1)


async def test_admin_requests():
    """Тест admin.user.list и admin.user.ban запросов"""
    try:
        nc = NATS()
        await nc.connect("nats://localhost:4222")
        print("✓ Подключено к NATS")

        # Тест list
        print("Отправляю запрос admin.user.list...")
        msg = await nc.request(
            "admin.user.list",
            json.dumps({"limit": 5}).encode(),
            timeout=2.0,
        )
        resp = json.loads(msg.data.decode())
        print("✓ Response admin.user.list:", resp)

        # Тест ban
        print("Отправляю запрос admin.user.ban...")
        msg = await nc.request(
            "admin.user.ban",
            json.dumps({"user_id": "c3ae6a37-cee7-40b7-81e7-2fcbb1795521"}).encode(),
            timeout=2.0,
        )
        resp = json.loads(msg.data.decode())
        print("✓ Response admin.user.ban:", resp)

        await nc.close()
    except Exception as e:
        print(f"✗ Ошибка в test_admin_requests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_num = sys.argv[1] if len(sys.argv) > 1 else "1"
    
    print(f"Запуск тест #{test_num}...\n")
    
    if test_num == "1":
        asyncio.run(test_publish_event())
    elif test_num == "2":
        asyncio.run(test_admin_requests())
    else:
        print("Использование: python test-nats-client.py [1|2]")
        print("  1 - Тест публикации события (работает если NATS запущен)")
        print("  2 - Тест admin запросов (требует запущенный admin микросервис)")
        sys.exit(1)
    
    print("\n✓ Все тесты пройдены!")

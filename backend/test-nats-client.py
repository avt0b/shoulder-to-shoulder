import asyncio, json
from nats.aio.client import Client as NATS


async def test():
    nc = NATS()
    await nc.connect('nats://localhost:4222')
    await nc.publish('workout.completed', json.dumps({
        'user_id': '035b4c6f-c074-4eb6-b4b0-2324867a20a9',
        'success': False
    }).encode())
    await nc.flush()
    await nc.close()
    print('Event sent')

asyncio.run(test())


async def test_admin_list():
    nc = NATS()
    await nc.connect("nats://localhost:4222")

    # Request/Reply
    msg = await nc.request(
        "admin.user.list",
        json.dumps({"limit": 10, "offset": 0}).encode(),
        timeout=2.0,
    )
    resp = json.loads(msg.data.decode())
    print("Response:", resp)

    await nc.close()


asyncio.run(test_admin_list())


async def test_nats_admins_users():
    nc = NATS()
    await nc.connect("nats://localhost:4222")

    # Тест list
    msg = await nc.request(
        "admin.user.list",
        json.dumps({"limit": 5}).encode(),
        timeout=2.0,
    )
    resp = json.loads(msg.data.decode())
    print("List response:", resp)

    msg = await nc.request(
        "admin.user.ban",
        json.dumps({"user_id": "c3ae6a37-cee7-40b7-81e7-2fcbb1795521"}).encode(),
        timeout=2.0,
    )
    resp = json.loads(msg.data.decode())
    print("Ban response:", resp)

    await nc.close()


asyncio.run(test_nats_admins_users())

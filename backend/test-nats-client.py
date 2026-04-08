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

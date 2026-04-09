"""NATS client for async messaging."""

from nats.aio.client import Client as NATS

from app.core.config import settings


class NATSClient:
    """NATS message broker client."""

    def __init__(self):
        """Initialize NATS client."""
        self.client: NATS | None = None

    async def connect(self):
        """Connect to NATS server."""
        if self.client is None:
            self.client = NATS()
            await self.client.connect(settings.NATS_URL)
            print(f"Connected to NATS at {settings.NATS_URL}")

    async def disconnect(self):
        """Disconnect from NATS server."""
        if self.client:
            await self.client.close()
            self.client = None
            print("Disconnected from NATS")

    async def publish(self, subject: str, message: bytes):
        """Publish message to NATS subject."""
        if not self.client:
            raise RuntimeError("NATS client not connected")
        await self.client.publish(subject, message)

    async def subscribe(self, subject: str, callback):
        """Subscribe to NATS subject."""
        if not self.client:
            raise RuntimeError("NATS client not connected")
        return await self.client.subscribe(subject, cb=callback)


# Global NATS client instance
nats_client = NATSClient()

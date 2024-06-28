from httpx import AsyncClient

from core import settings


class PaystackClient:
    def __init__(self, client: AsyncClient):
        self.client = client(
            base_url=settings.paystack_config.BASE_URL,
            headers={"Authorization": f"Bearer {settings.paystack_config.SECRET_KEY}"},
        )

    async def get_balance(self):
        rsp = await self.client.get(url="transaction/verify/igd38pit1u")
        return rsp.json()


def get_paystack(client=AsyncClient):
    return PaystackClient(client=client)

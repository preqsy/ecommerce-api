from httpx import AsyncClient
import logging

from core import settings
from models.auth_user import Customer
from models.orders import Order

logger = logging.getLogger(__name__)


class PaystackClient:

    def __init__(self, client=AsyncClient):
        self.client: AsyncClient = client(
            base_url=settings.paystack_config.BASE_URL,
            headers={"Authorization": f"Bearer {settings.paystack_config.SECRET_KEY}"},
        )

    async def initialize_payment(self, email, amount, channel, **kwargs):
        customer: Customer = kwargs.get("customer")
        order: Order = kwargs.get("order")
        metadata = {
            "customer_id": customer.id,
            "customer_first_name": customer.first_name,
            "customer_last_name": customer.last_name,
            "order_id": order.id,
            "custom_fields": [
                {
                    "display_name": "Order ID",
                    "display_id": "Order ID",
                    "value": order.total_amount,
                }
            ],
        }
        try:
            rsp = await self.client.post(
                "transaction/initialize",
                json={
                    "email": email,
                    "amount": amount * 100,
                    "channel": channel,
                    "callback_url": settings.paystack_config.CALLBACK_URL,
                    "metadata": metadata,
                },
            )
        except Exception as e:
            logger.error(e)
            return {"error": str(e)}

        return rsp.json()

    async def verify_payment(self, payment_ref):
        try:
            rsp = await self.client.get(url=f"transaction/verify/{payment_ref}")
            rsp_data = rsp.json()["data"]

        except Exception as e:
            logger.error(e)

        return rsp_data


def get_paystack():
    return PaystackClient()

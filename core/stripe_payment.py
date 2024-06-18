import stripe

from core import settings


stripe.api_key = settings.STRIPE_SECRET_KEY


async def create_checkout_session(quantity: int):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "NGN",
                        "product_data": {"name": "Items You Bought"},
                        "unit_amount": quantity * 100,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="https://google.com",
            cancel_url="https://yourdomain.com/cancel",
        )
        return {"id": session.id, "url": session.url}
    except Exception as e:
        raise ValueError()

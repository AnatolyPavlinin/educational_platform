import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(course_title: str, amount_cents: int) -> dict:
    """Создает продукт и цену в Stripe"""
    product = stripe.Product.create(
        name=f"Оплата курса '{course_title}'", metadata={"course_id": course_title}
    )
    price = stripe.Price.create(
        unit_amount=amount_cents, currency="rub", product=product.id, recurring=None
    )
    return {"product_id": product.id, "price_id": price.id}


def create_checkout_session(price_id: str, success_url: str, cancel_url: str) -> dict:
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return {"session_id": session.id, "checkout_url": session.url}

import stripe
from decimal import Decimal
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_base = "https://api.stripe.com/v1"


def create_payment_intent(amount: Decimal, currency: str, booking_id: str, customer_email: str, payment_method_type: str = "card") -> dict:
    """Create a Stripe Payment Intent for a booking."""
    intent = stripe.PaymentIntent.create(
        amount=int(float(amount) * 100),
        currency=currency,
        payment_method_types=[payment_method_type],
        description=f"Booking payment for booking #{booking_id}",
        receipt_email=customer_email,
        metadata={
            "booking_id": str(booking_id),
        },
        automatic_payment_methods={
            "enabled": True,
        },
    )
    return {
        "client_secret": intent.client_secret,
        "payment_intent_id": intent.id,
        "status": intent.status,
        "amount": intent.amount,
        "currency": intent.currency,
    }


def retrieve_payment_intent(payment_intent_id: str) -> dict:
    """Retrieve a Stripe Payment Intent by ID."""
    intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    return {
        "payment_intent_id": intent.id,
        "status": intent.status,
        "amount": intent.amount,
        "currency": intent.currency,
        "description": intent.description,
        "metadata": intent.metadata,
        "charges": [
            {
                "id": charge.id,
                "amount": charge.amount,
                "currency": charge.currency,
                "status": charge.status,
                "payment_method": charge.payment_method,
                "created": charge.created,
            }
            for charge in intent.charges.data
        ],
    }


def confirm_payment_intent(payment_intent_id: str) -> dict:
    """Confirm a Stripe Payment Intent."""
    intent = stripe.PaymentIntent.confirm(payment_intent_id)
    return {
        "payment_intent_id": intent.id,
        "status": intent.status,
        "client_secret": intent.client_secret,
    }


def cancel_payment_intent(payment_intent_id: str) -> dict:
    """Cancel a Stripe Payment Intent."""
    intent = stripe.PaymentIntent.cancel(payment_intent_id)
    return {
        "payment_intent_id": intent.id,
        "status": intent.status,
    }


def refund_payment(charge_id: str, amount: Decimal | None = None) -> dict:
    """Refund a Stripe charge."""
    params = {"charge": charge_id}
    if amount:
        params["amount"] = int(float(amount) * 100)
    refund = stripe.Refund.create(**params)
    return {
        "refund_id": refund.id,
        "amount": refund.amount,
        "currency": refund.currency,
        "status": refund.status,
    }


def get_payment_methods(customer_id: str | None = None, payment_method_type: str = "card") -> list:
    """Get available payment methods for a customer."""
    params = {"type": payment_method_type}
    if customer_id:
        params["customer"] = customer_id
    methods = stripe.PaymentMethod.list(**params)
    return [
        {
            "id": pm.id,
            "type": pm.type,
            "card": {
                "brand": pm.card.brand if pm.card else None,
                "last4": pm.card.last4 if pm.card else None,
                "exp_month": pm.card.exp_month if pm.card else None,
                "exp_year": pm.card.exp_year if pm.card else None,
            } if pm.card else None,
        }
        for pm in methods.data
    ]


def create_refund_from_intent(payment_intent_id: str, amount: Decimal | None = None) -> dict:
    """Create a refund from a Payment Intent."""
    intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    if not intent.charges.data:
        return {"error": True, "errMsg": "No charges found for this payment intent"}
    charge_id = intent.charges.data[0].id
    return refund_payment(charge_id, amount)


def handle_webhook_event(payload: bytes, sig_header: str) -> dict:
    """Handle a Stripe webhook event."""
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        return {
            "event_type": event.type,
            "data": event.data.object,
        }
    except ValueError:
        return {"error": True, "errMsg": "Invalid payload"}
    except stripe.error.SignatureVerificationError:
        return {"error": True, "errMsg": "Invalid signature"}


def create_checkout_session(
    amount: Decimal,
    currency: str,
    booking_id: str,
    customer_email: str,
    success_url: str,
    cancel_url: str,
) -> dict:
    """Create a Stripe Checkout Session for redirect-based payment methods."""
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": currency,
                    "product_data": {
                        "name": f"Hostel Booking #{booking_id}",
                    },
                    "unit_amount": int(float(amount) * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        customer_email=customer_email,
        metadata={"booking_id": str(booking_id)},
        success_url=success_url,
        cancel_url=cancel_url,
        automatic_tax={"enabled": True},
    )
    return {
        "checkout_url": session.url,
        "session_id": session.id,
    }

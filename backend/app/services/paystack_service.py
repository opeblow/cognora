import logging
import secrets
import httpx
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.payment import Payment
from app.services.credit_service import CreditService

logger = logging.getLogger(__name__)

CREDIT_PACKS = {
    50: 500,      # 50 credits = ₦500
    100: 900,     # 100 credits = ₦900
    200: 1600,    # 200 credits = ₦1,600
    500: 3500,    # 500 credits = ₦3,500
    1000: 6000,   # 1000 credits = ₦6,000
}

PAYSTACK_API = "https://api.paystack.co"


class PaystackService:
    def __init__(self, db: Session):
        self.db = db
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.public_key = settings.PAYSTACK_PUBLIC_KEY

    @staticmethod
    def get_webhook_secret() -> str:
        return settings.PAYSTACK_SECRET_KEY

    def get_payment_for_user(self, reference: str, user_id: str) -> Payment | None:
        return self.db.query(Payment).filter(Payment.reference == reference, Payment.user_id == user_id).first()

    def initialize_transaction(self, email: str, amount_kobo: int, metadata: dict | None = None) -> dict | None:
        if not self.secret_key:
            logger.warning("Paystack secret key not configured")
            return None

        reference = f"COG_{secrets.token_hex(12)}"
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(
                    f"{PAYSTACK_API}/transaction/initialize",
                    json={
                        "email": email,
                        "amount": amount_kobo,
                        "reference": reference,
                        "metadata": metadata or {},
                        "callback_url": f"{(settings.CORS_ORIGINS or ['http://localhost:3000'])[0]}/credits?reference={reference}",
                    },
                    headers={
                        "Authorization": f"Bearer {self.secret_key}",
                        "Content-Type": "application/json",
                    },
                )
                data = resp.json()
                if data.get("status"):
                    return {
                        "authorization_url": data["data"]["authorization_url"],
                        "reference": reference,
                    }
                logger.error(f"Paystack init failed: {data}")
                return None
        except Exception as e:
            logger.error(f"Paystack request failed: {e}")
            return None

    def verify_transaction(self, reference: str) -> dict | None:
        if not self.secret_key:
            logger.warning("Paystack secret key not configured")
            return None

        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(
                    f"{PAYSTACK_API}/transaction/verify/{reference}",
                    headers={"Authorization": f"Bearer {self.secret_key}"},
                )
                data = resp.json()
                if data.get("status") and data["data"]["status"] == "success":
                    return data["data"]
                logger.error(f"Paystack verify failed: {data}")
                return None
        except Exception as e:
            logger.error(f"Paystack verification request failed: {e}")
            return None

    def initialize_purchase(self, user_id: str, email: str, credit_amount: int) -> dict:
        if credit_amount not in CREDIT_PACKS:
            raise ValueError(f"Invalid credit amount. Available packs: {', '.join(str(k) for k in CREDIT_PACKS.keys())}")

        amount_kobo = CREDIT_PACKS[credit_amount] * 100  # Convert to kobo
        metadata = {
            "user_id": user_id,
            "credit_amount": credit_amount,
        }

        result = self.initialize_transaction(email, amount_kobo, metadata)
        if not result:
            raise ValueError("Failed to initialize payment. Please try again.")

        payment = Payment(
            user_id=user_id,
            amount=CREDIT_PACKS[credit_amount],
            currency="NGN",
            status="pending",
            reference=result["reference"],
            credits_purchased=credit_amount,
        )
        self.db.add(payment)
        self.db.commit()

        return {
            "authorization_url": result["authorization_url"],
            "reference": result["reference"],
            "credit_amount": credit_amount,
            "amount": CREDIT_PACKS[credit_amount],
            "currency": "NGN",
        }

    def handle_webhook(self, payload: dict) -> bool:
        event = payload.get("event", "")
        data = payload.get("data", {})

        if event == "charge.success":
            reference = data.get("reference", "")
            payment = self.db.query(Payment).filter(Payment.reference == reference).with_for_update().first()
            if not payment:
                logger.warning(f"Payment not found for reference: {reference}")
                return False

            if payment.status == "completed":
                return True

            verified = self.verify_transaction(reference)
            if not verified or verified.get("amount") != payment.amount * 100 or verified.get("currency") != payment.currency:
                logger.warning("Rejected payment webhook with mismatched provider data for %s", reference)
                return False
            metadata = verified.get("metadata") or {}
            if str(metadata.get("user_id")) != str(payment.user_id) or int(metadata.get("credit_amount", 0)) != payment.credits_purchased:
                logger.warning("Rejected payment webhook with mismatched metadata for %s", reference)
                return False

            payment.status = "completed"
            payment.payment_method = data.get("channel", "unknown")

            credit_service = CreditService(self.db)
            credit_amount = int(payment.credits_purchased or 0)
            if credit_amount > 0:
                credit_service.add_credits(
                    user_id=payment.user_id,
                    amount=credit_amount,
                    description=f"Paystack purchase: {credit_amount} credits (₦{payment.amount})",
                )

            self.db.commit()
            logger.info(f"Payment completed: ref={reference}, credits={credit_amount}")
            return True

        return False

    @staticmethod
    def get_credit_packs() -> dict:
        return CREDIT_PACKS

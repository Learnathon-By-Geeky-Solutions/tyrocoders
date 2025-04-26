from fastapi import HTTPException
from fastapi.responses import JSONResponse
from crud.user import UserCrud
from crud.subscription import SubscriptionCrud
from core.logger import logger
from utils.converter import convert_object_id_to_string
from datetime import datetime, timedelta
from core.config import settings
from typing import Optional
from urllib.parse import urlencode
from http import HTTPStatus
from schemas import UserCreate, UserLogin
from services.user_service import UserService

from bson import ObjectId
import stripe
from schemas.subscription import (
    PaymentRequest, SaveCheckoutSessionRequest
)

user_service = UserService()
user_crud = UserCrud()
subscription_crud = SubscriptionCrud()

class SubscriptionService:
    async def create_checkout_session(self, user_id: str, payment_data: PaymentRequest):
        """Create a Stripe checkout session with proper amount handling"""
        try:
            user = await user_service.validate_user(user_id)
            if not user:
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": "User not found"},
                )

            stripe.api_key = settings.STRIPE_SECRET_KEY
            session = stripe.checkout.Session.create(
                success_url=f"{settings.FRONTEND_URL}/payment/success",
                cancel_url=f"{settings.FRONTEND_URL}/payment/cancel",
                payment_method_types=["card"],
                mode="payment",
                customer_email=user["email"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": payment_data.package_name,
                            },
                            "unit_amount": int(payment_data.amount * 100),
                        },
                        "quantity": 1,
                    }
                ],
                metadata={
                    "user_id": user_id, 
                    "package": payment_data.package_name,
                    "interval": payment_data.interval
                }
            )

            logger.info(f"Created checkout session {session.id} for user {user_id}")
            return JSONResponse(
                status_code=HTTPStatus.CREATED,
                content={
                    "message": "Checkout session created successfully",
                    "data": {
                        "checkout_url": session.url,
                        "session_id": session.id
                    },
                },
            )
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe API error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,  # 400
                detail=f"Payment processing error: {getattr(e, 'user_message', str(e))}"
            )
        except Exception as e:
            logger.critical(f"Unexpected payment error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,  # 500
                detail="Internal payment processing error"
            )
        
    async def save_checkout_session(self, user_id, session_data: SaveCheckoutSessionRequest):

        try:
            user = await user_service.validate_user(user_id)
            if not user:
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": "User not found"},
                )
            
            session_id = session_data.session_id

            if not session_id:
                raise HTTPException(status_code=400, detail="session_id is required")

            stripe.api_key = settings.STRIPE_SECRET_KEY

            try:
                session = stripe.checkout.Session.retrieve(session_id)
                metadata = session.get("metadata", {})
            except stripe.error.InvalidRequestError:
                raise HTTPException(status_code=400, detail="Invalid session_id")

            # Save transaction record
            transaction_data = {
                "user_id": str(user_id),
                "session_id": session_id,
                "amount": session.amount_total / 100,
                "currency": session.currency,
                "payment_status": session.payment_status,
                "transaction_id": session.payment_intent,
                "package_name": metadata.get("package"),
                "interval": metadata.get("interval"),
                "created_at": datetime.now()
            }
            await subscription_crud.save_transaction(transaction_data)

            if session.payment_status == "paid":
                package_name = metadata.get("package")
                interval = metadata.get("interval")
                
                if interval in ("month", "year"):  # Main subscription
                    await user_crud.update_user_subscription(user_id, package_name, interval)
                else:  
                    await user_crud.update_user_addons(user_id, package_name)

            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "Payment completed successfully and package benefit updated",
                },
            )

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
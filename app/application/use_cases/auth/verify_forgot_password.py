import json
import logging

logger = logging.getLogger("assistly")


class VerifyForgotPasswordService:
    def __init__(self, cache_service):
        self.cache_service = cache_service

    def execute(self, data):
        try:
            # Fetch OTP payload from Redis
            raw = self.cache_service.get(
                f"forgot_password:{data.email}"
            )

            if not raw:
                logger.warning(
                    f"No forgot password request found for {data.email}"
                )
                raise Exception(
                    "OTP has expired or forgot password was not initiated."
                )

            payload = json.loads(raw)

            # Validate OTP
            if payload["otp"] != data.otp_code:
                logger.warning(
                    f"Invalid forgot password OTP entered for {data.email}"
                )
                raise Exception("Invalid OTP code.")

            # Store verification flag for reset password step
            self.cache_service.set(
                f"forgot_password_verified:{data.email}",
                300,
                "true"
            )

            logger.info(
                f"Forgot password OTP verified successfully for {data.email}"
            )

            return {
                "message": "OTP verified successfully."
            }

        except Exception as e:
            logger.error(
                f"Forgot password OTP verification failed for {data.email}",
                exc_info=True
            )
            raise
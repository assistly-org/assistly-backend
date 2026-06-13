import json
import random
import logging

logger = logging.getLogger("assistly")


class ForgotPasswordService:
    def __init__(
        self,
        user_repo,
        cache_service,
        task_dispatcher
    ):
        self.user_repo = user_repo
        self.cache_service = cache_service
        self.task_dispatcher = task_dispatcher

    def execute(self, data):

        try:
            logger.info("STEP 1: Finding user")

            user = self.user_repo.get_by_email(data.email)

            if not user:
                logger.warning(
                    f"Forgot password requested for non-existent email: {data.email}"
                )
                return {
                    "message": "If the email exists, an OTP has been sent."
                }

        except Exception as e:
            logger.error(
                f"STEP 1 FAILED - User lookup failed: {str(e)}",
                exc_info=True
            )
            raise

        try:
            logger.info("STEP 2: Generating OTP")

            otp_code = str(random.randint(100000, 999999))
            print(f"Forgot Password OTP: {otp_code}")

        except Exception as e:
            logger.error(
                f"STEP 2 FAILED - OTP generation failed: {str(e)}",
                exc_info=True
            )
            raise

        try:
            logger.info("STEP 3: Creating payload")

            payload = json.dumps({
                "email": data.email,
                "otp": otp_code
            })

        except Exception as e:
            logger.error(
                f"STEP 3 FAILED - Payload creation failed: {str(e)}",
                exc_info=True
            )
            raise

        try:
            logger.info("STEP 4: Saving OTP in Redis")

            self.cache_service.set(
                f"forgot_password:{data.email}",
                300,
                payload
            )

        except Exception as e:
            logger.error(
                f"STEP 4 FAILED - Redis save failed: {str(e)}",
                exc_info=True
            )
            raise

        try:
            logger.info("STEP 5: Sending OTP email")

            self.task_dispatcher.dispatch_otp_email(
                data.email,
                otp_code
            )

        except Exception as e:
            logger.error(
                f"STEP 5 FAILED - Email dispatch failed: {str(e)}",
                exc_info=True
            )
            raise

        logger.info(
            f"Forgot password OTP generated successfully for {data.email}"
        )

        return {
            "message": "OTP sent successfully."
        }
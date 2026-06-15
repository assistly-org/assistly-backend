import json
import random
import logging

logger = logging.getLogger("assistly")


class RequestEmailChangeService:

    def __init__(
        self,
        user_repo,
        cache_service,
        task_dispatcher
    ):
        self.user_repo = user_repo
        self.cache_service = cache_service
        self.task_dispatcher = task_dispatcher

    def execute(
        self,
        current_user,
        data
    ):

        if data.new_email == current_user.email:
            raise Exception(
                "New email must be different from current email."
            )

        existing_user = self.user_repo.get_by_email(
            data.new_email
        )

        if existing_user:
            raise Exception(
                "Email already exists."
            )

        otp = str(
            random.randint(100000, 999999)
        )
        print(f"Email Change OTP: {otp}")
        

        payload = json.dumps({
            "email": data.new_email,
            "otp": otp
        })

        self.cache_service.set(
            f"email_change:{data.new_email}",
            300,
            payload
        )

        self.task_dispatcher.dispatch_otp_email(
            data.new_email,
            otp
        )

        logger.info(
            f"Email change OTP generated for {current_user.email}"
        )

        return {
            "message": "OTP sent successfully."
        }
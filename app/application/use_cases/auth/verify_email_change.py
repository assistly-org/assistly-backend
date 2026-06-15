import json
import logging

logger = logging.getLogger("assistly")


class VerifyEmailChangeService:
    def __init__(
        self,
        user_repo,
        cache_service
    ):
        self.user_repo = user_repo
        self.cache_service = cache_service

    def execute(
        self,
        current_user,
        data
    ):
        try:
            raw = self.cache_service.get(
                f"email_change:{data.new_email}"
            )

            if not raw:
                logger.warning(
                    f"No email change request found for {data.new_email}"
                )
                raise Exception(
                    "OTP has expired or email change was not initiated."
                )

            payload = json.loads(raw)

            if payload["otp"] != data.otp_code:
                logger.warning(
                    f"Invalid email change OTP entered for {data.new_email}"
                )
                raise Exception(
                    "Invalid OTP code."
                )

            existing_user = self.user_repo.get_by_email(
                data.new_email
            )

            if existing_user:
                raise Exception(
                    "Email already exists."
                )

            current_user.email = data.new_email

            self.user_repo.update_user(
                current_user
            )

            self.cache_service.delete(
                f"email_change:{data.new_email}"
            )

            logger.info(
                f"Email changed successfully for {current_user.email}"
            )

            return {
                "message": "Email updated successfully."
            }

        except Exception as e:
            logger.error(
                f"Email change verification failed for {data.new_email}",
                exc_info=True
            )
            raise
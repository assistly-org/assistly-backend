import logging

logger = logging.getLogger("assistly")

class ChangePasswordService:
    def __init__(
        self,
        user_repo,
        hash_service
    ):
        self.user_repo = user_repo
        self.hash_service = hash_service

    def execute(
        self,
        current_user,
        data
    ):
        # Verify current password
        if not self.hash_service.verify_password(
            data.current_password,
            current_user.password_hash
        ):
            raise Exception(
                "Current password is incorrect."
            )

        # Hash new password
        hashed_password = self.hash_service.hash_password(
            data.new_password
        )

        # Update password
        current_user.password_hash = hashed_password

        self.user_repo.update_user(
            current_user
        )

        logger.info(
            f"Password changed successfully for {current_user.email}"
        )

        return {
            "message": "Password changed successfully."
        }
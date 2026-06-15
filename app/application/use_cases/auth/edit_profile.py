import logging

logger = logging.getLogger("assistly")


class EditProfileService:
    def __init__(
        self,
        user_repo
    ):
        self.user_repo = user_repo

    def execute(
        self,
        current_user,
        data
    ):
        current_user.name = data.name

        self.user_repo.update_user(
            current_user
        )

        logger.info(
            f"Profile updated successfully for {current_user.email}"
        )

        return {
            "message": "Profile updated successfully."
        }
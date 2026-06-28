import logging
from sqlalchemy.orm import Session # ⚡ Make sure to import Session


logger = logging.getLogger("assistly")

class ResetPasswordService:
    def __init__(
        self,
        db: Session, # ⚡ Inject the DB here!
        user_repo,
        hash_service,
        cache_service
    ):
        self.db = db # ⚡ Save it to the class
        self.user_repo = user_repo
        self.hash_service = hash_service
        self.cache_service = cache_service
    
    def execute(self, data):
        try:
            logger.info("STEP 1: Checking verification")

            verified = self.cache_service.get(
                f"forgot_password_verified:{data.email}"
            )

            if not verified:
                raise Exception(
                    "OTP verification required before resetting password."
                )

            logger.info("STEP 2: Finding user")

            user = self.user_repo.get_by_email(data.email)

            if not user:
                raise Exception(
                    "User not found."
                )

            logger.info("STEP 3: Hashing password")

            hashed_password = self.hash_service.hash_password(
                data.new_password
            )

            logger.info("STEP 4: Updating user")

            user.password_hash = hashed_password

            self.user_repo.update_user(user)

            logger.info("STEP 5: Cleaning Redis")

            self.cache_service.delete(
                f"forgot_password:{data.email}"
            )

            self.cache_service.delete(
                f"forgot_password_verified:{data.email}"
            )

            # ⚡ COMMIT THE TRANSACTION HERE!
            self.db.commit()

            logger.info("STEP 6: Success")

            return {
                "message": "Password reset successful."
            }

        except Exception as e:
            # ⚡ ROLLBACK IF ANYTHING FAILS!
            self.db.rollback()
            
            logger.exception(
                f"Password reset failed for {data.email}"
            )
            raise e
class RegistrationExpiredError(Exception):
    pass

class InvalidOTPError(Exception):
    pass

class ValidationError(Exception):
    pass

class UserAlreadyExistsError(Exception):
    pass

class SubdomainTakenError(Exception):
    pass

class InvalidCredentialsError(Exception):
    pass

class AccountDisabledError(Exception):
    pass

class InvalidTokenError(Exception):
    pass

class UserNotFoundError(Exception):
    pass

class DomainError(Exception):
    """Base exception for all domain-level errors."""
    pass

class UserNotVerifiedError(DomainError):
    def __init__(self, message="User account has not been verified via OTP."):
        super().__init__(message)

class WorkspaceSuspendedError(DomainError):
    def __init__(self, message="This workspace has been suspended."):
        super().__init__(message)

class InsufficientPermissionsError(DomainError):
    def __init__(self, message="User does not have the required role to perform this action in this workspace."):
        super().__init__(message)
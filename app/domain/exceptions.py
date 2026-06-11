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
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from pydantic import BaseModel
# Import your main FastAPI app and the dependencies you want to override
from app.main import app
from app.presentation.dependencies.auth_deps import get_register_service, get_login_service
from app.presentation.dependencies.auth_deps import get_refresh_service, get_logout_service
from app.presentation.dependencies.auth_deps import (
    get_verify_service,
    get_forgot_password_service,
    get_verify_forgot_password_service,
    get_reset_password_service,
    get_change_password_service,
    get_google_auth_service
)
from app.presentation.dependencies.current_user import get_current_user
from app.infrastructure.db.database import get_db
from app.domain.exceptions import InvalidOTPError
from app.domain.exceptions import UserAlreadyExistsError, InvalidCredentialsError
from app.domain.exceptions import InvalidTokenError

# Create the test client
client = TestClient(app)

# We need this dummy class for the Google Setup route since it still injects the DB


class MockSession:
    def commit(self): pass
    def rollback(self): pass

# ==========================================
# 1. TEST THE REGISTER ROUTE
# ==========================================


class MockRegisterService:
    def register(self, data):
        # Simulate a database conflict
        if data.email == "taken@assistly.com":
            raise UserAlreadyExistsError("Email is already registered.")

        # Simulate a successful registration
        return {
            "message": "User registered successfully",
            "user_id": "uuid-1234",
            "email": data.email
        }


def test_register_success():
    # 1. Override the dependency
    app.dependency_overrides[get_register_service] = lambda: MockRegisterService(
    )

    # 2. Fire the request
    payload = {
        "email": "new@assistly.com",
        "password": "Password123!",
        "company_name": "Assistly Test",
        "subdomain": "assistlytest"  # ⚡ Add this line!
    }
    response = client.post("/auth/register", json=payload)

    # 3. Assertions
    assert response.status_code == 200
    assert response.json()["message"] == "User registered successfully"

    # 4. Clean up the override
    app.dependency_overrides.clear()


def test_register_email_taken():
    app.dependency_overrides[get_register_service] = lambda: MockRegisterService(
    )

    payload = {
        "email": "taken@assistly.com",
        "password": "Password123!",
        "company_name": "Assistly Test",
        "subdomain": "taken_subdomain"
    }
    response = client.post("/auth/register", json=payload)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Email is already registered."

    app.dependency_overrides.clear()


# ==========================================
# 2. TEST THE LOGIN ROUTE (COOKIE CHECK)
# ==========================================


class MockLoginService:
    def login(self, data):
        if data.email == "wrong@assistly.com":
            raise InvalidCredentialsError("Invalid email or password")

        return {
            "message": "login successfully",
            "access_token": "fake_access_jwt",
            "refresh_token": "fake_refresh_jwt",
            "token_type": "bearer",
            "user": {"id": "1", "email": data.email, "tenant_subdomain": "test_subdomain"}
        }


def test_login_success_sets_cookie():
    app.dependency_overrides[get_login_service] = lambda: MockLoginService()

    response = client.post("/auth/login", json={
        "email": "owner@assistly.com",
        "password": "CorrectPassword!"
    })

    assert response.status_code == 200

    # ⚡ Check the JSON payload (Refresh token should NOT be here)
    data = response.json()
    assert data["access_token"] == "fake_access_jwt"
    assert "refresh_token" not in data  # response_model should strip it

    # ⚡ Check the hidden cookies!
    cookies = response.cookies
    assert "refresh_token" in cookies
    assert cookies["refresh_token"] == "fake_refresh_jwt"

    app.dependency_overrides.clear()


# ==========================================
# 3. TEST THE REFRESH ROUTE
# ==========================================

class MockRefreshService:
    def execute(self, refresh_token):
        if not refresh_token or refresh_token != "valid_old_refresh_token":
            raise InvalidTokenError("Invalid refresh token.")

        return {
            "access_token": "brand_new_access_jwt",
            "refresh_token": "brand_new_refresh_jwt",
            "token_type": "bearer"
        }


def test_refresh_success_rotates_cookie():
    app.dependency_overrides[get_refresh_service] = lambda: MockRefreshService(
    )

    # ⚡ We must explicitly pass the cookie into the test client
    client.cookies.set("refresh_token", "valid_old_refresh_token")
    response = client.post("/auth/refresh")

    assert response.status_code == 200

    # 1. Check the JSON payload for the new access token
    assert response.json()["access_token"] == "brand_new_access_jwt"

    # 2. Check the cookies to ensure the refresh token was overwritten
    cookies = response.cookies
    assert "refresh_token" in cookies
    assert cookies["refresh_token"] == "brand_new_refresh_jwt"

    app.dependency_overrides.clear()
    client.cookies.clear()


# ==========================================
# 4. TEST THE LOGOUT ROUTE
# ==========================================

class MockLogoutService:
    def execute(self, refresh_token):
        # We just need it to run without throwing an error
        pass


def test_logout_deletes_cookie():
    app.dependency_overrides[get_logout_service] = lambda: MockLogoutService()

    # Set a fake active session cookie
    client.cookies.set("refresh_token", "active_refresh_token")

    # Fire the logout request
    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert response.json()[
        "message"] == "Successfully logged out. Session revoked securely."

    # ⚡ Verify the cookie was deleted!
    # FastAPI deletes cookies by setting them to empty and expiring them in the past.
    cookies = response.cookies
    assert cookies.get("refresh_token") in [None, '""', ""]

    app.dependency_overrides.clear()
    client.cookies.clear()

# ==========================================
# 5. TEST THE VERIFY (OTP) ROUTE
# ==========================================


class MockVerifyService:
    def verify_otp(self, data):
        if data.otp_code == "000000":  # Simulate a bad OTP
            raise InvalidOTPError("Invalid or expired OTP.")

        return {
            "message": "Welcome to your workspace!",
            "access_token": "verified_access_jwt",
            "refresh_token": "verified_refresh_jwt",
            "token_type": "bearer",
            "user": {"id": "1", "email": data.email, "tenant_subdomain": "mycompany"}
        }


def test_verify_success():
    # ⚡ No DB override needed anymore! Just the service.
    app.dependency_overrides[get_verify_service] = lambda: MockVerifyService()

    payload = {"email": "new@assistly.com", "otp_code": "123456"}
    response = client.post("/auth/verify", json=payload)

    assert response.status_code == 200
    assert response.json()["access_token"] == "verified_access_jwt"

    # Verify the route correctly sets the refresh cookie
    assert "refresh_token" in response.cookies
    assert response.cookies["refresh_token"] == "verified_refresh_jwt"

    app.dependency_overrides.clear()


def test_verify_invalid_otp():
    app.dependency_overrides[get_verify_service] = lambda: MockVerifyService()

    payload = {"email": "new@assistly.com", "otp_code": "000000"}
    response = client.post("/auth/verify", json=payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid or expired OTP."

    app.dependency_overrides.clear()


# ==========================================
# 6. TEST THE FORGOT & RESET PASSWORD FLOW
# ==========================================

class MockForgotPasswordService:
    def execute(self, request):
        return {"message": "If the email exists, an OTP has been sent."}


class MockVerifyForgotPasswordService:
    def execute(self, request):
        return {"message": "OTP verified successfully. You can now reset your password."}


class MockResetPasswordService:
    def execute(self, request):
        if request.new_password == "TooShort":
            raise Exception("Password validation failed")
        return {"message": "Password reset successful."}


def test_forgot_password():
    app.dependency_overrides[get_forgot_password_service] = lambda: MockForgotPasswordService(
    )
    response = client.post("/auth/forgot-password",
                           json={"email": "user@assistly.com"})
    assert response.status_code == 200
    assert response.json()[
        "message"] == "If the email exists, an OTP has been sent."
    app.dependency_overrides.clear()


def test_verify_forgot_password():
    app.dependency_overrides[get_verify_forgot_password_service] = lambda: MockVerifyForgotPasswordService()
    response = client.post("/auth/verify-forgot-password",
                           json={"email": "user@assistly.com", "otp_code": "123456"})
    assert response.status_code == 200
    app.dependency_overrides.clear()


def test_reset_password_success():
    app.dependency_overrides[get_reset_password_service] = lambda: MockResetPasswordService(
    )
    response = client.post("/auth/reset-password", json={
                           "email": "user@assistly.com", "new_password": "BrandNewPassword123!"})
    assert response.status_code == 200
    assert response.json()["message"] == "Password reset successful."
    app.dependency_overrides.clear()


# ==========================================
# 7. TEST PROTECTED ROUTES (ME & CHANGE PASSWORD)
# ==========================================


# Create a fake user object to mock `get_current_user`
# ⚡ Inherit from BaseModel so FastAPI automatically converts it to JSON!
class MockUser(BaseModel):
    id: str = "uuid-1234"
    email: str = "test@assistly.com"


class MockChangePasswordService:
    def execute(self, current_user, request):
        return {"message": "Password changed successfully."}


def test_get_me():
    app.dependency_overrides[get_current_user] = lambda: MockUser()
    response = client.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == "test@assistly.com"
    app.dependency_overrides.clear()


def test_change_password():
    app.dependency_overrides[get_current_user] = lambda: MockUser()
    app.dependency_overrides[get_change_password_service] = lambda: MockChangePasswordService(
    )

    payload = {"current_password": "OldPassword123!",
               "new_password": "NewPassword123!"}
    response = client.post("/auth/change-password", json=payload)

    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully."
    app.dependency_overrides.clear()


# ==========================================
# 8. TEST GOOGLE AUTHENTICATION
# ==========================================

class MockGoogleAuthService:
    def google_login(self, data):
        return {
            "requires_setup": True,
            "setup_token": "google_setup_jwt",
            "message": "Please provide a company name and subdomain to finish setup."
        }

    def google_setup(self, data, db):
        # The router expects an object with a refresh_token attribute
        class FakeResult:
            access_token = "google_access_jwt"
            refresh_token = "google_refresh_jwt"
            message = "Google workspace setup complete."
        return FakeResult()


def test_google_login():
    app.dependency_overrides[get_google_auth_service] = lambda: MockGoogleAuthService(
    )
    response = client.post(
        "/auth/google", json={"id_token": "fake_google_id_token"})
    assert response.status_code == 200
    assert response.json()["requires_setup"] is True
    app.dependency_overrides.clear()


def test_google_setup():
    # ⚡ We need MockSession here because google_setup still injects get_db!
    app.dependency_overrides[get_google_auth_service] = lambda: MockGoogleAuthService(
    )
    app.dependency_overrides[get_db] = lambda: MockSession()

    payload = {
        "setup_token": "google_setup_jwt",
        "subdomain": "googletenant",
        "company_name": "Google Test Corp"
    }
    response = client.post("/auth/google/setup", json=payload)

    assert response.status_code == 200
    assert response.json()["access_token"] == "google_access_jwt"

    # Ensure the Google Setup sets the HTTP-only cookie
    assert "refresh_token" in response.cookies
    assert response.cookies["refresh_token"] == "google_refresh_jwt"

    app.dependency_overrides.clear()

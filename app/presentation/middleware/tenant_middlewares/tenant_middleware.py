from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.infrastructure.db.tenant_context import set_tenant_schema
from app.infrastructure.logger import logger


AUTH_SCHEMA = "assistly_auth"


class SubdomainTenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Get the host header (e.g., "api.mobilemart.localhost:8000")
        host = request.headers.get("host", "")

        # Strip port number (e.g., "api.mobilemart.localhost")
        domain_parts = host.split(":")[0].split(".")

        # 2. Extract the subdomain based on your new "api.subdomain.domain" rule

        # Scenario A: api.mobilemart.localhost (Length is 3+, starts with 'api')
        if len(domain_parts) >= 3 and domain_parts[0] == "api":
            subdomain = domain_parts[1]  # Grabs "mobilemart"
            schema_name = f"tenant_{subdomain}"
            logger.info(
                f"🎯 Middleware intercepted tenant (subdomain: {subdomain} 🟢) . Routing to {schema_name} ✅")
            set_tenant_schema(schema_name)

            request.state.subdomain = subdomain
            request.state.schema_name = schema_name

        # Scenario B: api.localhost (Length is exactly 2, starts with 'api')
        elif len(domain_parts) == 2 and domain_parts[0] == "api":
            logger.info(
                f"🔒 Auth API Base detected (Host: {host} 🟢). Routing to assistly_auth ✅ schema.")
            set_tenant_schema(AUTH_SCHEMA)

            # ⚡ Attach state for the global auth routes
            request.state.subdomain = None
            request.state.schema_name = AUTH_SCHEMA

        # Scenario C: Fallback for raw localhost, 127.0.0.1, or www.
        else:
            logger.info(
                f"❌ No tenant subdomain detected (Host: {host} 🟢). Routing to GLOBAL 🌍 schema.")
            set_tenant_schema("public")

            request.state.subdomain = None
            request.state.schema_name = "public"

        # 3. Continue processing the request
        response = await call_next(request)
        return response

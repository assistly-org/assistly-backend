import re
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
            raw_subdomain = domain_parts[1]  # Grabs "mobilemart" or "test-v1"
            
            # ⚡ SECURITY FIX 1: Convert URL hyphens to DB underscores
            safe_subdomain = raw_subdomain.replace("-", "_")
            
            # ⚡ SECURITY FIX 2: Block SQL Injection from spoofed Host headers
            if not re.match(r"^[a-z0-9_]+$", safe_subdomain):
                logger.warning(f"🚨 Malicious Host header detected: {host}")
                set_tenant_schema("public")
                request.state.subdomain = None
                request.state.schema_name = "public"
                return await call_next(request)

            schema_name = f"tenant_{safe_subdomain}"
            logger.info(
                f"🎯 Middleware intercepted tenant (subdomain: {raw_subdomain} 🟢) . Routing to {schema_name} ✅")
            set_tenant_schema(schema_name)

            request.state.subdomain = raw_subdomain # Keep original for UI purposes if needed
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

        # 3. Continue processing the request safely
        try:
            response = await call_next(request)
            return response
            
        finally:
            # ⚡ THE RESET: The connection is about to go back to the pool.
            # We must force it back to the public schema so it doesn't leak!
            set_tenant_schema("public")
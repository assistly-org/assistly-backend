from pydantic import BaseModel, HttpUrl
from typing import Optional

class TenantCreateRequest(BaseModel):
    company_name: str
    subdomain: str
    website_url: HttpUrl  # ⚡ Pydantic will ensure this is a valid format!

class TenantCreateResponse(BaseModel):
    message: str
    tenant_id: str
    tenant_subdomain: str
    website_url: str
    widget_api_key: str  # ⚡ We only show this ONCE!
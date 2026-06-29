from sqlalchemy import Column, Integer, Text, String
from app.infrastructure.db.database import TenantBase

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None


class DocumentChunk(TenantBase):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True)
    tenant_id = Column (String(50), nullable=False)
    document_id = Column(String(50), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)

    # OpenAI embedding size
    if Vector:
        embedding = Column(Vector(1536))
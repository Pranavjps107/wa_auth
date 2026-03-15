
# ----------------------------------------------------------------------------
# FILE: auth-service/app/models/tenant.py (SHARED SCHEMA)
# ----------------------------------------------------------------------------
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.db import Base


class Tenant(Base):
    """Tenant/Organization (SHARED SCHEMA - Both services reference this)"""
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    # Note: this deployment's tenants table does not include `subdomain` or `status` columns.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="tenant", cascade="all, delete-orphan")

    # Keep Tenant model minimal to match existing DB schema.

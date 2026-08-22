import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from app.core.database import Base


class UserRole(str, Enum):
    CITIZEN = "citizen"
    ADMIN = "admin"
    SUPPORT = "support"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    phone = Column(String(50), nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)
    role = Column(String(20), default=UserRole.CITIZEN.value, nullable=False)
    preferred_language = Column(String(10), default="en", nullable=False)
    country = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True, index=True)
    district = Column(String(100), nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    profile = Column(JSONB, default=dict, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "preferred_language": self.preferred_language,
            "country": self.country,
            "state": self.state,
            "district": self.district,
            "is_verified": self.is_verified,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
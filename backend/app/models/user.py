# -*- coding: utf-8 -*-
"""
派聪明AI知识库系统 - 用户模型
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base

class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # 组织关联
    organization_id: Mapped[Optional[int]] = mapped_column(ForeignKey("organizations.id"), nullable=True)

    organization: Mapped[Optional["Organization"]] = relationship(
        "Organization",
        back_populates="users",
        foreign_keys=[organization_id],
        lazy="selectin"
    )

    # 用户角色和状态
    role: Mapped[str] = mapped_column(String(20), default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 用户配置
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    position: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    preferences: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # API Key
    api_key: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True, nullable=True)
    
    # 关联关系
    documents = relationship("Document", back_populates="uploader", lazy="selectin")
    chat_sessions = relationship("ChatSession", back_populates="user", lazy="selectin")
    
    # 👇👇👇 关键点：这里也要指定 foreign_keys
    owned_organizations = relationship(
        "Organization", 
        back_populates="owner",
        foreign_keys="Organization.owner_id",
        overlaps="owner" # 消除警告
    )
    
    organizations = relationship(
        "Organization",
        secondary="user_organization",
        back_populates="members",
        lazy="selectin"
    )

    roles_in_organizations = relationship(
        "Role",
        secondary="user_organization_role_association",
        overlaps="user_organization_roles", # 消除警告
        lazy="selectin"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
        
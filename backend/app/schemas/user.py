# -*- coding: utf-8 -*-
"""User response schemas — single source of truth for User serialization."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict


class UserInfoResponse(BaseModel):
    """Canonical User response schema used across all endpoints."""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    nickname: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    organization_id: Optional[int] = None
    role: str = "user"
    is_active: bool = True
    is_superuser: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    preferences: Optional[str] = None
    api_key: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserStatsResponse(BaseModel):
    conversation_count: int
    message_count: int
    file_count: int
    knowledge_count: int
    storage_used: int = 0
    storage_limit: int = 0
    activity_trend: List[int] = []


class UserUpdateProfile(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(from_attributes=True)


class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str


class UserSessionResponse(BaseModel):
    id: int
    device_name: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool
    last_seen_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class UserAuditLogResponse(BaseModel):
    id: int
    action: str
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: Optional[datetime] = None

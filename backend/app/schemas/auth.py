"""认证相关的 Pydantic 模型"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UpdateProfileRequest(BaseModel):
    """更新用户资料"""
    full_name: Optional[str] = Field(None, max_length=100, description="姓名")
    email: Optional[EmailStr] = Field(None, description="邮箱")


class ChangePasswordRequest(BaseModel):
    """修改密码"""
    old_password: str = Field(..., min_length=1, description="旧密码")
    new_password: str = Field(..., min_length=8, max_length=128, description="新密码（8-128 位）")

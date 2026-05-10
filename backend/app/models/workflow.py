"""
Agent 工作流数据库模型
"""
from datetime import datetime
from typing import Optional, List, Any
from sqlalchemy import Integer, String, Text, Boolean, DateTime, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base


class Workflow(Base):
    """工作流定义"""
    __tablename__ = "workflows"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), comment="工作流名称")
    description: Mapped[Optional[str]] = mapped_column(Text, comment="工作流描述")
    flow_data: Mapped[Optional[Any]] = mapped_column(JSON, comment="工作流节点和边配置")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    executions: Mapped[List["WorkflowExecution"]] = relationship("WorkflowExecution", back_populates="workflow", lazy="dynamic")


class WorkflowExecution(Base):
    """工作流执行记录"""
    __tablename__ = "workflow_executions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workflow_id: Mapped[int] = mapped_column(Integer, ForeignKey("workflows.id"))
    status: Mapped[str] = mapped_column(String(20), default="pending", comment="执行状态: pending, running, completed, failed")
    input_data: Mapped[Optional[Any]] = mapped_column(JSON, comment="输入数据")
    output_data: Mapped[Optional[Any]] = mapped_column(JSON, comment="输出结果")
    node_results: Mapped[Optional[Any]] = mapped_column(JSON, comment="各节点执行结果")
    error_message: Mapped[Optional[str]] = mapped_column(Text, comment="错误信息")
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, comment="开始时间")
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, comment="完成时间")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    workflow: Mapped[Optional["Workflow"]] = relationship("Workflow", back_populates="executions")


class NodeDefinition(Base):
    """节点定义"""
    __tablename__ = "node_definitions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    node_type: Mapped[str] = mapped_column(String(50), unique=True, comment="节点类型标识")
    name: Mapped[str] = mapped_column(String(100), comment="节点显示名称")
    category: Mapped[str] = mapped_column(String(50), default="llm", comment="节点分类: llm, tool, io, logic")
    description: Mapped[Optional[str]] = mapped_column(Text, comment="节点描述")
    default_config: Mapped[Optional[Any]] = mapped_column(JSON, comment="默认配置")
    input_schema: Mapped[Optional[Any]] = mapped_column(JSON, comment="输入参数定义")
    output_schema: Mapped[Optional[Any]] = mapped_column(JSON, comment="输出参数定义")
    icon: Mapped[Optional[str]] = mapped_column(String(50), comment="图标名称")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

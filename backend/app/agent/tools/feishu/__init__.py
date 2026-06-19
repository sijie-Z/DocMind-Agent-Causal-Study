"""飞书 MCP Tools — 企业协同平台工具集。

工具列表:
    feishu_bitable_query   — 读取飞书多维表格记录（只读，带分页/过滤）
    (更多工具后续添加: 飞书文档、审批、通讯录等)

用法:
    from app.agent.tools.feishu import register_all  # 触发 @register_tool
"""

# 注册所有飞书工具
from app.agent.tools.feishu import bitable  # noqa: F401 — triggers @register_tool
from app.agent.tools.feishu.auth import FeishuTenantAuthHandler
from app.agent.tools.feishu.client import FeishuBitableClient

__all__ = [
    "FeishuTenantAuthHandler",
    "FeishuBitableClient",
]

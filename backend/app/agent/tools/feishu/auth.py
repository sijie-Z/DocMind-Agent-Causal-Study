"""飞书 Token 管理 — tenant_access_token 缓存 + 自动刷新。

使用方式:
    handler = FeishuTenantAuthHandler()
    token = await handler.get_token()

配置 (环境变量):
    FEISHU_APP_ID          — 飞书自建应用的 App ID
    FEISHU_APP_SECRET      — 飞书自建应用的 App Secret
    FEISHU_TOKEN_CACHE_TTL — token 缓存时间（秒，默认 3600，飞书有效期 7200）

注意:
    - tenant_access_token 有效期 2 小时
    - 默认提前 1 小时刷新（cache TTL = 3600s），避免边缘过期
    - 分布式环境下应接入 Redis 共享缓存（当前为进程级内存缓存）
"""

import logging
import os
import time
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger(__name__)

# 默认配置
_FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "")
_FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
_FEISHU_TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"


@dataclass
class TokenCache:
    """进程级 token 缓存。分布式环境应替换为 Redis。"""
    token: str = ""
    expires_at: float = 0.0  # unix timestamp

    @property
    def is_valid(self) -> bool:
        return bool(self.token) and time.time() < self.expires_at


class FeishuTenantAuthHandler:
    """飞书 tenant_access_token 管理器（进程级缓存）。"""

    def __init__(
        self,
        app_id: str = "",
        app_secret: str = "",
        cache_ttl: int = 3600,  # 飞书 token 有效期 7200s，我们提前 1h 刷新
    ):
        self._app_id = app_id or _FEISHU_APP_ID
        self._app_secret = app_secret or _FEISHU_APP_SECRET
        self._cache_ttl = cache_ttl
        self._cache = TokenCache()
        self._http_client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=10.0)
        return self._http_client

    async def get_token(self) -> str:
        """获取有效的 tenant_access_token。

        优先返回缓存中的 token；缓存过期或不存在时自动刷新。

        Returns:
            有效的 token 字符串。

        Raises:
            FeishuAuthError: 应用凭证无效或飞书服务异常。
        """
        if self._cache.is_valid:
            return self._cache.token

        return await self._refresh_token()

    async def _refresh_token(self) -> str:
        """向飞书请求新的 tenant_access_token。"""
        if not self._app_id or not self._app_secret:
            raise FeishuAuthError(
                "FEISHU_APP_ID 或 FEISHU_APP_SECRET 未配置。请在环境变量中设置。"
            )

        client = await self._get_client()
        try:
            resp = await client.post(
                _FEISHU_TOKEN_URL,
                json={"app_id": self._app_id, "app_secret": self._app_secret},
            )
            resp.raise_for_status()
            body = resp.json()

            code = body.get("code", -1)
            if code != 0:
                msg = body.get("msg", "未知错误")
                raise FeishuAuthError(f"飞书 token 换取失败 (code={code}): {msg}")

            token = body.get("tenant_access_token", "")
            expire_in = body.get("expire", 7200)  # 秒

            self._cache.token = token
            # 使用较小的 TTL：min(cache_ttl, expire_in - 600) 留 10 分钟余量
            effective_ttl = min(self._cache_ttl, expire_in - 600)
            self._cache.expires_at = time.time() + max(effective_ttl, 60)

            logger.info("飞书 token 刷新成功，有效期 %ds，缓存 TTL %ds", expire_in, effective_ttl)
            return token

        except httpx.TimeoutException:
            raise FeishuAuthError("飞书 token 换取超时，请检查网络连接")
        except httpx.HTTPStatusError as e:
            raise FeishuAuthError(f"飞书服务返回 HTTP {e.response.status_code}")
        except FeishuAuthError:
            raise
        except Exception as e:
            raise FeishuAuthError(f"飞书 token 换取异常: {e}")

    async def invalidate(self) -> None:
        """强制清除缓存，下次 get_token() 将重新换取。"""
        self._cache = TokenCache()
        logger.info("飞书 token 缓存已清除")

    async def close(self) -> None:
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None


class FeishuAuthError(Exception):
    """飞书认证相关错误。"""
    pass

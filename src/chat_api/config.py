from __future__ import annotations

# pydantic 负责数据校验；pydantic-settings 负责从环境变量/.env 读配置。
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """服务配置：自动读取 CHAT_* 环境变量和 .env 文件。

    字段名和环境变量的对应关系：
        api_key                 <- CHAT_API_KEY
        base_url                <- CHAT_BASE_URL
        model                   <- CHAT_MODEL
        rate_limit_per_minute   <- CHAT_RATE_LIMIT_PER_MINUTE
    环境变量的优先级高于 .env 文件。
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CHAT_",   # 所有字段自动加 CHAT_ 前缀
        extra="ignore",       # 忽略 .env 里的多余变量
    )

    # 这些字段在创建 Settings() 时会被 pydantic 校验和转换。
    api_key: str = Field(default="", description="兼容 OpenAI 协议的 API Key")
    base_url: str = Field(default="https://api.openai.com/v1")
    model: str = Field(default="gpt-4o-mini")

    timeout: float = Field(default=60.0, gt=0)            # 请求超时（秒）
    max_retries: int = Field(default=2, ge=0, le=10)      # 失败重试次数
    temperature: float = Field(default=0.7, ge=0, le=2)   # 0 最稳定，2 最发散
    max_tokens: int = Field(default=1024, ge=1, le=32768) # 最多生成多少 token

    # 单机限流阈值；多实例部署时要换成 Redis 等共享存储。
    rate_limit_per_minute: int = Field(default=600, ge=1, le=100_000)

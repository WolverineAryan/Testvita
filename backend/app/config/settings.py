import urllib.parse as up
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

def sanitize_db_url(v: str) -> str:
    if not v:
        return "sqlite+aiosqlite:///./codevita.db"
    v = v.strip()
    if v.startswith("sqlite"):
        return v

    # Convert dialect to asyncpg
    if v.startswith("postgres://"):
        v = v.replace("postgres://", "postgresql+asyncpg://", 1)
    elif v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
        v = v.replace("postgresql://", "postgresql+asyncpg://", 1)

    parsed = up.urlparse(v)
    if "postgresql" in parsed.scheme:
        query_dict = up.parse_qs(parsed.query)
        allowed_asyncpg_params = {"ssl", "timeout", "command_timeout", "server_settings"}
        
        cleaned_params = {}
        if "sslmode" in query_dict or "ssl" in query_dict:
            cleaned_params["ssl"] = "require"
            
        for k, val in query_dict.items():
            if k in allowed_asyncpg_params and k != "ssl":
                cleaned_params[k] = val[0] if isinstance(val, list) else val

        new_query = up.urlencode(cleaned_params)
        return up.urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))

    return v

class Settings(BaseSettings):
    PROJECT_NAME: str = "CodeVita AI Coach"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./codevita.db"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_url(cls, v: str) -> str:
        return sanitize_db_url(v)
    
    # JWT Auth
    SECRET_KEY: str = "dev-secret-key-change-in-production-codevita-ai-coach-2026-supersecure"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v
    
    # AI Configuration (NVIDIA Nemotron API)
    AI_PROVIDER: str = "nvidia"  # "nvidia", "mock"
    NVIDIA_API_KEY: str = ""
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_MODEL: str = "nvidia/llama-3.1-nemotron-70b-instruct"
    DEFAULT_AI_MODEL: str = "nvidia/llama-3.1-nemotron-70b-instruct"
    
    # Execution Sandbox Limits & Engine
    EXECUTION_MODE: str = "cloud"  # "cloud", "local", "auto"
    JUDGE0_API_URL: str = "https://ce.judge0.com"
    WANDBOX_API_URL: str = "https://wandbox.org/api/compile.json"
    EXECUTION_TIMEOUT_SECONDS: float = 3.0
    EXECUTION_MAX_MEMORY_MB: int = 256
    EXECUTION_MAX_OUTPUT_CHARS: int = 65536
    
    # Gamification
    XP_PER_EASY_SOLVE: int = 20
    XP_PER_MEDIUM_SOLVE: int = 50
    XP_PER_HARD_SOLVE: int = 100
    XP_PER_MOCK_ATTEMPT: int = 150
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )

settings = Settings()

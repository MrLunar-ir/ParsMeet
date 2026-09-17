from dataclasses import dataclass

@dataclass
class Config:
    token: str
    base_url: str = "https://botapi.codemeet.chat"
    timeout: int = 30
    polling_timeout: int = 30
    polling_limit: int = 100
    polling_max_retries: int = 3
    retries: int = 3
    retry_backoff: float = 2.0
    debug: bool = False
    log_level: str = "INFO"
    log_file: str = None
    ai_provider: str = "keylessai"
    ai_key: str = None
    ai_model: str = None
    ai_memory: bool = True
    rate_limit_max: int = 5
    rate_limit_window: int = 1
    cooldown_seconds: int = 3
    dashboard_enabled: bool = False
    dashboard_port: int = 8080
    webhook_enabled: bool = False
    webhook_port: int = 8443
    webhook_secret: str = None
    storage_path: str = "parsmeet_storage.json"
    database_path: str = "ParsMeetSaveMessage.db"
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    deepseek_api_key: str
    deepseek_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    deepseek_model: str = "deepseek-v3"
    tushare_token: str
    max_history_rounds: int = 20

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

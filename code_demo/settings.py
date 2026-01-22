"""
Centralized Configuration for Text Generation System
"""
import os
from typing import Optional


class Settings:
    """Configuration class for RabbitMQ, Redis, and application settings"""
    
    # RabbitMQ Configuration
    RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT: int = int(os.getenv("RABBITMQ_PORT", "5672"))
    RABBITMQ_USER: str = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD: str = os.getenv("RABBITMQ_PASSWORD", "guest")
    RABBITMQ_VHOST: str = os.getenv("RABBITMQ_VHOST", "/")
    
    # Queue Configuration
    TEXT_GENERATION_QUEUE: str = os.getenv("TEXT_GENERATION_QUEUE", "text_generation_tasks")
    QUEUE_DURABLE: bool = True
    PREFETCH_COUNT: int = int(os.getenv("PREFETCH_COUNT", "1"))
    
    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", "mypassword")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_DECODE_RESPONSES: bool = True
    
    # Task Configuration
    TASK_TTL: int = int(os.getenv("TASK_TTL", "3600"))  # 1 hour in seconds
    TASK_PREFIX: str = "task:"
    
    # Status Constants
    STATUS_PENDING: str = "PENDING"
    STATUS_PROCESSING: str = "PROCESSING"
    STATUS_COMPLETED: str = "COMPLETED"
    STATUS_FAILED: str = "FAILED"
    
    # Mock LLM Configuration (can be replaced with real API settings)
    MOCK_MIN_DELAY: float = float(os.getenv("MOCK_MIN_DELAY", "2.0"))
    MOCK_MAX_DELAY: float = float(os.getenv("MOCK_MAX_DELAY", "5.0"))
    
    # OpenAI Configuration (for future use)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "500"))
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    @classmethod
    def get_rabbitmq_url(cls) -> str:
        """Get RabbitMQ connection URL"""
        return f"amqp://{cls.RABBITMQ_USER}:{cls.RABBITMQ_PASSWORD}@{cls.RABBITMQ_HOST}:{cls.RABBITMQ_PORT}{cls.RABBITMQ_VHOST}"
    
    @classmethod
    def get_task_key(cls, task_id: str) -> str:
        """Get Redis key for a task"""
        return f"{cls.TASK_PREFIX}{task_id}"


# Create a singleton instance
settings = Settings()

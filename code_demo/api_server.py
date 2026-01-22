"""
API Server (Producer) - Accepts text generation requests and queues them
"""
import json
import uuid
import time
from typing import Dict, Any
import pika
import redis
from settings import settings


class TextGenerationProducer:
    """Producer class that accepts requests and publishes to RabbitMQ"""
    
    def __init__(self):
        """Initialize connections to RabbitMQ and Redis"""
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Establish connections to RabbitMQ and Redis"""
        try:
            # Connect to RabbitMQ
            credentials = pika.PlainCredentials(
                settings.RABBITMQ_USER,
                settings.RABBITMQ_PASSWORD
            )
            parameters = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                credentials=credentials,
                virtual_host=settings.RABBITMQ_VHOST
            )
            self.rabbitmq_connection = pika.BlockingConnection(parameters)
            self.rabbitmq_channel = self.rabbitmq_connection.channel()
            
            # Declare queue
            self.rabbitmq_channel.queue_declare(
                queue=settings.TEXT_GENERATION_QUEUE,
                durable=settings.QUEUE_DURABLE
            )
            
            # Connect to Redis
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=settings.REDIS_DECODE_RESPONSES
            )
            
            # Test Redis connection
            self.redis_client.ping()
            
            print("✓ Connected to RabbitMQ and Redis")
            
        except Exception as e:
            print(f"✗ Connection error: {e}")
            raise
    
    def create_task(self, prompt: str, metadata: Dict[str, Any] = None) -> str:
        """
        Create a text generation task
        
        Args:
            prompt: Text prompt for generation
            metadata: Optional metadata to attach to the task
            
        Returns:
            task_id: Unique identifier for the task
        """
        try:
            # Generate unique task ID
            task_id = str(uuid.uuid4())
            
            # Prepare task payload
            task_payload = {
                "task_id": task_id,
                "prompt": prompt,
                "metadata": metadata or {},
                "created_at": time.time(),
                "status": settings.STATUS_PENDING
            }
            
            # Save initial status to Redis
            redis_key = settings.get_task_key(task_id)
            self.redis_client.setex(
                redis_key,
                settings.TASK_TTL,
                json.dumps(task_payload)
            )
            
            # Publish task to RabbitMQ
            self.rabbitmq_channel.basic_publish(
                exchange='',
                routing_key=settings.TEXT_GENERATION_QUEUE,
                body=json.dumps(task_payload),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json',
                    message_id=task_id
                )
            )
            
            print(f"✓ Task created: {task_id[:8]}... | Prompt: {prompt[:50]}...")
            return task_id
            
        except Exception as e:
            print(f"✗ Error creating task: {e}")
            raise
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the current status and result of a task
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task data including status and result (if completed)
        """
        try:
            redis_key = settings.get_task_key(task_id)
            task_data = self.redis_client.get(redis_key)
            
            if not task_data:
                return {
                    "task_id": task_id,
                    "status": "NOT_FOUND",
                    "error": "Task not found or expired"
                }
            
            return json.loads(task_data)
            
        except Exception as e:
            print(f"✗ Error retrieving task status: {e}")
            return {
                "task_id": task_id,
                "status": "ERROR",
                "error": str(e)
            }
    
    def close(self):
        """Close connections"""
        try:
            if self.rabbitmq_connection and not self.rabbitmq_connection.is_closed:
                self.rabbitmq_connection.close()
            print("✓ Connections closed")
        except Exception as e:
            print(f"✗ Error closing connections: {e}")


# Standalone API simulation
def main():
    """Simulate API endpoint accepting requests"""
    producer = TextGenerationProducer()
    
    print("\n" + "="*70)
    print("🚀 Text Generation API Server (Simulation)")
    print("="*70)
    
    # Simulate multiple API requests
    test_prompts = [
        "Write a short story about a robot learning to paint",
        "Explain quantum computing in simple terms",
        "Create a Python function to validate email addresses",
        "Write a haiku about artificial intelligence"
    ]
    
    task_ids = []
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n[Request {i}] Creating task...")
        task_id = producer.create_task(
            prompt=prompt,
            metadata={"request_number": i, "source": "api_test"}
        )
        task_ids.append(task_id)
    
    print(f"\n{'='*70}")
    print(f"✓ Total {len(task_ids)} tasks created and queued")
    print(f"{'='*70}")
    print("\nTask IDs:")
    for i, tid in enumerate(task_ids, 1):
        print(f"  {i}. {tid}")
    
    print("\nTasks are now in RabbitMQ queue waiting for workers...")
    print("Start a worker with: python text_worker.py")
    
    producer.close()


if __name__ == "__main__":
    main()

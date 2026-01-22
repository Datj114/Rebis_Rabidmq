# 🚀 Asynchronous Text Generation System

Production-ready Python boilerplate for building async text generation services using **RabbitMQ** and **Redis**.

## 📁 Architecture

```
┌─────────────┐
│   Client    │ 
└──────┬──────┘
       │ 1. Submit prompt
       ↓
┌─────────────────┐
│  API Server     │ (api_server.py)
│  (Producer)     │
└────────┬────────┘
         │ 2. Create task → Redis (PENDING)
         │ 3. Publish to queue → RabbitMQ
         ↓
┌──────────────────┐
│   RabbitMQ       │
│   Queue          │
└────────┬─────────┘
         │ 4. Consume task
         ↓
┌──────────────────┐
│  Text Worker     │ (text_worker.py)
│  (Consumer)      │
└────────┬─────────┘
         │ 5. Update Redis → PROCESSING
         │ 6. Generate text (Mock LLM)
         │ 7. Update Redis → COMPLETED
         ↓
┌──────────────────┐
│     Redis        │
│   (Results)      │
└────────┬─────────┘
         │ 8. Poll for result
         ↓
┌─────────────┐
│   Client    │
└─────────────┘
```

## 🏗️ Components

| File | Description |
|------|-------------|
| `settings.py` | Centralized configuration for RabbitMQ, Redis, queues |
| `api_server.py` | Producer - API server that accepts requests and queues tasks |
| `text_worker.py` | Consumer - Worker that processes tasks and generates text |
| `client_test.py` | Test client with polling mechanism |

## 🔧 Configuration

All settings are in `settings.py` and can be overridden with environment variables:

```python
# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=mypassword

# Queue
TEXT_GENERATION_QUEUE=text_generation_tasks
TASK_TTL=3600  # 1 hour
```

## 🚀 Quick Start

### 1. Ensure Docker services are running
```bash
docker-compose up -d
docker-compose ps
```

### 2. Install dependencies
```bash
pip install pika redis
```

### 3. Start the worker (Terminal 1)
```bash
cd code_demo
python text_worker.py
```

### 4. Run tests (Terminal 2)

**Single request:**
```bash
python client_test.py single
```

**Multiple concurrent requests:**
```bash
python client_test.py multiple
```

**Interactive mode:**
```bash
python client_test.py interactive
```

## 📝 Usage Examples

### As a Library

```python
from api_server import TextGenerationProducer

# Initialize producer
producer = TextGenerationProducer()

# Submit a task
task_id = producer.create_task(
    prompt="Write a story about AI",
    metadata={"user_id": 123}
)

# Check status
status = producer.get_task_status(task_id)
print(status["status"])  # PENDING, PROCESSING, COMPLETED, or FAILED

# Get result
if status["status"] == "COMPLETED":
    print(status["result"])

producer.close()
```

### With Client Helper

```python
from client_test import TextGenerationClient

client = TextGenerationClient()

# Submit and wait for result
result = client.submit_and_wait(
    prompt="Explain neural networks",
    poll_interval=1.0,
    max_attempts=30
)

client.display_result(result)
client.close()
```

## 🔄 Task Lifecycle

```
PENDING → PROCESSING → COMPLETED
                    ↘ FAILED
```

1. **PENDING**: Task created and queued in RabbitMQ
2. **PROCESSING**: Worker picked up the task
3. **COMPLETED**: Text generation finished successfully
4. **FAILED**: Error occurred during processing

## 🤖 Replacing Mock LLM with Real API

The `generate_text_mock()` function in `text_worker.py` is designed for easy replacement:

### OpenAI Integration

```python
def generate_text_openai(self, prompt: str) -> str:
    """Replace mock with OpenAI API"""
    import openai
    
    openai.api_key = settings.OPENAI_API_KEY
    
    response = openai.ChatCompletion.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=settings.OPENAI_MAX_TOKENS,
        temperature=settings.OPENAI_TEMPERATURE
    )
    
    return response.choices[0].message.content
```

### Anthropic Claude Integration

```python
def generate_text_claude(self, prompt: str) -> str:
    """Replace mock with Anthropic Claude API"""
    import anthropic
    
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    message = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text
```

Just replace the call in `process_task()`:
```python
# generated_text = self.generate_text_mock(prompt)  # Old
generated_text = self.generate_text_openai(prompt)  # New
```

## ⚡ Performance & Scaling

### Multiple Workers

Run multiple workers for parallel processing:

```bash
# Terminal 1
python text_worker.py

# Terminal 2
python text_worker.py

# Terminal 3
python text_worker.py
```

Each worker processes one task at a time (`PREFETCH_COUNT=1`).

### Adjust Prefetch

In `settings.py`:
```python
PREFETCH_COUNT = 3  # Process up to 3 tasks per worker
```

## 🛡️ Error Handling

### Producer (API Server)
- ✅ Connection error handling
- ✅ Redis failure recovery
- ✅ Task creation validation

### Worker (Consumer)
- ✅ JSON parsing errors
- ✅ Processing exceptions → status FAILED
- ✅ Message acknowledgment
- ✅ No infinite requeue loops

### Client
- ✅ Polling timeout
- ✅ Task not found handling
- ✅ Connection cleanup

## 📊 Monitoring

### RabbitMQ Management UI
- URL: http://localhost:15672
- Login: guest/guest
- Monitor: Queue depth, message rates, consumers

### Redis CLI
```bash
docker exec -it redis redis-cli -a mypassword

# Check tasks
> KEYS task:*
> GET task:<task_id>
> TTL task:<task_id>

# Count tasks by status
> KEYS task:*
```

### Python Monitoring Script
```python
import redis
import json

client = redis.Redis(
    host='localhost',
    port=6379,
    password='mypassword',
    decode_responses=True
)

# Get all tasks
keys = client.keys("task:*")
for key in keys:
    data = json.loads(client.get(key))
    print(f"{data['task_id'][:8]}: {data['status']}")
```

## 🧪 Testing Scenarios

### Test 1: Single Request
```bash
python client_test.py single
```
Tests basic submit → process → poll workflow.

### Test 2: Concurrent Requests
```bash
python client_test.py multiple
```
Submits 3 requests simultaneously, tests parallel processing.

### Test 3: Worker Resilience
```bash
# Start worker
python text_worker.py

# Stop worker (Ctrl+C)
# Submit tasks
python api_server.py

# Restart worker → tasks will be processed
python text_worker.py
```

## 🔐 Production Considerations

### Security
- [ ] Use environment variables for credentials
- [ ] Implement API authentication
- [ ] Add rate limiting
- [ ] Validate input prompts

### Reliability
- [ ] Add dead letter queue (DLQ)
- [ ] Implement retry logic with exponential backoff
- [ ] Add health checks
- [ ] Monitor queue depth

### Scalability
- [ ] Use connection pooling
- [ ] Deploy multiple workers (Kubernetes/Docker Swarm)
- [ ] Implement task prioritization
- [ ] Add caching for repeated prompts

### Observability
- [ ] Add structured logging
- [ ] Implement metrics (Prometheus)
- [ ] Add distributed tracing (OpenTelemetry)
- [ ] Set up alerting

## 📚 References

- [RabbitMQ Tutorial](https://www.rabbitmq.com/tutorials/tutorial-one-python.html)
- [Pika Documentation](https://pika.readthedocs.io/)
- [Redis Python Client](https://redis-py.readthedocs.io/)
- [OpenAI API](https://platform.openai.com/docs/)

## 🎓 Use Cases

- **LLM API Services**: Queue expensive model inference
- **Batch Processing**: Process large volumes of text generation
- **Microservices**: Async communication between services
- **ETL Pipelines**: Text transformation and analysis
- **Chat Applications**: Handle message generation asynchronously

---

**Built for production.** Ready to scale. 🚀

# RabbitRabbit - Local Development Environment

Docker Compose setup for Python development with RabbitMQ and Redis.

## Services

### RabbitMQ
- **Image**: `rabbitmq:3-management`
- **AMQP Port**: 5672
- **Management UI**: http://localhost:15672
- **Credentials**: guest / guest
- **Volume**: `rabbitmq_data` (persists messages and configuration)

### Redis
- **Image**: `redis:alpine`
- **Port**: 6379
- **Password**: mypassword
- **Volume**: `redis_data` (persists data)

## Quick Start

### 1. Start the services
```bash
docker-compose up -d
```

### 2. Check service status
```bash
docker-compose ps
```

### 3. View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f rabbitmq
docker-compose logs -f redis
```

### 4. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 5. Test connections
```bash
# Test RabbitMQ
python test_rabbitmq.py

# Test Redis
python test_redis.py
```

## Management Access

- **RabbitMQ Management UI**: http://localhost:15672
  - Username: `guest`
  - Password: `guest`

## Useful Commands

```bash
# Stop services
docker-compose down

# Stop and remove volumes (⚠️ deletes all data)
docker-compose down -v

# Restart a specific service
docker-compose restart rabbitmq
docker-compose restart redis

# View resource usage
docker stats rabbitmq redis
```

## Service Health Checks

Both services include health checks that monitor availability:
- **RabbitMQ**: Uses `rabbitmq-diagnostics -q ping`
- **Redis**: Uses `redis-cli -a mypassword ping`

Check health status:
```bash
docker inspect rabbitmq --format='{{.State.Health.Status}}'
docker inspect redis --format='{{.State.Health.Status}}'
```

## Data Persistence

Data is persisted in named Docker volumes:
- `rabbitmq_data`: RabbitMQ messages, exchanges, queues
- `redis_data`: Redis key-value data

Volumes survive container restarts and can be backed up:
```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect rabbitmq_data
```

## Troubleshooting

### Services won't start
```bash
# Check if ports are already in use
sudo lsof -i :5672
sudo lsof -i :6379
sudo lsof -i :15672
```

### Connection refused
Wait for services to be fully ready (check health status):
```bash
docker-compose ps
```

### Reset everything
```bash
docker-compose down -v
docker-compose up -d
```

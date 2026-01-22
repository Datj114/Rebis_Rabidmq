#!/usr/bin/env python3
"""
Simple script to verify Redis connection.
Sets and retrieves a test key-value pair.
"""

import redis

def test_redis_connection():
    try:
        # Connect to Redis with password
        client = redis.Redis(
            host='localhost',
            port=6379,
            password='mypassword',
            decode_responses=True
        )
        
        # Test connection with ping
        if client.ping():
            print("✓ Redis connection established")
        
        # Set a test key
        test_key = 'test_key'
        test_value = 'Hello Redis!'
        client.set(test_key, test_value)
        print(f"✓ Set key '{test_key}' = '{test_value}'")
        
        # Get the test key
        retrieved_value = client.get(test_key)
        print(f"✓ Retrieved '{test_key}' = '{retrieved_value}'")
        
        # Test with expiration
        client.setex('temp_key', 10, 'This expires in 10 seconds')
        ttl = client.ttl('temp_key')
        print(f"✓ Created temporary key with TTL: {ttl} seconds")
        
        # Clean up
        client.delete(test_key, 'temp_key')
        print("✓ Cleaned up test keys")
        
        # Get Redis info
        info = client.info('server')
        print(f"\n✓ Redis connection successful!")
        print(f"Redis version: {info['redis_version']}")
        
    except redis.ConnectionError as e:
        print(f"✗ Redis connection failed: {e}")
        print("\nMake sure Redis is running:")
        print("  docker-compose up -d redis")
    except redis.AuthenticationError as e:
        print(f"✗ Redis authentication failed: {e}")
        print("Check password configuration in docker-compose.yml")
    except Exception as e:
        print(f"✗ Redis error: {e}")

if __name__ == "__main__":
    test_redis_connection()

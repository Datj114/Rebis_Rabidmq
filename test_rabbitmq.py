#!/usr/bin/env python3
"""
Simple script to verify RabbitMQ connection.
Sends a test message and receives it back.
"""

import pika

def test_rabbitmq_connection():
    try:
        # Connection parameters
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters(
            host='localhost',
            port=5672,
            credentials=credentials
        )
        
        # Establish connection
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        # Declare a test queue
        queue_name = 'test_queue'
        channel.queue_declare(queue=queue_name, durable=True)
        
        # Send a test message
        test_message = 'Hello RabbitMQ!'
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=test_message,
            properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
        )
        print(f"✓ Sent message: '{test_message}'")
        
        # Receive the message
        method_frame, header_frame, body = channel.basic_get(queue=queue_name, auto_ack=True)
        
        if body:
            print(f"✓ Received message: '{body.decode()}'")
        else:
            print("✗ No message received")
        
        # Clean up
        channel.queue_delete(queue=queue_name)
        connection.close()
        
        print("\n✓ RabbitMQ connection successful!")
        print("Management UI available at: http://localhost:15672")
        print("Login: guest / guest")
        
    except Exception as e:
        print(f"✗ RabbitMQ connection failed: {e}")
        print("\nMake sure RabbitMQ is running:")
        print("  docker-compose up -d rabbitmq")

if __name__ == "__main__":
    test_rabbitmq_connection()

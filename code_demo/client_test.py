"""
Client Test Script - Simulates a user sending requests and polling for results
"""
import time
import sys
from typing import Optional
from api_server import TextGenerationProducer
from settings import settings


class TextGenerationClient:
    """Client class to interact with the text generation system"""
    
    def __init__(self):
        """Initialize the producer"""
        self.producer = TextGenerationProducer()
    
    def submit_request(self, prompt: str, metadata: dict = None) -> str:
        """
        Submit a text generation request
        
        Args:
            prompt: Text prompt
            metadata: Optional metadata
            
        Returns:
            task_id: Task identifier for tracking
        """
        print(f"\n📝 Submitting request...")
        print(f"   Prompt: {prompt}")
        
        task_id = self.producer.create_task(prompt, metadata)
        print(f"   ✓ Task ID: {task_id}")
        
        return task_id
    
    def poll_result(
        self,
        task_id: str,
        poll_interval: float = 1.0,
        max_attempts: int = 60,
        verbose: bool = True
    ) -> Optional[dict]:
        """
        Poll for task result until completed or timeout
        
        Args:
            task_id: Task identifier
            poll_interval: Time between polls in seconds
            max_attempts: Maximum number of polling attempts
            verbose: Print polling progress
            
        Returns:
            Task result dictionary or None if timeout
        """
        if verbose:
            print(f"\n⏳ Polling for result (task: {task_id[:8]}...)...")
        
        for attempt in range(1, max_attempts + 1):
            # Get task status
            task_data = self.producer.get_task_status(task_id)
            status = task_data.get("status", "UNKNOWN")
            
            if verbose:
                print(f"   [{attempt}/{max_attempts}] Status: {status}")
            
            # Check if completed
            if status == settings.STATUS_COMPLETED:
                if verbose:
                    print("   ✓ Task completed!")
                return task_data
            
            # Check if failed
            if status == settings.STATUS_FAILED:
                if verbose:
                    print(f"   ✗ Task failed: {task_data.get('error', 'Unknown error')}")
                return task_data
            
            # Check if not found
            if status in ["NOT_FOUND", "ERROR"]:
                if verbose:
                    print(f"   ✗ Error: {task_data.get('error', 'Unknown error')}")
                return None
            
            # Wait before next poll
            time.sleep(poll_interval)
        
        if verbose:
            print(f"   ⏱️  Timeout after {max_attempts} attempts")
        return None
    
    def submit_and_wait(
        self,
        prompt: str,
        metadata: dict = None,
        poll_interval: float = 1.0,
        max_attempts: int = 60
    ) -> Optional[dict]:
        """
        Submit a request and wait for the result
        
        Args:
            prompt: Text prompt
            metadata: Optional metadata
            poll_interval: Time between polls
            max_attempts: Maximum polling attempts
            
        Returns:
            Task result or None
        """
        task_id = self.submit_request(prompt, metadata)
        result = self.poll_result(task_id, poll_interval, max_attempts)
        return result
    
    def display_result(self, result: dict):
        """Display the result in a formatted way"""
        print("\n" + "="*70)
        print("📊 RESULT")
        print("="*70)
        
        if not result:
            print("No result available")
            return
        
        print(f"Task ID: {result.get('task_id', 'N/A')}")
        print(f"Status: {result.get('status', 'N/A')}")
        print(f"Prompt: {result.get('prompt', 'N/A')}")
        
        if result.get('status') == settings.STATUS_COMPLETED:
            print(f"\nGenerated Text:")
            print("-" * 70)
            print(result.get('result', 'N/A'))
            print("-" * 70)
            
            created_at = result.get('created_at', 0)
            completed_at = result.get('completed_at', 0)
            if created_at and completed_at:
                duration = completed_at - created_at
                print(f"\nProcessing time: {duration:.2f} seconds")
        
        elif result.get('status') == settings.STATUS_FAILED:
            print(f"\nError: {result.get('error', 'Unknown error')}")
        
        print("="*70)
    
    def close(self):
        """Close connections"""
        self.producer.close()


def test_single_request():
    """Test a single request with polling"""
    print("\n" + "="*70)
    print("🧪 TEST 1: Single Request with Polling")
    print("="*70)
    
    client = TextGenerationClient()
    
    try:
        result = client.submit_and_wait(
            prompt="Write a short poem about machine learning",
            metadata={"test_id": 1},
            poll_interval=1.0,
            max_attempts=30
        )
        
        client.display_result(result)
        
    finally:
        client.close()


def test_multiple_requests():
    """Test multiple concurrent requests"""
    print("\n" + "="*70)
    print("🧪 TEST 2: Multiple Concurrent Requests")
    print("="*70)
    
    client = TextGenerationClient()
    
    try:
        prompts = [
            "Explain deep learning in one paragraph",
            "Write a function to calculate fibonacci numbers",
            "What is the future of artificial intelligence?"
        ]
        
        # Submit all requests
        task_ids = []
        for i, prompt in enumerate(prompts, 1):
            task_id = client.submit_request(
                prompt=prompt,
                metadata={"batch_id": "test2", "order": i}
            )
            task_ids.append(task_id)
        
        print(f"\n✓ Submitted {len(task_ids)} requests")
        
        # Poll for all results
        results = []
        for i, task_id in enumerate(task_ids, 1):
            print(f"\n--- Waiting for task {i}/{len(task_ids)} ---")
            result = client.poll_result(task_id, poll_interval=1.0, max_attempts=30)
            results.append(result)
        
        # Display all results
        for i, result in enumerate(results, 1):
            print(f"\n{'='*70}")
            print(f"RESULT {i}/{len(results)}")
            client.display_result(result)
        
    finally:
        client.close()


def interactive_mode():
    """Interactive mode for testing"""
    print("\n" + "="*70)
    print("🎮 Interactive Mode")
    print("="*70)
    print("Enter prompts to generate text (or 'quit' to exit)")
    
    client = TextGenerationClient()
    
    try:
        while True:
            print("\n" + "-"*70)
            prompt = input("Enter prompt: ").strip()
            
            if prompt.lower() in ['quit', 'exit', 'q']:
                print("Exiting...")
                break
            
            if not prompt:
                print("Please enter a valid prompt")
                continue
            
            result = client.submit_and_wait(
                prompt=prompt,
                poll_interval=1.0,
                max_attempts=30
            )
            
            client.display_result(result)
    
    except KeyboardInterrupt:
        print("\n\nExiting...")
    
    finally:
        client.close()


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "single":
            test_single_request()
        elif mode == "multiple":
            test_multiple_requests()
        elif mode == "interactive":
            interactive_mode()
        else:
            print(f"Unknown mode: {mode}")
            print_usage()
    else:
        print_usage()
        print("\nRunning default: Single request test...\n")
        test_single_request()


def print_usage():
    """Print usage instructions"""
    print("\nUsage: python client_test.py [mode]")
    print("\nModes:")
    print("  single       - Test single request (default)")
    print("  multiple     - Test multiple concurrent requests")
    print("  interactive  - Interactive prompt mode")
    print("\nExamples:")
    print("  python client_test.py")
    print("  python client_test.py single")
    print("  python client_test.py multiple")
    print("  python client_test.py interactive")


if __name__ == "__main__":
    main()

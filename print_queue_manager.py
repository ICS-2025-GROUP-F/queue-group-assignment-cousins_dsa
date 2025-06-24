"""
Print Queue Manager - Main Class
Integration of all modules including Module 3 (Job Expiry & Cleanup)
"""

import threading
import time
from typing import List, Dict, Any
from job_expiry import JobExpiryManager


class PrintQueueManager:
    """
    Main Print Queue Manager class that integrates all modules.
    Module 3 (Job Expiry & Cleanup) functions are integrated here.
    """

    def __init__(self, capacity=10, aging_interval=5, expiry_time=20, job_expiry_time=300):
        """
        Initialize the Print Queue Manager

        Args:
            capacity: Maximum number of jobs in queue
            aging_interval: Ticks between priority aging (Module 2)
            expiry_time: Time in ticks after which jobs expire (for tick-based modules)
            job_expiry_time: Time in seconds after which jobs expire (Module 3)
        """
        # Core queue properties
        self.capacity = capacity
        self.queue = []  # List to store job dictionaries
        self.current_size = 0

        # Thread safety
        self.lock = threading.Lock()

        # Time management
        self.current_time = 0  # Current simulation tick (for other modules)
        self.aging_interval = aging_interval
        self.expiry_time = expiry_time

        # Module 3: Initialize Job Expiry Manager
        self.expiry_manager = JobExpiryManager(expiry_time_seconds=job_expiry_time)

        print(f"PrintQueueManager initialized:")
        print(f"  - Capacity: {capacity}")
        print(f"  - Aging interval: {aging_interval} ticks")
        print(f"  - Job expiry time: {job_expiry_time} seconds")

    # ========== CORE QUEUE OPERATIONS ==========

    def enqueue_job(self, user_id: str, job_id: str, priority: int = 1) -> bool:
        """
        Add a job to the queue

        Args:
            user_id: ID of the user submitting the job
            job_id: Unique identifier for the job
            priority: Job priority (higher number = higher priority)

        Returns:
            True if job was added successfully, False otherwise
        """
        with self.lock:
            if self.current_size >= self.capacity:
                print(f"❌ Queue is full! Cannot add job {job_id} for user {user_id}")
                return False

            # Create job dictionary
            job = {
                'user_id': user_id,
                'job_id': job_id,
                'priority': priority,
                'start_tick': self.current_time,  # For tick-based modules
                'start_time': time.time(),  # Set immediately when job is added
                'waiting_time': 0,
                'submission_time': self.current_time
            }

            # Add to queue
            self.queue.append(job)
            self.current_size += 1

            print(f"✅ Added job {job_id} for user {user_id} (Priority: {priority})")
            return True

    def dequeue_job(self) -> Dict:
        """
        Remove and return the next job to be printed

        Returns:
            Job dictionary or None if queue is empty
        """
        with self.lock:
            if self.current_size == 0:
                print("❌ Queue is empty! No jobs to print.")
                return None

            # Sort by priority first, then by waiting time for tie-breaking
            self.queue.sort(key=lambda x: (-x['priority'], x['start_time']))

            job = self.queue.pop(0)
            self.current_size -= 1

            print(f"🖨️  Printing job {job['job_id']} for user {job['user_id']}")
            return job

    def print_job(self):
        """
        Print the next job in the queue (wrapper for dequeue_job)
        """
        return self.dequeue_job()

    # ========== MODULE 3 FUNCTIONS (Job Expiry & Cleanup) ==========

    def remove_expired_jobs(self):
        """
        Remove expired jobs from the queue.
        This function integrates your Module 3 functionality.
        """
        with self.lock:
            original_size = len(self.queue)
            self.queue = self.expiry_manager.remove_expired_jobs(self.queue)
            self.current_size = len(self.queue)

            expired_count = original_size - self.current_size
            if expired_count > 0:
                print(f"🗑️  Removed {expired_count} expired jobs. Queue size: {self.current_size}")

    def update_job_waiting_times(self):
        """
        Update waiting times for all jobs.
        This calls your Module 3 functionality.
        """
        self.expiry_manager.update_waiting_times(self.queue)

    def get_expiry_report(self) -> List[Dict]:
        """
        Get report of all expired jobs.
        """
        return self.expiry_manager.get_expired_jobs_report()

    def set_job_expiry_time(self, seconds: int):
        """
        Configure job expiry time.
        """
        self.expiry_manager.set_expiry_time(seconds)

    def get_jobs_near_expiry(self, threshold_percent=0.8) -> List[Dict]:
        """
        Get jobs that are close to expiring.
        """
        return self.expiry_manager.get_jobs_near_expiry(self.queue, threshold_percent)

    def get_expiry_statistics(self) -> Dict:
        """
        Get statistics about job expiry.
        """
        stats = self.expiry_manager.get_expiry_statistics()
        stats['current_queue_size'] = self.current_size
        stats['queue_capacity'] = self.capacity
        return stats

    # ========== PLACEHOLDER FUNCTIONS FOR OTHER MODULES ==========

    def apply_priority_aging(self):
        """
        Module 2: Apply priority aging to jobs
        TODO: To be implemented by Module 2 owner
        """
        # Placeholder - Module 2 will implement this
        if self.current_time % self.aging_interval == 0 and self.queue:
            print(f"[PLACEHOLDER] Priority aging should be applied at tick {self.current_time}")
            # Simple aging implementation for demonstration
            for job in self.queue:
                if job['waiting_time'] > self.aging_interval:
                    job['priority'] += 1
                    print(f"  → Job {job['job_id']} priority increased to {job['priority']}")

    def handle_simultaneous_submissions(self, jobs: List[Dict]):
        """
        Module 4: Handle concurrent job submissions
        TODO: To be implemented by Module 4 owner
        """
        print(f"[PLACEHOLDER] Simultaneous submission of {len(jobs)} jobs")

        # Thread-safe simultaneous submission
        with self.lock:
            successful_submissions = 0
            for job in jobs:
                if self.enqueue_job(job['user_id'], job['job_id'], job.get('priority', 1)):
                    successful_submissions += 1
            print(f"Successfully submitted {successful_submissions}/{len(jobs)} jobs")

    def send_simultaneous(self, jobs: List[Dict]):
        """
        Handle simultaneous job submissions (alternative method name)
        """
        self.handle_simultaneous_submissions(jobs)

    def tick(self):
        """
        Module 5: Simulate time passing
        This calls functions from all modules including Module 3!
        """
        with self.lock:
            self.current_time += 1
            print(f"\n⏰ TICK {self.current_time}")

            # Module 3: Job expiry functions (THESE ARE YOUR FUNCTIONS!)
            self.expiry_manager.advance_tick()  # Advance the expiry manager's time
            self.update_job_waiting_times()  # Update waiting times
            self.remove_expired_jobs()  # Remove expired jobs

            # Module 2: Priority aging (placeholder)
            self.apply_priority_aging()

            print(f"   Queue size after tick: {self.current_size}")

    def show_status(self):
        """
        Module 6: Display current queue status
        Enhanced to show Module 3 information!
        """
        with self.lock:
            # Update waiting times before showing status
            self.update_job_waiting_times()

            print("\n" + "=" * 60)
            print("🖨️  PRINT QUEUE STATUS")
            print("=" * 60)
            print(f"📊 Queue Size: {self.current_size}/{self.capacity}")
            print(f"⏰ Current Time: {self.current_time} ticks")

            if self.queue:
                print("\n📋 Jobs in Queue (sorted by priority):")
                # Sort queue for display
                sorted_queue = sorted(self.queue, key=lambda x: (-x['priority'], x['start_time']))

                for i, job in enumerate(sorted_queue):
                    waiting_time = job.get('waiting_time', 0)
                    waiting_str = f"{waiting_time:.1f}s"

                    print(f"   {i + 1}. User: {job['user_id']:<10} | "
                          f"Job: {job['job_id']:<10} | "
                          f"Priority: {job['priority']:<3} | "
                          f"Waiting: {waiting_str}")
            else:
                print("\n📋 Queue is empty")

            # Module 3: Show expiry information
            expiry_stats = self.get_expiry_statistics()
            print(f"\n🗑️  Expiry Statistics:")
            print(f"   Total Expired Jobs: {expiry_stats['total_expired_jobs']}")
            print(f"   Expiry Time: {expiry_stats['current_expiry_time']} seconds")

            # Show near expiry jobs
            near_expiry = self.get_jobs_near_expiry()
            if near_expiry:
                print(f"\n⚠️  Jobs Near Expiry ({len(near_expiry)}):")
                for job in near_expiry:
                    waiting_time = job.get('waiting_time', 0)
                    waiting_str = f"{waiting_time:.1f}s"
                    print(f"      Job {job['job_id']} - {waiting_str}")

            print("=" * 60 + "\n")


# Test function
def test_print_queue_manager():
    """
    Test the PrintQueueManager with Module 3 integration
    """
    print("=== Testing Print Queue Manager with Module 3 Integration ===")

    # Create queue manager with short expiry for testing
    pq_manager = PrintQueueManager(capacity=5, job_expiry_time=4)  # 4 seconds for testing

    # Add some test jobs
    pq_manager.enqueue_job("alice", "document1", 1)
    pq_manager.enqueue_job("bob", "presentation", 2)
    pq_manager.enqueue_job("charlie", "report", 1)

    # Show initial status
    pq_manager.show_status()

    # Simulate time passing with real time delays
    print("Simulating time passage...")
    for i in range(3):
        print(f"\n--- Waiting 2 seconds then tick {i + 1} ---")
        time.sleep(2)  # Wait 2 seconds
        pq_manager.tick()

        if i == 1:  # Print a job in the middle
            pq_manager.print_job()

        pq_manager.show_status()

    # Wait for jobs to expire
    print("\n--- Waiting for remaining jobs to expire ---")
    time.sleep(3)
    pq_manager.tick()
    pq_manager.show_status()

    # Show expiry report
    expired_jobs = pq_manager.get_expiry_report()
    print(f"\n📊 Final Expiry Report: {len(expired_jobs)} jobs expired during test")

    print("=== Test Complete ===")

if __name__ == "__main__":
    test_print_queue_manager()
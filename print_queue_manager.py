import threading
import time
from typing import List, Dict, Any


class PrintQueueManager:
    def __init__(self, capacity=10, aging_interval=5, job_expiry_time=300):
        self.capacity = capacity
        self.queue = []
        self.current_size = 0
        self.lock = threading.Lock()

        # Timing and aging
        self.aging_interval = aging_interval
        self.job_expiry_time = job_expiry_time  # Fixed parameter name
        self.current_time = 0

        # Module 3: Job Expiry tracking
        self.expired_jobs = []
        self.total_expired_jobs = 0

        print(f"PrintQueueManager initialized with capacity: {capacity}")

    def enqueue_job(self, user_id: str, job_id: str, priority: int = 1) -> bool:
        with self.lock:
            if self.current_size >= self.capacity:
                print(f"Queue is full! Cannot add job {job_id}")
                return False

            job = {
                'user_id': user_id,
                'job_id': job_id,
                'priority': priority,
                'start_time': time.time(),
                'waiting_time': 0,
                'submission_time': self.current_time
            }

            self.queue.append(job)
            self.current_size += 1
            print(f"Added job {job_id} for user {user_id}")
            return True

    def print_job(self, job_id: str = None) -> Dict:
        """Print a job. If job_id is provided, print that specific job. Otherwise, print highest priority job."""
        with self.lock:
            if self.current_size == 0:
                print("Queue is empty!")
                return None

            if job_id:
                # Find and remove specific job
                for i, job in enumerate(self.queue):
                    if job['job_id'] == job_id:
                        removed_job = self.queue.pop(i)
                        self.current_size -= 1
                        print(f"Printing job {job_id} for user {removed_job['user_id']}")
                        return removed_job
                print(f"Job {job_id} not found in queue")
                return None
            else:
                # Print highest priority job (existing logic)
                self.queue.sort(key=lambda x: (-x['priority'], x['start_time']))
                job = self.queue.pop(0)
                self.current_size -= 1
                print(f"Printing job {job['job_id']} for user {job['user_id']}")
                return job

    def apply_priority_aging(self):
        """Apply priority aging to jobs that have waited long enough"""
        with self.lock:
            for job in self.queue:
                # Update waiting time
                job['waiting_time'] = time.time() - job['start_time']

                # Apply aging if job has waited long enough
                if job['waiting_time'] > self.aging_interval:
                    job['priority'] += 1
                    print(f"Job {job['job_id']} priority increased to {job['priority']}")

    def remove_expired_jobs(self):
        """Remove jobs that have exceeded the expiry time"""
        with self.lock:
            current_time = time.time()
            remaining_jobs = []

            for job in self.queue:
                job['waiting_time'] = current_time - job['start_time']

                if job['waiting_time'] >= self.job_expiry_time:
                    # Job expired
                    expired_job = job.copy()
                    expired_job['expiry_time'] = current_time
                    expired_job['final_waiting_time'] = job['waiting_time']
                    self.expired_jobs.append(expired_job)
                    self.total_expired_jobs += 1
                    print(f"Job {job['job_id']} expired after {job['waiting_time']:.1f}s")
                else:
                    remaining_jobs.append(job)

            self.queue = remaining_jobs
            self.current_size = len(self.queue)

    def send_simultaneous(self, jobs: List[Dict]):
        """Handle simultaneous job submissions"""
        print(f"Processing {len(jobs)} simultaneous submissions")

        successful = 0
        for job in jobs:
            if self.enqueue_job(
                    job.get('user_id', ''),
                    job.get('job_id', ''),
                    job.get('priority', 1)
            ):
                successful += 1

        print(f"Successfully submitted {successful}/{len(jobs)} jobs")

    def tick(self):
        """Simulate time passing - update waiting times, apply aging, remove expired jobs"""
        with self.lock:
            self.current_time += 1
            print(f"\n== TICK {self.current_time} ==")

            # Update waiting times for all jobs
            current_time = time.time()
            for job in self.queue:
                job['waiting_time'] = current_time - job['start_time']

            # Apply priority aging
            self.apply_priority_aging()

            # Remove expired jobs
            self.remove_expired_jobs()

            print(f"Queue size after tick: {self.current_size}")

    def show_status(self):
        """Display current queue status"""
        with self.lock:
            print("\n" + "=" * 50)
            print("PRINT QUEUE STATUS")
            print("=" * 50)
            print(f"Queue Size: {self.current_size}/{self.capacity}")
            print(f"Current Time: {self.current_time}")

            if self.queue:
                print("\nJobs in Queue:")
                # Sort for display (highest priority first, then by start time)
                sorted_queue = sorted(self.queue, key=lambda x: (-x['priority'], x['start_time']))

                for i, job in enumerate(sorted_queue):
                    waiting_time = job.get('waiting_time', 0)
                    print(f"  {i + 1}. User: {job['user_id']:<10} | "
                          f"Job: {job['job_id']:<10} | "
                          f"Priority: {job['priority']:<3} | "
                          f"Waiting: {waiting_time:.1f}s")
            else:
                print("\nQueue is empty")

            print(f"\nTotal Expired Jobs: {self.total_expired_jobs}")
            print("=" * 50)



    def get_expiry_report(self) -> List[Dict]:
        """Get list of expired jobs for reporting"""
        return self.expired_jobs.copy()

    def get_jobs_near_expiry(self, threshold_percent: float = 0.8) -> List[Dict]:
        """Get jobs that are close to expiring"""
        threshold_time = self.job_expiry_time * threshold_percent
        near_expiry_jobs = []

        current_time = time.time()
        for job in self.queue:
            job['waiting_time'] = current_time - job['start_time']
            if job['waiting_time'] >= threshold_time:
                near_expiry_jobs.append(job.copy())

        return near_expiry_jobs

    def get_expiry_statistics(self) -> Dict[str, Any]:
        """Get statistics about job expiry"""
        return {
            'total_expired_jobs': self.total_expired_jobs,
            'current_expiry_time': self.job_expiry_time,
            'expired_jobs_this_session': len(self.expired_jobs)
        }

    def set_job_expiry_time(self, seconds: int) -> None:
        """Set new job expiry time"""
        self.job_expiry_time = seconds
        print(f"Job expiry time updated to {seconds} seconds")

    # ========== UTILITY METHODS ==========

    def get_queue_size(self) -> int:
        """Get current queue size"""
        return self.current_size

    def is_full(self) -> bool:
        """Check if queue is full"""
        return self.current_size >= self.capacity

    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return self.current_size == 0

    def get_expired_jobs(self) -> List[Dict]:
        """Get list of expired jobs"""
        return self.expired_jobs.copy()


def main():
    """Main function for testing"""
    print("== PRINT QUEUE SIMULATION ==")

    # Create print queue manager
    pq_manager = PrintQueueManager(capacity=5, job_expiry_time=10)

    # Demonstrate all functionality
    print("\n1. Adding jobs...")
    pq_manager.enqueue_job("alice", "doc1", 1)
    pq_manager.enqueue_job("bob", "doc2", 2)
    pq_manager.enqueue_job("charlie", "doc3", 1)

    print("\n2. Initial status...")
    pq_manager.show_status()

    print("\n3. Processing tick...")
    pq_manager.tick()

    print("\n4. Printing a job...")
    pq_manager.print_job()

    print("\n5. Final status...")
    pq_manager.show_status()

    print("\n== SIMULATION COMPLETE ==")


if __name__ == "__main__":
    main()

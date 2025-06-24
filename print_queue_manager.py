import threading
import time
from typing import List, Dict, Any
from job_expiry_module import JobExpiryManager

class PrintQueueManager:
    def __init__(self, capacity=10, aging_interval=5, expiry_time=20, job_expiry_time=300):
        self.capacity = capacity
        self.queue = []
        self.current_size = 0
        self.lock = threading.Lock()
        self.current_time = 0
        self.aging_interval = aging_interval
        self.expiry_time = expiry_time
        self.expiry_manager = JobExpiryManager(expiry_time_seconds=job_expiry_time)

        print(f"PrintQueueManager initialized:")
        print(f"  - Capacity: {capacity}")
        print(f"  - Aging interval: {aging_interval} ticks")
        print(f"  - Job expiry time: {job_expiry_time} seconds")

    def enqueue_job(self, user_id: str, job_id: str, priority: int = 1) -> bool:
        with self.lock:
            if self.current_size >= self.capacity:
                print(f"Queue is full! Cannot add job {job_id} for user {user_id}")
                return False

            job = {
                'user_id': user_id,
                'job_id': job_id,
                'priority': priority,
                'start_tick': self.current_time,
                'start_time': time.time(),
                'waiting_time': 0,
                'submission_time': self.current_time
            }

            self.queue.append(job)
            self.current_size += 1

            print(f"Added job {job_id} for user {user_id} (Priority: {priority})")
            return True

    def dequeue_job(self) -> Dict:
        with self.lock:
            if self.current_size == 0:
                print("Queue is empty! No jobs to print.")
                return None

            self.queue.sort(key=lambda x: (-x['priority'], x['start_time']))
            job = self.queue.pop(0)
            self.current_size -= 1

            print(f"Printing job {job['job_id']} for user {job['user_id']}")
            return job

    def print_job(self, job_id=None):
        return self.dequeue_job()

    def remove_expired_jobs(self):
        with self.lock:
            original_size = len(self.queue)
            self.queue = self.expiry_manager.remove_expired_jobs(self.queue)
            self.current_size = len(self.queue)
            expired_count = original_size - self.current_size
            if expired_count > 0:
                print(f"Removed {expired_count} expired jobs. Queue size: {self.current_size}")

    def update_job_waiting_times(self):
        self.expiry_manager.update_waiting_times(self.queue)

    def get_expiry_report(self) -> List[Dict]:
        return self.expiry_manager.get_expired_jobs_report()

    def set_job_expiry_time(self, seconds: int):
        self.expiry_manager.set_expiry_time(seconds)

    def get_jobs_near_expiry(self, threshold_percent=0.8) -> List[Dict]:
        return self.expiry_manager.get_jobs_near_expiry(self.queue, threshold_percent)

    def get_expiry_statistics(self) -> Dict:
        stats = self.expiry_manager.get_expiry_statistics()
        stats['current_queue_size'] = self.current_size
        stats['queue_capacity'] = self.capacity
        return stats

    def apply_priority_aging(self):
        if self.current_time % self.aging_interval == 0 and self.queue:
            for job in self.queue:
                if job['waiting_time'] > self.aging_interval:
                    job['priority'] += 1
                    print(f"Job {job['job_id']} priority increased to {job['priority']}")

    def handle_simultaneous_submissions(self, jobs: List[Dict]):
        print(f"Simultaneous submission of {len(jobs)} jobs")
        with self.lock:
            successful_submissions = 0
            for job in jobs:
                if self.enqueue_job(job['user_id'], job['job_id'], job.get('priority', 1)):
                    successful_submissions += 1
            print(f"Successfully submitted {successful_submissions}/{len(jobs)} jobs")

    def send_simultaneous(self, jobs: List[Dict]):
        self.handle_simultaneous_submissions(jobs)

    def tick(self):
        with self.lock:
            self.current_time += 1
            print(f"\nTICK {self.current_time}")
            self.expiry_manager.advance_tick()
            self.update_job_waiting_times()
            self.remove_expired_jobs()
            self.apply_priority_aging()
            print(f"Queue size after tick: {self.current_size}")

    def show_status(self):
        with self.lock:
            self.update_job_waiting_times()
            print("\n" + "=" * 60)
            print("PRINT QUEUE STATUS")
            print("=" * 60)
            print(f"Queue Size: {self.current_size}/{self.capacity}")
            print(f"Current Time: {self.current_time} ticks")

            if self.queue:
                print("\nJobs in Queue (sorted by priority):")
                sorted_queue = sorted(self.queue, key=lambda x: (-x['priority'], x['start_time']))
                for i, job in enumerate(sorted_queue):
                    waiting_time = job.get('waiting_time', 0)
                    waiting_str = f"{waiting_time:.1f}s"
                    print(f"   {i + 1}. User: {job['user_id']:<10} | "
                          f"Job: {job['job_id']:<10} | "
                          f"Priority: {job['priority']:<3} | "
                          f"Waiting: {waiting_str}")
            else:
                print("\nQueue is empty")

            expiry_stats = self.get_expiry_statistics()
            print(f"\nExpiry Statistics:")
            print(f"   Total Expired Jobs: {expiry_stats['total_expired_jobs']}")
            print(f"   Expiry Time: {expiry_stats['current_expiry_time']} seconds")

            near_expiry = self.get_jobs_near_expiry()
            if near_expiry:
                print(f"\nJobs Near Expiry ({len(near_expiry)}):")
                for job in near_expiry:
                    waiting_time = job.get('waiting_time', 0)
                    waiting_str = f"{waiting_time:.1f}s"
                    print(f"      Job {job['job_id']} - {waiting_str}")

            print("=" * 60 + "\n")

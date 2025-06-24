import threading
import time
from datetime import datetime
from collections import deque
import heapq


class Job:
    def __init__(self, user_id, job_id, priority, submission_time=0):
        self.user_id = user_id
        self.job_id = job_id
        self.priority = priority
        self.original_priority = priority
        self.submission_time = submission_time
        self.waiting_time = 0

    def __lt__(self, other):
        return self.priority > other.priority

    def __repr__(self):
        return f"Job(user={self.user_id}, job={self.job_id}, priority={self.priority}, wait={self.waiting_time})"


class PrintQueueManager:
    def __init__(self, capacity=10, aging_interval=5, expiry_time=20):
        self.capacity = capacity
        self.queue = []  # Using a list as priority queue with heapq
        self.lock = threading.RLock()  # Reentrant lock for nested calls
        self.current_time = 0
        self.aging_interval = aging_interval
        self.expiry_time = expiry_time
        self.job_history = []  # Track completed/expired jobs
        self.stats = {
            'total_submitted': 0,
            'total_completed': 0,
            'total_expired': 0,
            'total_rejected': 0
        }

    # Module 1: Core Queue Management
    def enqueue_job(self, user_id, job_id, priority):
        with self.lock:
            if len(self.queue) >= self.capacity:
                print(f"Queue full! Job {job_id} from user {user_id} rejected")
                self.stats['total_rejected'] += 1
                return False

            job = Job(user_id, job_id, priority, self.current_time)
            heapq.heappush(self.queue, job)
            self.stats['total_submitted'] += 1

            print(f"Job {job_id} from user {user_id} added to queue (priority: {priority})")
            return True

    def dequeue_job(self):
        with self.lock:
            if not self.queue:
                return None

            job = heapq.heappop(self.queue)
            self.stats['total_completed'] += 1
            self.job_history.append(('completed', job, self.current_time))

            print(f"Printing job {job.job_id} from user {job.user_id} (waited {job.waiting_time} time units)")
            return job

    def show_status(self):
        with self.lock:
            print(f"\nQueue Status at time {self.current_time}:")
            print(f"Queue size: {len(self.queue)}/{self.capacity}")
            print(f"Stats: Submitted={self.stats['total_submitted']}, "
                  f"Completed={self.stats['total_completed']}, "
                  f"Expired={self.stats['total_expired']}, "
                  f"Rejected={self.stats['total_rejected']}")

    # Module 2: Priority & Aging System
    def apply_priority_aging(self):
        with self.lock:
            if not self.queue:
                return

            jobs = []
            while self.queue:
                jobs.append(heapq.heappop(self.queue))

            aged_jobs = []
            for job in jobs:
                if job.waiting_time > 0 and job.waiting_time % self.aging_interval == 0:
                    job.priority += 1  # Increase priority
                    aged_jobs.append(job)

            for job in jobs:
                heapq.heappush(self.queue, job)

            if aged_jobs:
                print(f"Aged {len(aged_jobs)} jobs: {[f'{j.job_id}(+1)' for j in aged_jobs]}")

    # Module 3: Job Expiry & Cleanup
    def remove_expired_jobs(self):
        with self.lock:
            if not self.queue:
                return

            jobs = []
            expired_jobs = []

            while self.queue:
                job = heapq.heappop(self.queue)
                if job.waiting_time >= self.expiry_time:
                    expired_jobs.append(job)
                    self.stats['total_expired'] += 1
                    self.job_history.append(('expired', job, self.current_time))
                else:
                    jobs.append(job)
            for job in jobs:
                heapq.heappush(self.queue, job)

            if expired_jobs:
                print(f"💀 Expired {len(expired_jobs)} jobs: {[j.job_id for j in expired_jobs]}")

    # Module 4: Concurrent Job Submission Handling
    def handle_simultaneous_submissions(self, jobs):
        print(f"Handling {len(jobs)} simultaneous job submissions...")
        threads = []

        for job in jobs:
            t = threading.Thread(
                target=self.enqueue_job,
                args=(job["user_id"], job["job_id"], job["priority"])
            )
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        print("All simultaneous submissions processed")

    # Module 5: Event Simulation & Time Management
    def tick(self):
        with self.lock:
            self.current_time += 1

            for job in self.queue:
                job.waiting_time = self.current_time - job.submission_time

            self.apply_priority_aging()
            self.remove_expired_jobs()

    # Module 6: Visualization & Reporting
    def print_queue_snapshot(self):
        with self.lock:
            print(f"\n📸 Queue Snapshot at time {self.current_time}")
            print("=" * 60)

            if not self.queue:
                print("Queue is empty")
                return

            sorted_jobs = sorted(self.queue, reverse=True)  # Highest priority first

            print(f"{'Pos':<4} {'User':<8} {'Job ID':<10} {'Priority':<8} {'Wait Time':<10}")
            print("-" * 60)

            for i, job in enumerate(sorted_jobs, 1):
                print(f"{i:<4} {job.user_id:<8} {job.job_id:<10} "
                      f"{job.priority:<8} {job.waiting_time:<10}")

    def print_job(self, job_id):
        print(f"Printing job {job_id}...")
        time.sleep(0.1)  # Simulate print time
        print(f"Job {job_id} printed successfully")

    # Additional utility methods
    def get_queue_copy(self):
        """Return a copy of current queue for external analysis"""
        with self.lock:
            return list(self.queue)

    def clear_queue(self):
        """Emergency clear queue"""
        with self.lock:
            cleared_jobs = len(self.queue)
            self.queue.clear()
            print(f"Cleared {cleared_jobs} jobs from queue")

    def get_statistics(self):
        """Get comprehensive statistics"""
        with self.lock:
            return {
                'current_time': self.current_time,
                'queue_size': len(self.queue),
                'capacity_utilization': len(self.queue) / self.capacity * 100,
                **self.stats
            }


# Demo and testing function
def run_simulation():
    print("Print Queue Simulator Starting...")
    pqm = PrintQueueManager(capacity=5, aging_interval=3, expiry_time=10)

    # Initial jobs
    print("\n=== Initial Job Submissions ===")
    pqm.enqueue_job("Alice", "doc1.pdf", 2)
    pqm.enqueue_job("Bob", "report.docx", 1)
    pqm.enqueue_job("Charlie", "image.jpg", 3)
    pqm.print_queue_snapshot()

    # Simulate time passage
    print("\n=== Time Progression ===")
    for t in range(1, 8):
        print(f"\n--- Time {t} ---")
        pqm.tick()

        # Add some jobs at specific times
        if t == 2:
            pqm.enqueue_job("David", "slides.pptx", 1)
        elif t == 4:
            # Test simultaneous submissions
            simultaneous_jobs = [
                {"user_id": "Eve", "job_id": "urgent.pdf", "priority": 5},
                {"user_id": "Frank", "job_id": "normal.doc", "priority": 2},
                {"user_id": "Grace", "job_id": "low.txt", "priority": 1}
            ]
            pqm.handle_simultaneous_submissions(simultaneous_jobs)

        if t % 3 == 0:
            job = pqm.dequeue_job()
            if job:
                pqm.print_job(job.job_id)

        pqm.print_queue_snapshot()
        pqm.show_status()

    print("\n=== Final Statistics ===")
    stats = pqm.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    run_simulation()
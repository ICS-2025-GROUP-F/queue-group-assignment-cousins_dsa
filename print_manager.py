import threading
import time

class PrintQueueManager:
    def __init__(self, capacity=10, aging_interval=5, expiry_time=20):
        self.expired_jobs_log = None
        self.capacity = capacity
        self.queue = [None] * capacity
        self.front = 0
        self.rear = 0
        self.size = 0
        self.queue = []  # initialize your queue here
        self.lock = threading.Lock()
        self.current_time = 0
        self.aging_interval = aging_interval
        self.expiry_time = expiry_time

    # Module 1: Core Queue Management
    def enqueue_job(self, user_id, job_id, priority):
        with self.lock:
            if self.is_full():
                print(f"Queue is full! Cannot add job {job_id} from user {user_id}")
                return False

            job = {
                "user_id": user_id,
                "job_id": job_id,
                "priority": priority,
                "submission_time": self.current_time,
                "waiting_time": 0,
                "being_printed": False
            }

            self.queue[self.rear] = job
            self.rear = (self.rear + 1) % self.capacity
            self.size += 1
            print(f"Job {job_id} from user {user_id} added to queue (Priority: {priority})")
            return True

    def dequeue_job(self):
        with self.lock:
            if self.is_empty():
                return None

            best_job = None
            best_index = -1

            current_index = self.front
            for _ in range(self.size):
                job = self.queue[current_index]
                if job is not None and not job["being_printed"]:
                    if best_job is None or (job["priority"], job["waiting_time"]) < (best_job["priority"], best_job["waiting_time"]):
                        best_job = job
                        best_index = current_index
                current_index = (current_index + 1) % self.capacity

            if best_index != -1:
                # Remove the job from queue
                for _ in range((self.rear - best_index) % self.capacity):
                    next_index = (best_index + 1) % self.capacity
                    self.queue[best_index] = self.queue[next_index]
                    best_index = next_index
                self.rear = (self.rear - 1 + self.capacity) % self.capacity
                self.queue[self.rear] = None
                self.size -= 1
                return best_job

            return None

    def show_status(self):
        with self.lock:
            print("\nCurrent Queue Status:")
            print("====================")
            index = self.front
            for _ in range(self.size):
                job = self.queue[index]
                if job:
                    print(f"JobID: {job['job_id']}, UserID: {job['user_id']}, Priority: {job['priority']}, Waiting: {job['waiting_time']}s")
                index = (index + 1) % self.capacity
            print("====================\n")

    def is_empty(self):
        return self.size == 0

    def is_full(self):
        return self.size == self.capacity

    # Module 2: Priority & Aging System
    def apply_priority_aging(self):
        self.time_since_last_aging += 1
        
        if self.time_since_last_aging >= self.aging_interval:
            for job in self.queue:
                if not job['being_printed']:
                    job['priority'] = max(1, job['priority'] - 1)  
                    
            self.time_since_last_aging = 0
            
        self.queue.sort(key=lambda x: (x['priority'], x['waiting_time']))
    
    def _sort_queue_by_priority(self):
        self.queue.sort(key=lambda x: (x['priority'], x['waiting_time']))  # Implement aging logic and reorder queue
    
    # Module 3: Job Expiry & Cleanup

    def remove_expired_jobs(self):
        with self.lock:
            expired_jobs = []
            remaining_jobs = []

            for job in self.queue:
                if job['waiting_time'] >= self.expiry_time and not job['being_printed']:
                    expired_jobs.append(job)
                    # Log the expired job for reporting
                    self.expired_jobs_log.append({
                        'job_id': job['job_id'],
                        'user_id': job['user_id'],
                        'expired_at_time': self.current_time,
                        'total_wait_time': job['waiting_time']
                    })
                else:
                    remaining_jobs.append(job)

            # Update the queue with remaining jobs
            self.queue = remaining_jobs

            # Notify about expired jobs
            if expired_jobs:
                self._notify_expired_jobs(expired_jobs)

            return len(expired_jobs)  # Return count of expired jobs

    def _notify_expired_jobs(self, expired_jobs):
        print(f"\n EXPIRED JOBS ALERT - Time {self.current_time} ")
        for job in expired_jobs:
            print(f"   Job {job['job_id']} from User {job['user_id']} has expired!")
            print(f"   (Waited {job['waiting_time']}s, limit: {self.expiry_time}s)")
        print("=" * 50)

    def get_expired_jobs_report(self):

        if not self.expired_jobs_log:
            return "No jobs have expired yet."

        report = f"\n EXPIRED JOBS REPORT (Total: {len(self.expired_jobs_log)}) \n"
        report += "=" * 60 + "\n"

        for i, expired_job in enumerate(self.expired_jobs_log, 1):
            report += f"{i:2d}. Job {expired_job['job_id']} (User {expired_job['user_id']})\n"
            report += f"    Expired at: Time {expired_job['expired_at_time']}\n"
            report += f"    Total wait: {expired_job['total_wait_time']}s\n"
            report += "-" * 50 + "\n"

        return report

    def update_waiting_times(self):
        with self.lock:
            for job in self.queue:
                if not job['being_printed']:
                    job['waiting_time'] = self.current_time - job['submission_time']

    def cleanup_system(self):
        # Update waiting times first
        self.update_waiting_times()

        # Remove expired jobs
        expired_count = self.remove_expired_jobs()

        return expired_count


    # Module 4: Concurrent Job Submission Handling
    def handle_simultaneous_submissions(self, jobs):
        threads = []
        for job in jobs:
            t = threading.Thread(target=self.enqueue_job, args=(job["user_id"], job["job_id"], job["priority"]))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

    # Module 5: Event Simulation & Time Management
    def tick(self):
        with self.lock:
            self.current_time += 1
            print(f"\n[Tick {self.current_time}] Time has progressed.")

            for job in self.queue:
                job['waiting_time'] += 1

            if self.current_time % self.aging_interval == 0:
                self.apply_priority_aging()

            self.remove_expired_jobs()
            self.show_status()

    # Module 6: Visualization & Reporting
    def print_queue_snapshot(self):
        print(f"\n[Snapshot at time {self.current_time}]")
        for i, job in enumerate(self.queue):
            print(f"{i+1}. User: {job['user_id']}, Job: {job['job_id']}, Priority: {job['priority']}, Waiting: {job['waiting_time']}")

    # Printing jobs
    def print_jobs(self):
        with self.lock:
            if self.is_empty():
                print("No jobs to print - queue is empty")
                return False

            job = self.dequeue_job()
            if job:
                print(f"PRINTING: Job {job['job_id']} from user {job['user_id']} (Priority: {job['priority']}, Waited: {job['waiting_time']}s)")
                return True
            else:
                print("No printable job found")
                return False

import time
from typing import List, Dict, Any


class JobExpiryManager:

    def __init__(self, expiry_time_seconds: int = 300):
        self.expiry_time_seconds = expiry_time_seconds
        self.expired_jobs = []  # Track expired jobs for reporting
        self.total_expired_jobs = 0
        self.start_time = time.time()  # Track when manager started

        print(f"JobExpiryManager initialized with {expiry_time_seconds}s expiry time")

    def update_waiting_times(self, queue: List[Dict]) -> None:

        current_time = time.time()

        for job in queue:
            # Set start_time if not already set
            if job.get('start_time') is None:
                job['start_time'] = current_time

            # Calculate waiting time in seconds
            job['waiting_time'] = current_time - job['start_time']

    def remove_expired_jobs(self, queue: List[Dict]) -> List[Dict]:

        current_time = time.time()
        remaining_jobs = []

        for job in queue:
            # Ensure start_time is set
            if job.get('start_time') is None:
                job['start_time'] = current_time

            waiting_time = current_time - job['start_time']
            job['waiting_time'] = waiting_time

            # Check if job has expired
            if waiting_time >= self.expiry_time_seconds:
                # Job has expired - add to expired jobs list
                expired_job = job.copy()
                expired_job['expiry_time'] = current_time
                expired_job['final_waiting_time'] = waiting_time

                self.expired_jobs.append(expired_job)
                self.total_expired_jobs += 1

                print(f" Job {job['job_id']} by {job['user_id']} expired after {waiting_time:.1f}s")
            else:
                # Job is still valid
                remaining_jobs.append(job)

        return remaining_jobs

    def get_jobs_near_expiry(self, queue: List[Dict], threshold_percent: float = 0.8) -> List[Dict]:

        threshold_time = self.expiry_time_seconds * threshold_percent
        near_expiry_jobs = []

        for job in queue:
            waiting_time = job.get('waiting_time', 0)
            if waiting_time >= threshold_time:
                near_expiry_jobs.append(job)

        return near_expiry_jobs

    def get_expired_jobs_report(self) -> List[Dict]:

        return self.expired_jobs.copy()

    def get_expiry_statistics(self) -> Dict[str, Any]:

        return {
            'total_expired_jobs': self.total_expired_jobs,
            'current_expiry_time': self.expiry_time_seconds,
            'expired_jobs_this_session': len(self.expired_jobs),
            'manager_uptime': time.time() - self.start_time
        }

    def set_expiry_time(self, seconds: int) -> None:

        self.expiry_time_seconds = seconds
        print(f"Job expiry time updated to {seconds} seconds")

    def advance_tick(self) -> None:

        pass  # Time-based system doesn't need tick advancement

    def notify_expiry(self, job: Dict) -> None:

        print(f" NOTIFICATION: Job {job['job_id']} for user {job['user_id']} has expired!")

    def clear_expired_history(self) -> None:

        cleared_count = len(self.expired_jobs)
        self.expired_jobs.clear()
        print(f"Cleared {cleared_count} expired jobs from history")

    def get_time_until_expiry(self, job: Dict) -> float:

        waiting_time = job.get('waiting_time', 0)
        return self.expiry_time_seconds - waiting_time

import time
from typing import List, Dict, Any


class JobExpiryManager:
    def __init__(self, expiry_time_seconds: int = 300):
        self.expiry_time_seconds = expiry_time_seconds
        self.expired_jobs = []
        self.total_expired_jobs = 0

        # Use simulated time for testing compatibility
        self.current_time = 0
        self.start_time = 0

        print(f"JobExpiryManager initialized with {expiry_time_seconds}s expiry time")

    def update_waiting_times(self, queue: List[Dict]) -> None:
        """Update waiting times for all jobs in the queue"""
        for job in queue:
            if job.get('start_time') is None:
                job['start_time'] = self.current_time
            job['waiting_time'] = self.current_time - job['start_time']

    def remove_expired_jobs(self, queue: List[Dict]) -> List[Dict]:
        """Remove jobs that have exceeded the expiry time"""
        remaining_jobs = []

        for job in queue:
            # Ensure job has start time
            if job.get('start_time') is None:
                job['start_time'] = self.current_time

            waiting_time = self.current_time - job['start_time']
            job['waiting_time'] = waiting_time

            if waiting_time >= self.expiry_time_seconds:
                # Job expired
                expired_job = job.copy()
                expired_job['expiry_time'] = self.current_time
                expired_job['final_waiting_time'] = waiting_time

                self.expired_jobs.append(expired_job)
                self.total_expired_jobs += 1
                self.notify_expiry(job)

                print(f"Job {job['job_id']} by {job['user_id']} expired after {waiting_time:.1f}s")
            else:
                remaining_jobs.append(job)

        return remaining_jobs

    def get_jobs_near_expiry(self, queue: List[Dict], threshold_percent: float = 0.8) -> List[Dict]:
        """Get jobs that are close to expiring"""
        threshold_time = self.expiry_time_seconds * threshold_percent
        near_expiry_jobs = []

        for job in queue:
            waiting_time = job.get('waiting_time', 0)
            if waiting_time >= threshold_time:
                near_expiry_jobs.append(job)

        return near_expiry_jobs

    def get_expired_jobs_report(self) -> List[Dict]:
        """Get list of all expired jobs"""
        return self.expired_jobs.copy()

    def get_expiry_statistics(self) -> Dict[str, Any]:
        """Get statistics about job expiry"""
        return {
            'total_expired_jobs': self.total_expired_jobs,
            'current_expiry_time': self.expiry_time_seconds,
            'expired_jobs_this_session': len(self.expired_jobs),
            'manager_uptime': self.current_time - self.start_time
        }

    def set_expiry_time(self, seconds: int) -> None:
        """Set new job expiry time"""
        self.expiry_time_seconds = seconds
        print(f"Job expiry time updated to {seconds} seconds")

    def advance_tick(self) -> None:
        """Advance the simulated time by one unit"""
        self.current_time += 1

    def notify_expiry(self, job: Dict) -> None:
        """Notify when a job expires"""
        print(f"NOTIFICATION: Job {job['job_id']} for user {job['user_id']} has expired!")

    def clear_expired_history(self) -> None:
        """Clear the history of expired jobs"""
        cleared_count = len(self.expired_jobs)
        self.expired_jobs.clear()
        print(f"Cleared {cleared_count} expired jobs from history")

    def get_time_until_expiry(self, job: Dict[str, Any]) -> float:
        """Get time remaining until job expires"""
        waiting_time = job.get('waiting_time', 0)
        return max(0, self.expiry_time_seconds - waiting_time)

    def set_current_time(self, time_value: int) -> None:
        """Set the current simulated time (for testing)"""
        self.current_time = time_value

    def get_current_time(self) -> int:
        """Get the current simulated time"""
        return self.current_time


def main():
    """Test the JobExpiryManager"""
    print("== Testing JobExpiryManager ==")

    # Create manager with short expiry time for testing
    expiry_manager = JobExpiryManager(expiry_time_seconds=5)

    # Create test queue with some jobs
    test_queue = [
        {
            'user_id': 'alice',
            'job_id': 'doc1',
            'priority': 1,
            'start_time': 0
        },
        {
            'user_id': 'bob',
            'job_id': 'doc2',
            'priority': 2,
            'start_time': 0
        },
        {
            'user_id': 'charlie',
            'job_id': 'doc3',
            'priority': 1,
            'start_time': 0
        }
    ]

    print(f"\n1. Initial queue has {len(test_queue)} jobs")

    # Test over time
    for tick in range(8):
        expiry_manager.set_current_time(tick)
        expiry_manager.update_waiting_times(test_queue)

        print(f"\nTick {tick}:")
        print(f"  Queue size: {len(test_queue)}")

        # Check jobs near expiry
        near_expiry = expiry_manager.get_jobs_near_expiry(test_queue)
        if near_expiry:
            print(f"  Jobs near expiry: {[job['job_id'] for job in near_expiry]}")

        # Remove expired jobs
        test_queue = expiry_manager.remove_expired_jobs(test_queue)
        print(f"  Remaining jobs: {[job['job_id'] for job in test_queue]}")

        # Show statistics
        stats = expiry_manager.get_expiry_statistics()
        print(f"  Total expired: {stats['total_expired_jobs']}")

    # Final report
    print(f"\n2. Final Statistics:")
    final_stats = expiry_manager.get_expiry_statistics()
    for key, value in final_stats.items():
        print(f"   {key}: {value}")

    print(f"\n3. Expired Jobs Report:")
    expired_jobs = expiry_manager.get_expired_jobs_report()
    for job in expired_jobs:
        print(f"   Job {job['job_id']} expired at time {job['expiry_time']} after {job['final_waiting_time']}s")




if __name__ == "__main__":
    main()
from print_queue_manager import PrintQueueManager
import time
def test_basic_expiry():
    print("== Testing Basic Job Expiry ==")
    manager = PrintQueueManager(capacity=10, job_expiry_time=3)

    # Add jobs
    manager.enqueue_job("alice", "doc1", 1)
    manager.enqueue_job("bob", "doc2", 2)
    manager.enqueue_job("charlie", "doc3", 1)

    print("Initial queue:")
    manager.show_status()

    print("Waiting 4 seconds for jobs to expire...")
    time.sleep(4)

    print("After waiting 4 seconds (before tick):")
    manager.show_status()  # This should show updated waiting times

    print("Calling tick() to process expiry...")
    manager.tick()

    print("After expiry processing:")
    manager.show_status()

    expired_jobs = manager.get_expiry_report()
    print(f"\nExpired jobs report: {len(expired_jobs)} jobs expired")
    for job in expired_jobs:
        waiting_time = job.get('final_waiting_time', job.get('waiting_time', 0))
        print(f"  - Job {job['job_id']} by {job['user_id']} expired after {waiting_time:.1f} seconds")


def test_step_by_step_expiry():
    print("\n== Testing Step-by-Step Expiry ==")
    manager = PrintQueueManager(capacity=5, job_expiry_time=3)

    # Add a single job for clear tracking
    manager.enqueue_job("test_user", "test_job", 1)

    print("Job added. Tracking expiry progress:")

    for i in range(5):
        print(f"\n--- After {i} seconds ---")
        manager.show_status()

        if i < 4:  # Don't sleep after the last iteration
            time.sleep(1)

        # Check if job expired
        if i >= 3:  # After 3 seconds, job should expire
            manager.tick()
            print("Tick called - checking for expired jobs...")


def test_near_expiry_warnings():
    print("\n== Testing Near Expiry Warnings ==")
    manager = PrintQueueManager(capacity=10, job_expiry_time=5)

    manager.enqueue_job("user1", "urgent_doc", 3)
    manager.enqueue_job("user2", "report", 1)

    print("Jobs added. Waiting to approach expiry threshold...")

    # Wait for 4 seconds (80% of 5 second expiry time)
    time.sleep(4)
    manager.tick()

    print("After 4 seconds (80% of expiry time):")
    manager.show_status()

    near_expiry = manager.get_jobs_near_expiry(threshold_percent=0.8)
    print(f"\nJobs near expiry (>80% of expiry time): {len(near_expiry)}")
    for job in near_expiry:
        print(f"  - Job {job['job_id']} has been waiting {job['waiting_time']:.1f}s")


def test_mixed_scenario():
    print("\n== Testing Mixed Scenario (Process + Expire) ==")
    manager = PrintQueueManager(capacity=10, job_expiry_time=4)

    # Add jobs with different priorities
    manager.enqueue_job("alice", "doc1", 1)
    manager.enqueue_job("bob", "doc2", 3)  # Higher priority
    manager.enqueue_job("charlie", "doc3", 2)

    print("Initial state:")
    manager.show_status()

    # Wait 2 seconds, then process highest priority job
    print("\nWaiting 2 seconds...")
    time.sleep(2)
    manager.tick()

    print("Processing highest priority job:")
    processed = manager.print_job()
    if processed:
        print(f"Processed: {processed['job_id']} (Priority: {processed['priority']})")

    manager.show_status()

    # Wait another 3 seconds for remaining jobs to expire
    print("\nWaiting another 3 seconds for remaining jobs to expire...")
    time.sleep(3)
    manager.tick()

    print("Final state (jobs should be expired):")
    manager.show_status()

    # Show expiry report
    expired_jobs = manager.get_expiry_report()
    print(f"\nExpiry Report: {len(expired_jobs)} jobs expired")
    for job in expired_jobs:
        waiting_time = job.get('final_waiting_time', job.get('waiting_time', 0))
        print(f"  - {job['job_id']} (Priority: {job['priority']}) expired after {waiting_time:.1f}s")


def test_configuration_changes():
    print("\n== Testing Expiry Time Configuration ==")
    manager = PrintQueueManager(capacity=5, job_expiry_time=5)

    manager.enqueue_job("test_user", "config_test", 1)

    print("Initial expiry time: 5 seconds")
    stats = manager.get_expiry_statistics()
    print(f"Current expiry time: {stats['current_expiry_time']} seconds")

    # Change expiry time to 2 seconds
    print("\nChanging expiry time to 2 seconds...")
    manager.set_job_expiry_time(2)

    stats = manager.get_expiry_statistics()
    print(f"New expiry time: {stats['current_expiry_time']} seconds")

    # Wait 3 seconds (more than new expiry time)
    print("Waiting 3 seconds...")
    time.sleep(3)
    manager.tick()

    print("Status after configuration change:")
    manager.show_status()


if __name__ == "__main__":
    print("RUNNING MODULE 3 (JOB EXPIRY) TESTS")
    print("=" * 60)

    test_basic_expiry()
    test_step_by_step_expiry()
    test_near_expiry_warnings()
    test_mixed_scenario()
    test_configuration_changes()

    print("\n" + "=" * 60)
    print("ALL MODULE 3 TESTS COMPLETED")
    print("=" * 60)
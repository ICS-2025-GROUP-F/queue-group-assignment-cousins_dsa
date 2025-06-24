from print_manager import PrintQueueManager


if __name__ == "__main__":
    pq_manager = PrintQueueManager()
    user_id, job_id, priority = 2, 2, 3
    pq_manager.enqueue_job(user_id, job_id, priority)
    pq_manager.tick()
    pq_manager.print_job(job_id)
    pq_manager.show_status()
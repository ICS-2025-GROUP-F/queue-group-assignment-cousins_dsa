from print_queue_manager import PrintQueueManager

if __name__ == "__main__":

    pq_manager = PrintQueueManager()


    user_id, job_id, priority = "2", "2", 3

    print("Adding job to queue...")
    pq_manager.enqueue_job(user_id, job_id, priority)

    print("\nProcessing tick...")
    pq_manager.tick()

    print(f"\nPrinting job {job_id}...")
    printed_job = pq_manager.print_job(job_id)

    if printed_job:
        print(f"Successfully printed job: {printed_job}")
    else:
        print(f"Job {job_id} not found or queue is empty")


    print("\nFinal queue status:")
    pq_manager.show_status()
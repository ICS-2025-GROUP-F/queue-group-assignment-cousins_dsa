import threading
import time

class PrintQueueManager:
    def __init__(self, capacity=10, aging_interval=5, expiry_time=20):
        self.capacity = capacity
        self.queue = []  
        self.lock = threading.Lock()
        self.current_time = 0
        self.aging_interval = aging_interval
        self.expiry_time = expiry_time


    #  Member 5 
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

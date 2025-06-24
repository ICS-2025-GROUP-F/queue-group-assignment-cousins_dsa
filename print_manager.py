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

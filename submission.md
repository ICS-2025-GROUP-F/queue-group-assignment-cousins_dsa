# 📄 Print Queue Simulation - Submission File

## 🧠 Group Name
ICS-2025-GROUP-F

## 👥 Team Members

| Name            | Registration Number | Module Responsibility           |
|-----------------|---------------------|----------------------------------|
| Ian Kitheka     | 190118              | Core Queue Management           |
| Mwai Komo       | 170469              | Priority & Aging System         |
| Shylynn Wanjiru | 192108              | Job Expiry & Cleanup            |
| Karani Claude   | 178616              | Concurrent Submission Handling  |
| Kathy           | 192231              | Event Simulation & Time Mgmt    |


---

## 🧩 Module Descriptions

### Module 1: Core Queue Management
- Implemented by: Ian Kitheka
- Description: Handles circular queue logic, enqueuing, dequeuing, and queue status.

### Module 2: Priority & Aging System
- Implemented by: Mwai Komo
- Description: Implements priority-based sorting and aging mechanism to elevate waiting jobs.

### Module 3: Job Expiry & Cleanup
- Implemented by: Shylynn Wanjiru
- Description: Tracks waiting time, removes expired jobs, and logs expiration events.

### Module 4: Concurrent Submission Handling
- Implemented by:  Karani Claude
- Description: Supports multi-threaded simultaneous job submissions with thread safety.

### Module 5: Event Simulation & Time Management
- Implemented by: Kathy
- Description: Simulates time passage using `tick()`, updates jobs, applies aging and expiry.

### Module 6: Visualization & Reporting
- Implemented by:  Karani Claude
- Description: Provides a visual or CLI-based snapshot of the queue’s state.

---

## ▶️ How to Run the Code

### Prerequisites:
- Python 3.8+

### To run the simulation:
```bash
python main.py
```
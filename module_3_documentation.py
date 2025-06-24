"""
Module 3: Job Expiry & Cleanup - Documentation
Student: [Your Name]
Registration: 192108
Branch: 192108-ft-jobExpiry

== COMPLETED FEATURES ==
 JobExpiryManager class with configurable expiry time
 Automatic waiting time tracking for all jobs
 Expired job detection and removal
 Notification system for expired jobs
 Near-expiry warning system
 Integration functions for main PrintQueueManager
 Comprehensive test suite
 Statistics and reporting functionality

== INTEGRATION POINTS ===
Functions for other modules to use:
- remove_expired_jobs(): Call during tick() events (Module 5)
- update_job_waiting_times(): Call every tick to update times
- get_expiry_report(): Use for status visualization (Module 6)
- set_job_expiry_time(): Configure expiry time
- get_jobs_near_expiry(): Get warning list for priority system (Module 2)

== USAGE EXAMPLE ==
# In main system:
pq_manager = PrintQueueManager()
pq_manager.enqueue_job("user1", "job1", 1)
pq_manager.tick()  # This calls your module functions
pq_manager.show_status()  # Shows expiry information

== FILES CREATED ==
- job_expiry: Core module implementation
- print_queue_manager.py: Integration with main system
- test_module3.py: Test suite
- module3_documentation.py: This documentation

== READY FOR TEAM INTEGRATION ==
Module 3 is complete and ready to be merged with other team modules.
All functions are tested and documented.
"""
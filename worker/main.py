import os
import json
import time
import logging
import redis
import numpy as np
from prometheus_client import start_http_server

from inference_worker import InferenceWorker

# Config
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
MODEL_PATH = os.getenv("MODEL_PATH", "/models/resnet50.pt")
DEVICE = os.getenv("DEVICE", "cuda")
QUEUE_KEY = "ai_jobs:processing" # Simplified for demo, should pop from queue

logging.basicConfig(level=logging.INFO)

def main():
    # Start Prometheus server
    start_http_server(8081)
    
    # Init Worker
    worker = InferenceWorker(MODEL_PATH, DEVICE)
    worker.warmup()
    
    # Redis
    r = redis.from_url(REDIS_URL)
    
    logging.info("Worker started, listening for jobs...")
    
    # Simplified loop using BLPOP or similar from a queue
    # The Architecture describes a RedisJobQueue class, but usage here implies 
    # we need to pop from 'ai_jobs:queue:{priority}' or rely on the queue logic.
    # For this demo, let's assume we pull from a simplified list key.
    
    while True:
        try:
            # Simple demo polling, real one would use the sophisticated queue class
            # or BLPOP on multiple priority keys.
            # Here we just look for 'ai_jobs:queue:50'
            job_data_raw = r.rpop("ai_jobs:queue:50") 
            
            if job_data_raw:
                job_id = job_data_raw.decode('utf-8')
                logging.info(f"Processing job {job_id}")
                
                # simulate fetching payload etc
                # inputs = fetch_inputs(job_id)
                fake_inputs = [np.random.randn(3, 224, 224).astype(np.float32)]
                
                results = worker.predict(fake_inputs)
                
                logging.info(f"Job {job_id} completed: {results}")
                # Mark complete in Redis...
                
            else:
                time.sleep(0.1)
                
        except Exception as e:
            logging.error(f"Error in worker loop: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()

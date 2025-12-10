import time
import logging
import random
import uuid
from typing import Dict, Any, List
from prometheus_client import Counter, Histogram, Gauge

# Metrics
SIMULATION_SCENARIOS_TOTAL = Counter(
    'simulation_scenarios_total',
    'Total simulation scenarios run',
    ['scenario_type', 'status']
)
SIMULATION_DURATION = Histogram(
    'simulation_duration_seconds',
    'Duration of simulation execution',
    ['scenario_type']
)
SENSOR_DATA_BYTES = Counter(
    'sensor_data_processed_bytes',
    'Total bytes of synthetic sensor data processed'
)
SIMULATION_PASS_RATE = Gauge(
    'simulation_pass_rate',
    'Rolling pass rate of simulations'
)

class SimulationWorker:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("SimulationWorker")
        
    def generate_sensor_data(self, sensors: List[Dict[str, Any]], duration_sec: int) -> int:
        """Simulate data generation. Returns total bytes generated."""
        total_bytes = 0
        for sensor in sensors:
            sType = sensor.get('type')
            count = sensor.get('count', 1)
            
            # Rough estimation of data rate
            if sType == 'camera':
                # 1920x1080 * 3 bytes * 30fps
                bytes_per_sec = 1920 * 1080 * 3 * 30 * count
            elif sType == 'lidar':
                # 1M points * 16 bytes (x,y,z,reflectivity)
                bytes_per_sec = 1000000 * 16 * count
            else:
                bytes_per_sec = 1024 * 1024 # Default 1MB/s
                
            total_bytes += bytes_per_sec * duration_sec
            
        return total_bytes

    def run_inference_pipeline(self, data_bytes: int) -> Dict[str, float]:
        """Simulate processing pipeline (Inference + Planning + Control)"""
        # Simulate CPU/GPU load
        time.sleep(random.uniform(0.1, 0.5)) 
        
        # Simulate meaningful metrics
        return {
            "collision_rate": random.uniform(0, 0.05), # Low prob of collision
            "lane_deviation": random.uniform(0, 0.3),  # Meters
            "reaction_time": random.uniform(0.1, 0.4)  # Seconds
        }

    def evaluate(self, metrics: Dict[str, float], thresholds: Dict[str, float]) -> bool:
        """Compare metrics against thresholds"""
        passed = True
        for k, v in metrics.items():
            if k in thresholds:
                if v > thresholds[k]:
                    passed = False
                    break
        return passed

    def process_job(self, job_spec: Dict[str, Any]):
        scenario = job_spec.get('scenario', {})
        sensors = job_spec.get('sensors', [])
        eval_config = job_spec.get('evaluation', {})
        
        scen_type = scenario.get('type', 'unknown')
        duration_str = scenario.get('duration', '1s')
        try:
            duration = int(duration_str.replace('s', ''))
        except:
            duration = 10
            
        with SIMULATION_DURATION.labels(scenario_type=scen_type).time():
            self.logger.info(f"Starting simulation: {scen_type} for {duration}s")
            
            # 1. Generate Data
            data_bytes = self.generate_sensor_data(sensors, duration)
            SENSOR_DATA_BYTES.inc(data_bytes)
            
            # 2. Run Pipeline
            results = self.run_inference_pipeline(data_bytes)
            
            # 3. Evaluate results
            thresholds = eval_config.get('threshold', {})
            passed = self.evaluate(results, thresholds)
            
            status = "passed" if passed else "failed"
            SIMULATION_SCENARIOS_TOTAL.labels(scenario_type=scen_type, status=status).inc()
            
            self.logger.info(f"Simulation {status}. Metrics: {results}")
            
            return {
                "status": status,
                "metrics": results,
                "data_processed_mb": data_bytes / (1024*1024)
            }

if __name__ == "__main__":
    # Test run
    worker = SimulationWorker()
    spec = {
        "scenario": {"type": "driving", "duration": "5s"},
        "sensors": [{"type": "camera", "count": 1}],
        "evaluation": {"threshold": {"collision_rate": 0.01}}
    }
    worker.process_job(spec)

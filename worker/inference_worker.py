import torch
import torch.nn as nn
from typing import Dict, Any, List
import numpy as np
from prometheus_client import Counter, Histogram, Gauge
import time
import logging

# Prometheus metrics
INFERENCE_REQUESTS = Counter(
    'inference_requests_total', 
    'Total inference requests',
    ['model_name', 'status']
)
INFERENCE_LATENCY = Histogram(
    'inference_latency_seconds',
    'Inference latency in seconds',
    ['model_name'],
    buckets=[.01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5]
)
BATCH_SIZE = Histogram(
    'inference_batch_size',
    'Batch size for inference requests',
    ['model_name'],
    buckets=[1, 2, 4, 8, 16, 32, 64, 128, 256]
)
GPU_UTILIZATION = Gauge(
    'gpu_utilization_percent',
    'GPU utilization percentage',
    ['device_id']
)

class InferenceWorker:
    def __init__(
        self,
        model_path: str,
        device: str = "cuda",
        max_batch_size: int = 32,
        timeout_ms: int = 100
    ):
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.model = self._load_model(model_path)
        self.model.to(self.device)
        self.model.eval()
        self.max_batch_size = max_batch_size
        self.timeout_ms = timeout_ms
        self.model_name = model_path.split("/")[-1]
        
        logging.info(f"Loaded model {self.model_name} on {self.device}")
    
    def _load_model(self, model_path: str) -> nn.Module:
        """Load PyTorch model with JIT optimization if available"""
        try:
            # Try loading as TorchScript first
            model = torch.jit.load(model_path)
            logging.info("Loaded TorchScript model")
        except:
            # Fall back to regular PyTorch model
            try:
                model = torch.load(model_path)
                logging.info("Loaded PyTorch model")
            except Exception as e:
                logging.warning(f"Failed to load model from path, using dummy ResNet50 for demo: {e}")
                from torchvision.models import resnet50
                model = resnet50()
        return model
    
    @torch.inference_mode()
    def predict(self, inputs: List[np.ndarray]) -> List[Dict[str, Any]]:
        """Run batch inference with metrics collection"""
        start_time = time.perf_counter()
        
        try:
            # Convert inputs to tensor
            # Assuming inputs are already preprocessed numpy arrays of correct shape
            # For demo, if input is not valid, we generate random
            if inputs and inputs[0] is None:
                 batch = torch.randn(len(inputs), 3, 224, 224, device=self.device)
            else:
                batch = torch.tensor(
                    np.stack(inputs), 
                    dtype=torch.float32,
                    device=self.device
                )
            
            BATCH_SIZE.labels(model_name=self.model_name).observe(len(inputs))
            
            # Run inference
            with torch.cuda.amp.autocast(enabled=True):  # Mixed precision
                outputs = self.model(batch)
            
            # Process outputs
            if isinstance(outputs, torch.Tensor):
                results = outputs.cpu().numpy().tolist()
            else:
                results = [o.cpu().numpy().tolist() for o in outputs]
            
            # Record metrics
            latency = time.perf_counter() - start_time
            INFERENCE_LATENCY.labels(model_name=self.model_name).observe(latency)
            INFERENCE_REQUESTS.labels(
                model_name=self.model_name, 
                status="success"
            ).inc(len(inputs))
            
            # Update GPU utilization
            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    try:
                        util = torch.cuda.utilization(i)
                        GPU_UTILIZATION.labels(device_id=str(i)).set(util)
                    except:
                        pass
            
            return [{"prediction": r, "latency_ms": latency * 1000} for r in results]
            
        except Exception as e:
            INFERENCE_REQUESTS.labels(
                model_name=self.model_name, 
                status="error"
            ).inc(len(inputs))
            logging.error(f"Inference error: {e}")
            raise
    
    def warmup(self, sample_input: np.ndarray = None, iterations: int = 10):
        """Warmup model for consistent latency"""
        logging.info(f"Warming up model with {iterations} iterations...")
        if sample_input is None:
             sample_input = np.random.randn(3, 224, 224).astype(np.float32)
             
        for _ in range(iterations):
            self.predict([sample_input])
        logging.info("Warmup complete")

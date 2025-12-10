"""
Load test script for AI Job Orchestrator
Usage: python load_test.py --jobs 1000 --concurrency 50
"""
import asyncio
import aiohttp
import time
import statistics
import argparse
from dataclasses import dataclass

TOKEN = "fake-super-secret-token"
API_URL = "http://localhost:8000/api/v1/jobs/"

@dataclass
class BenchmarkResult:
    total_jobs: int
    successful: int
    failed: int
    duration: float
    throughput: float
    latencies: list

async def submit_job(session, url):
    start = time.perf_counter()
    json_data = {
        "job_type": "inference",
        "priority": 50,
        "image": "pytorch-inference:latest"
    }
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    try:
        async with session.post(url, json=json_data, headers=headers) as resp:
            latency = (time.perf_counter() - start) * 1000
            return resp.status == 200, latency
    except Exception:
        return False, 0

async def run_benchmark(num_jobs, concurrency):
    print(f"Starting benchmark: {num_jobs} jobs, {concurrency} concurrency")
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        latencies = []
        success = 0
        failed = 0
        
        start_time = time.perf_counter()
        
        # Batch creation for simplicity in this script
        # Real load test uses a semaphore or worker queue
        semaphore = asyncio.Semaphore(concurrency)
        
        async def bounded_submit():
            async with semaphore:
                ok, lat = await submit_job(session, API_URL)
                return ok, lat

        tasks = [bounded_submit() for _ in range(num_jobs)]
        results = await asyncio.gather(*tasks)
        
        total_time = time.perf_counter() - start_time
        
        for ok, lat in results:
            if ok:
                success += 1
                latencies.append(lat)
            else:
                failed += 1
                
        return BenchmarkResult(
            total_jobs=num_jobs,
            successful=success,
            failed=failed,
            duration=total_time,
            throughput=success / total_time if total_time > 0 else 0,
            latencies=latencies
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs", type=int, default=100)
    parser.add_argument("--concurrency", type=int, default=10)
    args = parser.parse_args()
    
    res = asyncio.run(run_benchmark(args.jobs, args.concurrency))
    
    print("\nBenchmark Results")
    print("=================")
    print(f"Total Jobs: {res.total_jobs}")
    print(f"Successful: {res.successful}")
    print(f"Failed:     {res.failed}")
    print(f"Duration:   {res.duration:.2f}s")
    print(f"Throughput: {res.throughput:.2f} jobs/sec")
    if res.latencies:
        print(f"P50 Latency: {statistics.median(res.latencies):.2f}ms")
        print(f"P95 Latency: {statistics.quantiles(res.latencies, n=20)[-1]:.2f}ms")
        print(f"P99 Latency: {statistics.quantiles(res.latencies, n=100)[-1]:.2f}ms")

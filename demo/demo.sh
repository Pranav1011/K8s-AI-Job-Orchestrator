#!/bin/bash
# demo.sh - Interactive demo of AI Job Orchestrator

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

TOKEN="fake-super-secret-token"
API_URL="http://localhost:8000"

echo -e "${BLUE}🚀 K8s AI Job Orchestrator Demo${NC}"
echo "================================"

# 1. Show CRDs
echo -e "\n${GREEN}📋 Step 1: Checking Custom Resource Definitions${NC}"
kubectl get crds | grep aiplatform

# 2. Submit jobs
echo -e "\n${GREEN}📤 Step 2: Submitting 10 High Priority AI Jobs${NC}"
for i in {1..10}; do
   echo "Submitting Job $i..."
   curl -s -X POST "${API_URL}/api/v1/jobs/" \
       -H "Authorization: Bearer ${TOKEN}" \
       -H "Content-Type: application/json" \
       -d '{
           "job_type": "inference",
           "priority": 80,
           "image": "pytorch-inference:latest"
       }' > /dev/null
done

# 3. Watch jobs
echo -e "\n${GREEN}👀 Step 3: Watching Job Progress (Ctrl+C to stop)${NC}"
echo "Waiting 5 seconds for controller to reconcile..."
sleep 5
kubectl get aijobs

# 4. Show metrics
echo -e "\n${GREEN}📊 Step 4: Queue Metrics${NC}"
# Use port-forward to controller if needed, or check API metrics
curl -s "${API_URL}/api/v1/queues/"

echo -e "\n${BLUE}✅ Demo Complete! Check Grafana at http://localhost:3000${NC}"

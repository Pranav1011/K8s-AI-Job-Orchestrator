package scheduler

import (
	"context"
	"sort"
	"time"

	"github.com/go-logr/logr"
	"sigs.k8s.io/controller-runtime/pkg/client"

	aiplatformv1alpha1 "github.com/yourorg/ai-job-scheduler/controller/pkg/apis/aiplatform/v1alpha1"
)

// Scheduler decides which pending jobs to run based on priority and availability.
type Scheduler struct {
	Client client.Client
	Log    logr.Logger
}

func NewScheduler(client client.Client, log logr.Logger) *Scheduler {
	return &Scheduler{
		Client: client,
		Log:    log,
	}
}

// Start runs the scheduling loop.
func (s *Scheduler) Start(ctx context.Context) error {
	ticker := time.NewTicker(10 * time.Second) // Scheduling interval
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return nil
		case <-ticker.C:
			s.ScheduleLoop(ctx)
		}
	}
}

func (s *Scheduler) ScheduleLoop(ctx context.Context) {
	s.Log.Info("Running scheduling loop")

	// 1. List all Pending Jobs
	var jobList aiplatformv1alpha1.AIJobList
	if err := s.Client.List(ctx, &jobList); err != nil {
		s.Log.Error(err, "Failed to list jobs")
		return
	}

	pendingJobs := []aiplatformv1alpha1.AIJob{}
	for _, job := range jobList.Items {
		if job.Status.Phase == "Pending" || job.Status.Phase == "" {
			pendingJobs = append(pendingJobs, job)
		}
	}

	if len(pendingJobs) == 0 {
		return
	}

	// 2. Sort Logic (Priority)
	sort.Sort(ByPriority(pendingJobs))

	// 3. Scheduling Loop with Gang & Preemption Support
	for _, job := range pendingJobs {
		// Gang Scheduling Check
		if job.Spec.Gang.Enabled {
			// In a real implementation, we would group jobs by a Gang ID or Label.
			// Here, assuming AIJob represents the *entire* gang (if MinMembers > 1, it implies sub-resources).
			// If we need to wait for X resources to be available:
			requiredResources := getResourceRequirements(&job)
			availableResources := s.getClusterCapacity(ctx) // Placeholder

			if !s.hasCapacity(availableResources, requiredResources, job.Spec.Gang.MinMembers) {
				s.Log.Info("Not enough capacity for gang", "job", job.Name, "minMembers", job.Spec.Gang.MinMembers)
				
				// Preemption Logic
				if job.Spec.Priority == "high" || job.Spec.Priority == "critical" {
					if preempted := s.tryPreemption(ctx, &job, requiredResources); preempted {
						// Retry scheduling in next loop or proceed if immediate capacity freed
						s.Log.Info("Preempted jobs for gang", "job", job.Name)
					}
				}
				continue
			}
		}

		if err := s.scheduleJob(ctx, &job); err != nil {
			s.Log.Error(err, "Failed to schedule job", "job", job.Name)
		}
	}
}

// Helpers for Demo Logic
func getResourceRequirements(job *aiplatformv1alpha1.AIJob) map[string]int64 {
	// Parse cpu/gpu strings to int
	return map[string]int64{"gpu": 1} // Simplified
}

func (s *Scheduler) getClusterCapacity(ctx context.Context) map[string]int64 {
	// Query ComputeClusters...
	return map[string]int64{"gpu": 100} // Mock
}

func (s *Scheduler) hasCapacity(available, required map[string]int64, multiplier int) bool {
	// Simple check for 'gpu'
	reqGPU := required["gpu"] * int64(multiplier)
	availGPU := available["gpu"]
	return availGPU >= reqGPU
}

func (s *Scheduler) tryPreemption(ctx context.Context, highPrioJob *aiplatformv1alpha1.AIJob, required map[string]int64) bool {
	// List running jobs
	// Filter for lower priority and Preemptible=true
	// Evict (Update Status -> Pending/Preempted)
	return false // Simplified
}

func (s *Scheduler) scheduleJob(ctx context.Context, job *aiplatformv1alpha1.AIJob) error {
	// "Scheduling" here means transitioning to "Queued" or "Running"
	// and potentially creating the Pod (delegated to Controller? or done here?)
	// Let's say we mark it as "Queued" which means "Accepted by Scheduler".
	// The Reconciler then sees "Queued" and creates the Pod.
	
	// Check if queue exists
	// Check quotas...
	
	job.Status.Phase = "Queued"
	// if using node assignment: job.Spec.NodeName = "selected-node"

	if err := s.Client.Status().Update(ctx, job); err != nil {
		return err
	}
	s.Log.Info("Scheduled job", "job", job.Name, "new_phase", "Queued")
	return nil
}

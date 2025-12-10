package scheduler

import (
	aiplatformv1alpha1 "github.com/yourorg/ai-job-scheduler/controller/pkg/apis/aiplatform/v1alpha1"
)

// ByPriority implements sort.Interface for []AIJob based on Priority
type ByPriority []aiplatformv1alpha1.AIJob

func (a ByPriority) Len() int      { return len(a) }
func (a ByPriority) Swap(i, j int) { a[i], a[j] = a[j], a[i] }
func (a ByPriority) Less(i, j int) bool {
	// Parse priority string (high > medium > low)
	p1 := getPriorityValue(a[i].Spec.Priority)
	p2 := getPriorityValue(a[j].Spec.Priority)
	
	if p1 != p2 {
		return p1 > p2 // Higher priority first
	}
	
	// Tie breaker: CreationTimestamp (FIFO)
	return a[i].CreationTimestamp.Before(&a[j].CreationTimestamp)
}

func getPriorityValue(p string) int {
	switch p {
	case "high", "critical":
		return 3
	case "medium":
		return 2
	case "low":
		return 1
	default:
		return 1 // Default to low
	}
}

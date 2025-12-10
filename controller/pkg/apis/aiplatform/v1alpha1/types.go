package v1alpha1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// AIJobSpec defines the desired state of AIJob
type AIJobSpec struct {
	JobType     string            `json:"jobType"`
	Priority    string            `json:"priority"`
	Preemptible bool              `json:"preemptible,omitempty"`
	Gang        GangSpec          `json:"gang,omitempty"`
	Image       string            `json:"image"`
	Resources   ResourceSpec      `json:"resources"`
	InputData   InputDataSpec     `json:"inputData"`
	OutputData  OutputDataSpec    `json:"outputData"`
	Model       ModelSpec         `json:"model"`
	Timeout     int               `json:"timeout"`
	Retries     int               `json:"retries"`
	Concurrency int               `json:"concurrency,omitempty"`
}

type GangSpec struct {
	Enabled    bool `json:"enabled"`
	MinMembers int  `json:"minMembers"`
}

type ResourceSpec struct {
	CPU    string `json:"cpu"`
	Memory string `json:"memory"`
	GPU    string `json:"gpu"`
}

type InputDataSpec struct {
	Source string `json:"source"`
	Format string `json:"format"`
}

type OutputDataSpec struct {
	Destination string `json:"destination"`
}

type ModelSpec struct {
	Path      string `json:"path"`
	Framework string `json:"framework"`
}

// AIJobStatus defines the observed state of AIJob
type AIJobStatus struct {
	Phase          string      `json:"phase,omitempty"`
	StartTime      *metav1.Time `json:"startTime,omitempty"`
	CompletionTime *metav1.Time `json:"completionTime,omitempty"`
	Metrics        JobMetrics  `json:"metrics,omitempty"`
}

type JobMetrics struct {
	LatencyP50 string `json:"latencyP50,omitempty"`
	LatencyP99 string `json:"latencyP99,omitempty"`
	Throughput string `json:"throughput,omitempty"`
}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status

// AIJob is the Schema for the aijobs API
type AIJob struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   AIJobSpec   `json:"spec,omitempty"`
	Status AIJobStatus `json:"status,omitempty"`
}

// +kubebuilder:object:root=true

// AIJobList contains a list of AIJob
type AIJobList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []AIJob `json:"items"`
}

// AIJobQueueSpec defines the desired state of AIJobQueue
type AIJobQueueSpec struct {
	MaxConcurrentJobs int               `json:"maxConcurrentJobs"`
	ConcurrencyLimits ConcurrencyLimits `json:"concurrencyLimits,omitempty"`
	PriorityClasses   []PriorityClass   `json:"priorityClasses"`
	ResourceQuota     ResourceQuotaSpec `json:"resourceQuota"`
	Scheduling        SchedulingSpec    `json:"scheduling"`
}

type ConcurrencyLimits struct {
	MaxConcurrentPerUser      int `json:"maxConcurrentPerUser"`
	MaxConcurrentPerNamespace int `json:"maxConcurrentPerNamespace"`
}

type PriorityClass struct {
	Name   string `json:"name"`
	Weight int    `json:"weight"`
}

type ResourceQuotaSpec struct {
	MaxGPUs   int    `json:"maxGPUs"`
	MaxCPUs   int    `json:"maxCPUs"`
	MaxMemory string `json:"maxMemory"`
}

type SchedulingSpec struct {
	Algorithm  string `json:"algorithm"`
	Preemption string `json:"preemption"`
}

// +kubebuilder:object:root=true

// AIJobQueue is the Schema for the aijobqueues API
type AIJobQueue struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec AIJobQueueSpec `json:"spec,omitempty"`
}

// +kubebuilder:object:root=true

// AIJobQueueList contains a list of AIJobQueue
type AIJobQueueList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []AIJobQueue `json:"items"`
}

// ComputeClusterSpec defines the desired state of ComputeCluster
type ComputeClusterSpec struct {
	NodeSelector    NodeSelectorSpec `json:"nodeSelector"`
	MinNodes        int              `json:"minNodes"`
	MaxNodes        int              `json:"maxNodes"`
	Autoscaling     AutoscalingSpec  `json:"autoscaling"`
}

type NodeSelectorSpec struct {
	Accelerator string `json:"accelerator"`
}

type AutoscalingSpec struct {
	Enabled            bool   `json:"enabled"`
	ScaleUpThreshold   int    `json:"scaleUpThreshold"`
	ScaleDownThreshold int    `json:"scaleDownThreshold"`
	CooldownPeriod     string `json:"cooldownPeriod"`
}

// +kubebuilder:object:root=true

// ComputeCluster is the Schema for the computeclusters API
type ComputeCluster struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec ComputeClusterSpec `json:"spec,omitempty"`
}

// +kubebuilder:object:root=true

// ComputeClusterList contains a list of ComputeCluster
type ComputeClusterList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []ComputeCluster `json:"items"`
}

func init() {
	SchemeBuilder.Register(&AIJob{}, &AIJobList{}, &AIJobQueue{}, &AIJobQueueList{}, &ComputeCluster{}, &ComputeClusterList{})
}

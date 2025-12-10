package controller

import (
	"context"
	"time"

	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"

	aiplatformv1alpha1 "github.com/yourorg/ai-job-scheduler/controller/pkg/apis/aiplatform/v1alpha1"
)

// AIJobReconciler reconciles a AIJob object
type AIJobReconciler struct {
	client.Client
	Scheme *runtime.Scheme
}

//+kubebuilder:rbac:groups=aiplatform.example.com,resources=aijobs,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=aiplatform.example.com,resources=aijobs/status,verbs=get;update;patch
//+kubebuilder:rbac:groups=aiplatform.example.com,resources=aijobs/finalizers,verbs=update

func (r *AIJobReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	_ = log.FromContext(ctx)

	// Fetch the AIJob instance
	job := &aiplatformv1alpha1.AIJob{}
	if err := r.Get(ctx, req.NamespacedName, job); err != nil {
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	// Basic Lifecycle Management
	// If Pending, we might want to mark it as Queued if not already.
	// Real scheduling happens via the Scheduler component (called here or separately).
	// For now, let's just observe the state.

	if job.Status.Phase == "" {
		job.Status.Phase = "Pending"
		if err := r.Status().Update(ctx, job); err != nil {
			return ctrl.Result{}, err
		}
		return ctrl.Result{}, nil
	}

	// Handle retries and failures (placeholder logic)
	if job.Status.Phase == "Failed" {
		// Exponential backoff logic would go here
		// Check RetryCount vs MaxRetries
		if job.Spec.Retries > 0 { // Simplistic check
			// Requeue logic
			return ctrl.Result{RequeueAfter: 10 * time.Second}, nil
		}
	}

	return ctrl.Result{}, nil
}

// SetupWithManager sets up the controller with the Manager.
func (r *AIJobReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&aiplatformv1alpha1.AIJob{}).
		Complete(r)
}

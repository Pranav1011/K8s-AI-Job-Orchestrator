package controller

import (
	"context"

	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"

	aiplatformv1alpha1 "github.com/yourorg/ai-job-scheduler/controller/pkg/apis/aiplatform/v1alpha1"
)

// AIJobQueueReconciler reconciles a AIJobQueue object
type AIJobQueueReconciler struct {
	client.Client
	Scheme *runtime.Scheme
}

//+kubebuilder:rbac:groups=aiplatform.example.com,resources=aijobqueues,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=aiplatform.example.com,resources=aijobqueues/status,verbs=get;update;patch
//+kubebuilder:rbac:groups=aiplatform.example.com,resources=aijobqueues/finalizers,verbs=update

func (r *AIJobQueueReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	_ = log.FromContext(ctx)

	// Fetch the Queue instance
	queue := &aiplatformv1alpha1.AIJobQueue{}
	if err := r.Get(ctx, req.NamespacedName, queue); err != nil {
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	// For now, the queue is a configuration object.
	// We could validate the resource quotas or priority classes here.
	// Or update status with current job counts (if we added fields for that).

	return ctrl.Result{}, nil
}

// SetupWithManager sets up the controller with the Manager.
func (r *AIJobQueueReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&aiplatformv1alpha1.AIJobQueue{}).
		Complete(r)
}

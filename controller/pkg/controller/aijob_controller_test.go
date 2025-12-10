package controller

import (
	"context"
	"testing"
	"time"

	aiplatformv1alpha1 "github.com/yourorg/ai-job-scheduler/controller/pkg/apis/aiplatform/v1alpha1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/types"
	"sigs.k8s.io/controller-runtime/pkg/client/fake"
	"sigs.k8s.io/controller-runtime/pkg/reconcile"
)

func TestAIJobReconciler_Reconcile(t *testing.T) {
	// Register operator types with the runtime scheme.
	scheme := runtime.NewScheme()
	_ = aiplatformv1alpha1.AddToScheme(scheme)

	// Create a fake client to mock API calls.
	// Create a pending job
	job := &aiplatformv1alpha1.AIJob{
		ObjectMeta: metav1.ObjectMeta{
			Name:      "test-job",
			Namespace: "default",
		},
		Spec: aiplatformv1alpha1.AIJobSpec{
			JobType: "inference",
			Image:   "test-image",
		},
	}

	// Objects to track in the fake client.
	objs := []runtime.Object{job}

	// Create a fake client with initialized objects.
	cl := fake.NewClientBuilder().WithScheme(scheme).WithRuntimeObjects(objs...).Build()

	// Create a Reconcile object with our fake client.
	r := &AIJobReconciler{Client: cl, Scheme: scheme}

	// Mock request to reconcile the job
	req := reconcile.Request{
		NamespacedName: types.NamespacedName{
			Name:      "test-job",
			Namespace: "default",
		},
	}

	// 1. Initial Reconcile: Should transition to "Pending" (if empty) or stay Pending
	// In our implementation, we set Phase to Pending if empty.
	// But our input object has empty phase.
	_, err := r.Reconcile(context.TODO(), req)
	if err != nil {
		t.Fatalf("reconcile: (%v)", err)
	}

	// Check the result
	updatedJob := &aiplatformv1alpha1.AIJob{}
	err = cl.Get(context.TODO(), req.NamespacedName, updatedJob)
	if err != nil {
		t.Fatalf("get job: (%v)", err)
	}

	if updatedJob.Status.Phase != "Pending" {
		t.Errorf("expected phase Pending, got %v", updatedJob.Status.Phase)
	}
}

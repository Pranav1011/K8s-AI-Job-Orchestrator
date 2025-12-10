package agent

import (
	"context"
	"fmt"
)

// Agent defines the interface for an AI agent
type Agent interface {
	Name() string
	Execute(ctx context.Context, inputs map[string]string) (map[string]string, error)
}

// Registry holds available agents
var Registry = map[string]Agent{
	"code-analyzer": &CodeAnalyzerAgent{},
	"code-generator": &CodeGeneratorAgent{},
}

// CodeAnalyzerAgent implementation
type CodeAnalyzerAgent struct{}

func (a *CodeAnalyzerAgent) Name() string { return "code-analyzer" }
func (a *CodeAnalyzerAgent) Execute(ctx context.Context, inputs map[string]string) (map[string]string, error) {
	// Logic to call LLM (OpenAI/Gemini) could go here
	fmt.Printf("Analyzing issue: %s\n", inputs["issue_url"])
	return map[string]string{"analysis_result": "Issue found in login logic"}, nil
}

// CodeGeneratorAgent implementation
type CodeGeneratorAgent struct{}

func (a *CodeGeneratorAgent) Name() string { return "code-generator" }
func (a *CodeGeneratorAgent) Execute(ctx context.Context, inputs map[string]string) (map[string]string, error) {
	fmt.Printf("Generating fix based on: %s\n", inputs["analysis"])
	return map[string]string{
		"suggested_fix": "func login() { ... }",
		"confidence_score": "0.95",
	}, nil
}

# Contributing to K8s AI Job Orchestrator

Thank you for your interest in contributing! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- Go 1.21+
- Python 3.11+
- Docker 24+
- Kind or Minikube
- kubectl 1.25+
- Helm 3.0+

### Setting Up Your Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/K8s-AI-Job-Orchestrator.git
cd K8s-AI-Job-Orchestrator

# Add upstream remote
git remote add upstream https://github.com/Pranav1011/K8s-AI-Job-Orchestrator.git

# Setup local development environment
make dev-setup

# Verify everything works
make test
```

See the [Development Guide](docs/development.md) for detailed setup instructions.

## Development Workflow

### 1. Create a Branch

```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
# or for bug fixes
git checkout -b fix/issue-description
```

### 2. Make Changes

- Write clean, readable code
- Follow the code standards below
- Add tests for new functionality
- Update documentation as needed

### 3. Commit Changes

We use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Format: <type>(<scope>): <description>

# Examples:
git commit -m "feat(scheduler): add priority preemption support"
git commit -m "fix(api): handle timeout errors gracefully"
git commit -m "docs(readme): update installation instructions"
git commit -m "test(controller): add gang scheduling tests"
git commit -m "refactor(worker): simplify job execution logic"
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `ci`: CI/CD changes
- `chore`: Maintenance tasks

### 4. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then open a Pull Request on GitHub.

## Code Standards

### Go (Controller)

```bash
# Format code
go fmt ./...

# Run linter
golangci-lint run

# Run tests
go test ./... -v
```

**Guidelines:**
- Follow [Effective Go](https://golang.org/doc/effective_go)
- Use meaningful variable and function names
- Add comments for exported functions
- Handle errors explicitly
- Use context for cancellation

### Python (Job Service & Workers)

```bash
# Format code
black app/ tests/
isort app/ tests/

# Type checking
mypy app/

# Run tests
pytest tests/ -v
```

**Guidelines:**
- Use type hints for all functions
- Follow [PEP 8](https://pep8.org/)
- Write docstrings for public functions
- Use async/await for I/O operations
- Handle exceptions appropriately

### Documentation

- Use Markdown for all documentation
- Keep language clear and concise
- Include code examples where helpful
- Update relevant docs when changing behavior

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run specific test suites
make test-go      # Go tests only
make test-python  # Python tests only

# Run with coverage
make test-coverage
```

### Writing Tests

- Write unit tests for new functions
- Add integration tests for API endpoints
- Test error cases, not just happy paths
- Mock external dependencies

### Test Structure

```
controller/
  pkg/
    scheduler/
      scheduler.go
      scheduler_test.go    # Tests alongside source

job-service/
  app/
  tests/
    test_jobs.py          # Tests in separate directory
    conftest.py           # Shared fixtures
```

## Submitting Changes

### Pull Request Guidelines

1. **Title**: Use conventional commit format
2. **Description**: Explain what and why
3. **Link Issues**: Reference related issues
4. **Small PRs**: Keep changes focused
5. **Tests**: Include tests for changes
6. **Documentation**: Update if needed

### Review Process

1. Automated checks must pass (CI, linting, tests)
2. At least one maintainer review required
3. Address review feedback
4. Squash commits if requested
5. Maintainer merges when approved

### After Merge

```bash
# Clean up local branch
git checkout main
git pull upstream main
git branch -d feature/your-feature-name
```

## Release Process

Releases are managed by maintainers following [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

## Getting Help

- Open an [issue](https://github.com/Pranav1011/K8s-AI-Job-Orchestrator/issues) for bugs or features
- Check existing issues before creating new ones
- Join discussions in issue comments

## Recognition

Contributors are recognized in release notes and the project README. Thank you for helping improve this project!

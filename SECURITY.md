# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x.x   | Yes       |
| 0.x.x   | Limited (critical fixes only) |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly.

### How to Report

**For sensitive security issues**, please report via:

1. **GitHub Security Advisories**: [Create a private security advisory](https://github.com/Pranav1011/K8s-AI-Job-Orchestrator/security/advisories/new)
2. **Email**: Create an issue marked `[SECURITY]` requesting private contact

**Please do NOT:**
- Open a public GitHub issue for security vulnerabilities
- Disclose the vulnerability publicly before it's addressed

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Resolution Target**: Depends on severity
  - Critical: 7 days
  - High: 14 days
  - Medium: 30 days
  - Low: 60 days

## Security Best Practices

When deploying this project, follow these recommendations:

### Authentication & Authorization

- Use strong JWT secrets (minimum 256 bits)
- Enable Kubernetes RBAC with least privilege
- Rotate credentials regularly
- Use network policies to restrict access

### Infrastructure

- Keep Kubernetes and dependencies updated
- Use TLS for all external communication
- Store secrets in a secret manager (Vault, AWS Secrets Manager)
- Enable audit logging

### Container Security

- Run containers as non-root
- Use read-only file systems where possible
- Scan images for vulnerabilities
- Use specific image tags, not `latest`

## Known Security Considerations

| Area | Consideration | Mitigation |
|------|---------------|------------|
| API Authentication | JWT tokens in headers | Use short-lived tokens, HTTPS only |
| Redis | Default no authentication | Enable Redis AUTH, use TLS |
| PostgreSQL | Database credentials | Use secrets, encrypted connections |
| Controller | Cluster-wide permissions | Namespace-scoped RBAC where possible |

## Security Updates

Security updates are released as patch versions and announced via:

- GitHub Releases
- Security Advisories
- CHANGELOG.md

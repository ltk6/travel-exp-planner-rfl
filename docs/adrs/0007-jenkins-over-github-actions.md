# ADR-0007: Self-Hosted Jenkins over GitHub Actions

- **Status:** Proposed
- **Phase:** 2
- **Date:** 2026-08-27

---

## Context

Phase 2 requires a local CI/CD pipeline that lints, tests, builds, scans, and deploys the stack
automatically on every merge to `main`. The two primary options evaluated were:

1. **GitHub Actions** — cloud-hosted CI managed by GitHub. Pipelines are defined as YAML workflows
   under `.github/workflows/` and execute on GitHub's remote runners.
2. **Self-hosted Jenkins** — an open-source CI controller provisioned locally, running inside the
   Phase 2 Vagrant VM alongside the Docker Compose stack.

The overarching project constraint is **local-first, zero-cost infrastructure**: all compute,
databases, CI/CD, and monitoring must run on developer hardware. The executive summary explicitly
targets `$0` monthly infrastructure spend across all phases.

---

## Decision

Use **self-hosted Jenkins** running inside the Vagrant VM as the sole CI/CD controller.
All pipeline stages are defined in a `Jenkinsfile` at the repo root. No GitHub-managed runners
are used at any point in the pipeline.

---

## Consequences

**Positive:**
- Fully consistent with the local-first constraint — CI executes on developer hardware with no
  external service dependency (GitHub uptime, runner availability, or free-tier minute quotas).
- Provisioning Jenkins inside the `Vagrantfile` is a genuine **Platform/SRE deliverable** —
  it demonstrates the ability to operate CI infrastructure, not just configure a SaaS product.
- The "self-hosted CI/CD" claim in the DevOps track proof artifact is substantiated by an actual
  Jenkins controller, not a cloud YAML configuration.
- Avoids accidental secrets leakage through GitHub Actions environment variables in a public or
  semi-public repository context.

**Negative:**
- Jenkins requires explicit provisioning and maintenance (JDK, plugins, agent configuration) as
  part of the `Vagrantfile` setup. This adds provisioning complexity compared to committing
  `.github/workflows/` YAML files.
- The Jenkins UI and plugin ecosystem are more operationally heavy than GitHub Actions; plugin
  version mismatches can cause pipeline failures.
- No native GitHub PR status checks unless the GitHub API is configured separately (e.g., via
  the GitHub Branch Source plugin). PRs may need manual verification steps during initial setup.
- Rebuilding the Vagrant VM (ephemeral infrastructure reconstruction) must also re-provision
  Jenkins and restore its job configuration; this must be automated in the provisioning scripts
  to meet the reproducibility requirement.

# Travel Experience Planner — Capstone Roadmap
### Triple-Track Internship Preparation — 10-Month Plan (Zero-Cost: Local-First + On-Demand OCI)

---

## Executive Summary

**Architecture — Current State.** Monolith with hub-and-spoke logic. **N18** (FastAPI orchestrator) calls modules **N1–N17** in-process. The **N3** database module connects to a remote managed Supabase PostgreSQL instance. A shared `contracts.py` (Pydantic V2) enforces interface boundaries. **N16** (Next.js frontend) is deployed separately.

**Zero-Cost Infrastructure.** 100% of backend services, databases (migrating N3 off Supabase), Kubernetes clusters, and monitoring run locally on developer hardware using Terraform, `kind` (Kubernetes in Docker), and Vagrant. N18 is exposed to Vercel (N16) via a Cloudflare Tunnel. An on-demand OCI Always Free ARM64 environment ($0 tier) is spun up via Terraform solely for metrics collection and validation, then immediately destroyed.

**Cloud Portability.** Terraform configurations and Kubernetes manifests are environment-neutral. Swapping from local `kind` to OCI ARM64 requires only a variable-file parameter change (`terraform apply -var-file="environments/oci.tfvars"`), with zero alterations to code or manifests.

**Application Code Freeze.** Core application code freezes after Phase 0. Subsequent phases focus on platform infrastructure (containerization, orchestration, resilience, metrics). A CD sprint runs on top of this hardened system once the infrastructure is stable.

**Linux Knowledge.** Hands-on Linux administration, networking, and kernel metrics are acquired just-in-time as required by each phase's tasks.

**Track Focuses:**

| Track | Target Role | Core Proof Artifact |
|---|---|---|
| **Network Engineer** | Network Ops / Cloud Networking | Local network segmentation using Kubernetes `NetworkPolicies`, traffic routing, and Cloudflare Tunnel ingress. |
| **Software Engineer** | Backend / Full-Stack | Hub-and-spoke topology, contract-tested interfaces, and a custom circuit breaker finite-state machine (FSM). |
| **Cloud / DevOps** | Platform / SRE / DevOps | Terraform-managed local Kubernetes cluster, cloud-portable IaC, self-hosted CI/CD, and local Prometheus/Grafana monitoring. |

**Core Spine:** Containerize the stack → extract N1 to a local microservice → expose N18 via Cloudflare Tunnel → load-test N5 Groq API rate limits to force uvicorn thread exhaustion → build a circuit breaker → validate the fix via before/after Locust metrics.

**Scope Tiers.** Kubernetes uses `kind` locally. OCI is on-demand only. Prometheus/Grafana runs locally. High-priority items are must-ship; low-priority tools degrade gracefully to simpler implementations if time is tight.

---

## Scope & Artifact Map

| Artifact | Tracks | Tier / Fallback |
|---|---|---|
| Shared Pydantic V2 contracts (`contracts.py`, module ↔ N18) | SWE | Must-ship |
| Automated contract tests wired into local CI | SWE, Platform | Must-ship |
| Multi-stage Dockerfiles + healthchecks | SWE, Platform | Must-ship |
| Local CI/CD pipeline with live deploy (via Cloudflare Tunnel) | SWE, Platform | Must-ship |
| Locust load tests + structured logs | SWE, Platform | Must-ship |
| Circuit breaker FSM + unit tests + integration tests | SWE, Platform | Must-ship |
| Before/after comparison metrics (failure vs fallback) | SWE, Platform | Must-ship |
| Scaffolding CLI + DX metrics | SWE, Platform | Must-ship |
| Multi-arch images (`linux/amd64` + `linux/arm64`) for N18 and N1 | SWE, Platform | Must-ship |
| OCI on-demand pipeline (Terraform + Helm, Phase 5) | Platform | Must-ship |
| Decision records (ADRs) | Network, SWE, Platform | Must-ship |
| Resumes per track | Network, SWE, Platform | Must-ship |
| Local Kubernetes (`kind`) cluster + NetworkPolicies | Network, Platform | Degrade-gracefully -> written configs only |
| HPA autoscaling | Platform | Degrade-gracefully -> basic scaling config |
| Prometheus/Grafana dashboard | Platform | Degrade-gracefully -> dashboard optional; runbook must-ship |
| Governance-as-code admission checks in CI | Platform | Degrade-gracefully -> manual checklist |
| Platform documentation | Platform | Degrade-gracefully -> `PLATFORM.md` only |
| Container image scanning (`trivy`) in CI | SWE, Platform | Degrade-gracefully -> manual scan reports |
| Demo video | Network, SWE, Platform | Degrade-gracefully -> minimal cut |

---

## Timeline at a Glance

| Period | Phase | Focus |
|---|---|---|
| August | 0 | Baseline benchmarks, architecture audit |
| September | 1 | Docker, N1 microservice extraction, local database |
| Oct–Nov | 2 | Local CI/CD, Vagrant environment, Cloudflare Tunnel |
| December | 3 | Load testing & chaos validation (Compose only) |
| January | — | Exam buffer (no project work) |
| Feb–Mar | 4 | Terraform-managed local `kind` cluster, NetworkPolicies |
| April | 5 | Prometheus/Grafana observability, on-demand OCI pipeline |
| May | 6 | Circuit breaker implementation & N5 async refactor |
| June, weeks 1–2 | 7 | Developer experience: scaffolding CLI, compliance checks |
| June, weeks 3–4 | 8 | Resumes, documentation freeze, demo video |

---

## Phase 0 — Baseline (August)

**Goals**
- Measure baseline latency, throughput, and system behavior under light load.
- Document current state (monolith, managed Supabase DB, in-process execution) and record primary bottlenecks.

**Tasks**
- **Architecture Audit**: Document module boundaries, in-process execution contracts, and current Supabase PostgreSQL schema.
- **Latency Baseline**: Benchmark N5/N18 endpoints; record p50/p95 response times.
- **Hypothesis Definition**: Document Groq API synchronous execution vulnerabilities as a point of failure to be tested in Phase 3.
- **Highlights Log**: Initialize `docs/highlights.md` to track metrics and decisions across phases.

**Docs**
- System description and problem statement in top-level `README.md`.
- `docs/architecture-as-is.md` detailing current state.

**Deliverables**
- `benchmarks/results/2026-08-baseline.json`
- `docs/architecture-as-is.md`

---

## Phase 1 — Containerization & Local Stack (September)

**Goals**
- Replace host-bound `run.bat` with a containerized local stack.
- Extract N1 (embeddings) into an independent service; maintain existing interface contract.

**Tasks**
- **Extract N1 Service**: Move embedding generation logic to a standalone containerized FastAPI service. Keep it inside the local Docker network.
- **Write Dockerfiles**: Implement multi-stage builds (`Dockerfile.n18`, `Dockerfile.n1`, `Dockerfile.n16`). Target `linux/amd64` and `linux/arm64`.
- **Compose Orchestration**: Write `docker-compose.yml` linking N1, N18, Next.js, and a local PostgreSQL+`pgvector` container on a shared bridge network. Migrate off Supabase.
- **Service Configuration**: Inject database credentials and API endpoints via environment variables.
- **Secrets Baseline**: Commit `.env.example` with required keys; exclude actual secrets via `.gitignore`.
- **Backup Script**: Write `scripts/pg_dump_cron.sh` to back up the local database volume.
- **Architecture Mapping**: Diagram container network paths.

**Docs**
- ADR: Standalone service boundary choice.
- ADR: REST vs gRPC for internal service communication.
- ADR: Docker Compose vs Kubernetes for local development.
- ADR: Secrets management pipeline.
- `docs/N1-embed-api.md` (service contract).

**Deliverables**
- Functional local Compose stack with active healthchecks.
- Container network diagram.

---

## Phase 2 — Local CI/CD & Public Ingress (Oct–Nov)

**Goals**
- Implement automated linting, testing, and vulnerability checks in local CI.
- Expose the local orchestrator securely to the public Next.js UI on Vercel.

**Tasks**
- **Trunk-Based Workflow**: Merge to `main` via short-lived feature branches and PRs gated by CI.
- **Linting & Formatting**: Enforce formatting gates (`ruff`, `eslint`, `prettier`) in CI.
- **Vulnerability Scans**: Add container vulnerability scanning (`trivy`) to the build pipeline.
- **Vagrant Environment**: Run the docker-compose stack inside a headless Vagrant VM (`vagrant up`). Run `kind` directly on host in Phase 4.
- **Cloudflare Ingress**: Set up a Cloudflare Tunnel daemon on the Vagrant VM to expose N18's API.
- **Frontend Integration**: Connect the Next.js UI on Vercel to N18 through the tunnel.
- **Build Caching**: Configure BuildKit layer caching for Docker builds in CI.
- **Multi-Arch Builds**: Build both `linux/amd64` and `linux/arm64` image tags for cloud deployment.
- **Tests**: Wire contract and integration smoke tests into CI.

**Docs**
- `docs/deployment-runbook.md` (Vagrant provisioning, tunnel configuration, token rotation).

**Deliverables**
- Local CI runner configuration files (`.github/workflows/`).
- `Vagrantfile` with automated provisioning scripts.
- Version-controlled `cloudflared` config.
- Integration tests in `tests/smoke/`.

---

## Ephemeral Infrastructure Reconstruction Runbook

- Track and log the time required to tear down and rebuild environments (`vagrant destroy && vagrant up`, `kind delete cluster && terraform apply`).
- Log issues and timings in `docs/ephemeral-infra-log.md` at the start of each phase to verify configuration reproducibility.

---

## Phase 3 — Chaos Engineering & Failure Testing (December)

**Goals**
- Validate uvicorn worker thread blocking under rate-limited upstream calls.
- Document system behavior under database drops, latency injection, and container failure.

**Tasks**
- **Load Script**: Write `loadtests/locustfile.py` with representative traffic ratios.
- **Load Test**: RAMP Locust users against the Compose stack to force Groq API thread exhaustion.
- **Chaos Scenarios**: Terminate the database container during active requests, inject latency into internal API calls, and kill uvicorn workers.
- **Backup Verification**: Validate database recovery by restoring data from a cron-generated backup.
- **Postmortem**: Document recovery times, system failures, and metric drops in a blameless postmortem.

**Docs**
- `docs/incident-2026-12-n5-429-storm.md` (postmortem).
- `docs/local-infrastructure-disruption-runbook.md` (chaos steps & recovery procedures).

**Deliverables**
- `loadtests/locustfile.py`.
- Recorded benchmarks of failure modes and restore runs.

---

## January — Exam Buffer

No active development.

---

## Phase 4 — Local, Cloud-Portable Kubernetes Deployment (Feb–Mar)

**Goals**
- Deploy the orchestrator, database, and embedding service onto local Kubernetes.
- Enforce network boundary isolation and verify cloud-portable infrastructure manifests.

**Tasks**
- **IaC Structure**: Create modular Terraform configs (`infra/modules/`) with environment parameterization (`local.tfvars` vs `oci.tfvars`).
- **Local Cluster**: Spin up a local cluster via `kind` on the host OS.
- **K8s Manifests**: Write Deployments, Services, ConfigMaps, and HPA targets for N18 and N1.
- **Probes**: Configure liveness and readiness endpoints.
- **Secrets**: Move configuration parameters and credentials to K8s Secrets.
- **Image Sourcing**: Load local image builds directly into `kind` nodes to bypass remote registry pulls.
- **Autoscaling**: Configure autoscaling via KEDA using request queue metrics.
- **Network Isolation**: Enforce network boundaries between components using `NetworkPolicies`.
- **Validation**: Re-run Locust tests on `kind` to verify that increasing compute replicas does not bypass external API limits.
- **Rollback Verification**: Test manual deployment rollbacks via `kubectl rollout undo`.

**Docs**
- ADR: `kind` vs managed cloud cluster selection.
- ADR: Metrics source selection for HPA/autoscaling.
- ADR: Terraform configuration boundaries for portability.
- Network flow diagram showing namespaces and pod boundaries.

**Deliverables**
- Terraform configurations and Kubernetes manifests (`k8s/`, `infra/`).
- HPA and rollback validation reports.

---

## Phase 5 — Observability & Ephemeral Infrastructure Governance (April)

**Goals**
- Implement metrics scraping and visual dashboards for the local cluster.
- Provision and tear down the target OCI ARM64 cluster using the portable IaC modules.

**Tasks**
- **Reconstruction Logging**: Log local cluster teardown and redeployment loops.
- **Logging**: Configure structured stdout JSON logging in N18.
- **Metrics Stack**: Deploy Prometheus and Grafana onto `kind` via Terraform Helm charts.
- **Dashboard**: Create a Grafana dashboard monitoring cluster latency, HTTP error codes, and pod scaling.
- **OCI Deployment**: Run `terraform apply -var-file=environments/oci.tfvars` to spin up OCI ARM64 resources, run the Helm monitoring stack, and verify multi-arch images.
- **Tear Down**: Destroy OCI resources immediately after verifying metrics capture.

**Docs**
- `docs/runbooks/embedding-service-down.md`.
- `docs/runbooks/high-429-rate.md`.
- `docs/ephemeral-infra-log.md` updates.

**Deliverables**
- Prometheus/Grafana manifests, dashboard configurations, and live OCI run screenshots.

---

## Phase 6 — Resilience: Circuit Breaker Refactor (May)

**Goals**
- Mitigate uvicorn worker blocking under rate-limited upstream calls.

**Tasks**
- **Circuit Breaker**: Implement a state-based circuit breaker wrapping N5 Groq calls with backup fallbacks.
- **Unit Tests**: Add tests verifying state transitions (Closed, Open, Half-Open).
- **Concurrency Tests**: Write integration tests demonstrating resilience under concurrent upstream failures.
- **Locust Verification**: Re-run Phase 3 Locust load tests against local and OCI targets; verify `/health` remains responsive during Groq API rate limits.
- **Metrics Comparison**: Chart response times and error rates (Phase 3 baseline vs. Phase 6 resolved).

**Docs**
- ADR: Circuit breaker FSM design and logic.
- Update runbooks to include manual circuit breaker reset states.

**Deliverables**
- FSM logic, unit/concurrency tests, and before/after latency comparison charts.

---

## Phase 7 — Developer Experience: Scaffolding CLI & Compliance (Jun 1–2)

**Goals**
- Provide automated template generation and static configuration analysis for new modules.

**Tasks**
- **Manual Timing Baseline**: Measure the manual developer time required to configure and deploy a new in-process spoke.
- **CLI Tool**: Implement a CLI tool (`travel-cli`) to scaffold new modules matching template specifications (code structure, tests, manifests).
- **Admission Checks**: Add a CI step verifying that new modules expose `/health` endpoints and matching schemas.
- **CLI Validation**: Measure CLI-assisted deployment times; compare metrics against the manual baseline.
- **Platform Index**: Compile `PLATFORM.md` detailing system endpoints and development workflows.

**Docs**
- ADR: Scaffolding CLI vs Developer Portal selection.
- `docs/golden-path-metrics.md` (manual vs CLI times).

**Deliverables**
- CLI tool repository, CI compliance checks, and `PLATFORM.md`.

---

## Phase 8 — Resumes, Documentation, and Demo Video (Jun 3–4)

**Goals**
- Freeze documentation, finalize resumes, and export verification media.

**Tasks**
- **Test Coverage**: Run coverage reports targeting ≥70% core backend coverage.
- **API Spec**: Export raw OpenAPI schema files.
- **Architecture File**: Compile `ARCHITECTURE.md` showing system flows, ADR lists, and portability constraints.
- **Resume Preparation**: Build track-specific resumes mapping highlights from `docs/highlights.md` to target DevOps, software, and networking keywords.
- **Recording**: Record a video walkthrough demonstrating cluster deployment, chaos engineering injection, circuit breaker recovery, and golden-path CLI onboarding.
- **Tear Down**: Verify all target cloud environments are destroyed.

**Docs**
- `demo/script.md` (narration guide).

**Deliverables**
- `ARCHITECTURE.md`, `docs/openapi.json`, final resumes, and demo video link.

---

## Risk Register

| Risk | Mitigation |
|---|---|
| Phase 3 schedule slips into January | Phase 3 tasks are kept small to accommodate scheduling overrides. |
| Learning curve for Terraform/Kubernetes delays Phase 4 | Phase 4 is allocated two months to account for initial setup learning. |
| Local infrastructure strains developer machine resources | Limit pod replica parameters and clean local node caches after runs. |
| Cloudflare Tunnel drops mid-demo | Maintain a direct port-forwarding fallback path for local endpoints. |
| OCI deployment fails to run cleanly | Confirm variable targets beforehand; fall back to dry-run plans if limits block provision. |
| HPA does not scale under real traffic load | Set low scaling thresholds and use custom request triggers. |
| OCI free-tier resources become unavailable | Rely on the local `kind` environment for core verification. |
| CLI design suffers from scope creep | Restrict targets to simple code generators; defer portal integrations. |
| Metrics timing is skewed by familiarity | Keep code configurations simple and document limitations. |
| Phase 8 block runs tight | Maintain a 2-day contingency buffer in July. |
| External learning requirements delay milestones | Drop optional integrations to preserve must-ship deliverables. |
| Metrics differ across resumes | Enforce `docs/highlights.md` as the single source of truth. |

---

## KPI Dashboard

| Metric | Baseline (Aug) | Target (Jun) |
|---|---|---|
| p95 latency under load (local cluster) | From Phase 0 benchmark | ≥30% improvement |
| 429 error rate under storm load | ~100% at peak (Phase 3) | <5% |
| Contract-covered boundaries | Existing | 100% enforced in CI |
| Decision records written | 0 | 9+ |
| Test coverage (core modules) | Unmeasured | ≥70% |
| Ephemeral infrastructure reconstructions logged | 0 | One per phase from Phase 2 onward |
| Cloud-portability retarget proof (OCI) | N/A | Live `oci.tfvars` apply validated (Phase 5) |
| OCI cluster spin-up time | N/A | ≤ 5 minutes |
| Time-to-first-green-CI-run | N/A | Quantified reduction vs manual |
| Monthly infrastructure spend | $0 | $0 |

---

## Optional Add-Ons

Only attempt once core deliverables are complete:
- OpenTelemetry distributed tracing across the N18↔N1 boundary.
- Provision a second OCI region for failover testing using the same Terraform modules.
- Add a second golden-path template to the CLI.

---

## Year 4 Preview

- Distributed tracing and service mesh (Istio/Linkerd).
- GitOps (ArgoCD/Flux) pipeline automation.
- Managed cloud K8s cluster (EKS/GKE) with real VPC infrastructure.
- Spot instances and cost-optimized autoscaling (Karpenter).
- IAM least-privilege policies.
- Internal developer portal (Backstage).
# Travel Experience Planner — Capstone Roadmap
### Triple-Track Internship Preparation — 10-Month Plan (Zero-Cost: Local-First + On-Demand OCI)

---

## Executive Summary

**Architecture — Current State.** The system runs a hub-and-spoke design: **N18** is the core FastAPI orchestrator. Modules **N1–N17** (including N1 for BGE-M3 vector embeddings) execute in-process inside N18, each exposing functions N18 calls directly. The **N3** database module currently connects to a managed **Supabase** PostgreSQL instance. A shared `contracts.py` — a Pydantic V2 contract file imported by both the module and N18 — locks both sides to a single schema. **N16** is the Next.js frontend, deployed independently of the backend.

**Zero-Cost Infrastructure Guarantee — Target State.** The goal of this roadmap is to ensure 100% of backend systems, databases (migrating N3 off Supabase), Kubernetes clusters, and observability tooling **run locally on commodity developer hardware**. **Provision every environment** — cluster, network, database, monitoring stack — through Terraform, `kind` (Kubernetes in Docker), and Vagrant (`vagrant up`). Once fully implemented, no paid cloud service, managed database, or hosted compute tier will appear anywhere in this architecture. **Expose exactly one component** externally: the local core orchestrator (N18), tunneled to the public Vercel frontend (N16) via an encrypted Cloudflare Tunnel for live evaluation. Every other service — N1 embeddings, Postgres/pgvector, the `kind` cluster, Prometheus/Grafana — stays sealed inside the local network boundary. The one targeted exception is the **OCI Always Free ARM64 environment** (4 OCPU / 24 GB RAM, $0 via the Always Free tier): activated exclusively through Operational Tasks — metrics capture, demo recordings, and live interview hosting — and immediately torn down via `terraform destroy` after each session.

**Cloud Portability Guarantee.** **Modularize every Terraform configuration and Kubernetes manifest** to enforce complete environment neutrality. **Prove retargetability** from the local `kind` environment to the **OCI Always Free ARM64 cluster** through a single variable-file swap — `terraform apply -var-file="environments/oci.tfvars"` — with zero changes to application code and zero changes to Kubernetes manifests. Environment identity lives entirely in `.tfvars`, never in code.

**Application Code Freeze after Phase 0.** Core application code (N1–N18 module logic, shared ontologies, pipeline algorithms) is frozen at the end of Phase 0. From Phase 1 onward, the only permitted application-layer changes are wiring adjustments required by containerization or orchestration (environment variable injection, healthcheck endpoints, graceful shutdown handlers). This deliberate freeze separates the application tier from the platform/infrastructure tier — it turns the repository from a "working on app features" project into a true platform engineering exercise where you build automated delivery, containerization, orchestration, and reliability around a stable, known-good system. Every phase after Phase 0 is measured by what it adds to the platform, not to the product.

**Linux Knowledge — Just-In-Time, Not Front-Loaded.** Linux underpins Docker, Vagrant, Kubernetes, and OCI. Rather than studying it generically upfront, this roadmap acquires Linux skills in three tiers, each learned at the moment the phase demands it. Prerequisites are called out within Phases 1, 2, and 4.

**Three internship tracks, one system:**

| Track | Target Role | Core Proof Artifact |
|---|---|---|
| **Network Engineer** | Network Ops / Cloud Networking | Local network segmentation using Kubernetes `NetworkPolicies` as a zero-cost VPC/Security-Group analog, plus traffic flow diagrams and the Cloudflare Tunnel ingress model. |
| **Software Engineer** | Backend / Full-Stack | Hub-and-spoke architecture, contract-tested boundaries, and a custom circuit breaker finite-state machine (FSM). |
| **Cloud / DevOps** | Platform / SRE / DevOps | Terraform-provisioned local Kubernetes cluster, cloud-portable IaC, self-hosted CI/CD, and self-hosted observability — all fully reproducible on a laptop. |

**Spine of the project:** **Containerize the full stack** → **extract N1** into an independently deployable local microservice → **expose N18 live** through Cloudflare Tunnel → **hypothesize and confirm** that N5 (activity generation) fails under load with `429` errors from a single-provider LLM API → **build a circuit breaker** to fix it → **validate the fix** with quantified before/after metrics from local load tests and a live confirmation run. This thread runs through every phase and anchors all three resumes plus the final demo video.

**Scope note.** Kubernetes remains the strongest Cloud/DevOps signal in the project, provisioned as a Terraform-managed local `kind` cluster for all day-to-day work. The OCI Always Free ARM64 cluster is the concrete on-demand cloud target: activated via Operational Tasks only, never always-on. Distributed tracing (OpenTelemetry) is deferred: high time cost, low interview ROI at internship level. Self-hosted Prometheus/Grafana covers day-to-day observability locally and is validated live on OCI during Phase 5.

**Internal scope tiers.** The plan runs alongside a school curriculum plus self-directed learning of new tooling. The core plan splits into a **must-ship tier** and a **degrade-gracefully tier**, so a slip in any phase resolves through a pre-agreed fallback instead of a late scramble.

**Multi-perspective narrative.** Every artifact reads through multiple resume lenses:
* **Shared `contracts.py`:** an internal code contract for SWE; a golden interface other "teams" build against for platform engineering.
* **Terraform + `kind` + K8s manifests, fully cloud-portable:** an infra-as-code exercise for SWE; the paved road every new service lands on for platform engineering.
* **Local CI/CD pipeline:** an automated gate for SWE; a self-service path to "production" without hand-holding for platform engineering.
* **Circuit breaker FSM:** a resilience pattern for SWE; a reliability primitive every future module inherits for free, for platform engineering.

**What was deliberately not added, and why.** A full internal developer portal (Backstage-style) is the canonical "real" version of this work, but it's a multi-month investment even for an experienced team. Building a platform that does everything before a single golden path is proven is the dominant failure mode at this stage. **This plan ships one narrow golden path** (module scaffolding) with one honest metric — not a portal. See the Phase 7 decision record.

---

## Scope & Artifact Map

One table covers what's being built, which track(s) it supports, and how firmly it's committed. **Must-ship** items are non-negotiable and support all three resumes. **Degrade-gracefully** items carry a pre-agreed fallback, so a schedule slip becomes a planned substitution, not a scramble.

**Zero-Cost Infrastructure Guarantee (scope-level):** every row resolves to $0/month. Local components run on the i5-13500H dev machine. The OCI Always Free ARM64 environment is an on-demand exception — activated only for Operational Tasks and torn down immediately after each session. The only always-on external endpoint is N18, surfaced through a Cloudflare Tunnel.

| Artifact | Tracks | Tier / fallback if time is short |
|---|---|---|
| Shared Pydantic V2 contracts (`contracts.py`, module ↔ N18) | SWE | Must-ship — already in place |
| Automated contract tests wired into local CI | SWE, Platform | Must-ship |
| Multi-stage Dockerfiles + healthchecks | SWE, Platform | Must-ship |
| Local CI/CD pipeline with one live deploy path per component (via Cloudflare Tunnel) | SWE, Platform | Must-ship |
| Locust load tests + structured logs | SWE, Platform | Must-ship |
| Circuit breaker FSM + unit tests + concurrency integration test | SWE, Platform | Must-ship |
| One before/after comparison chart (failure → fallback) | SWE, Platform | Must-ship |
| Golden-path scaffolding CLI + timed before/after DX metric | SWE, Platform | Must-ship — the lead platform-eng proof point |
| Multi-arch images (`linux/amd64` + `linux/arm64`) for N18 and N1 | SWE, Platform | Must-ship — OCI Ampere A1 compatibility |
| OCI on-demand pipeline (Terraform + Helm, provision and tear down OCI ARM64, Phase 5) | Platform | Must-ship — the concrete cloud-portability proof |
| Decision records | Network, SWE, Platform | Must-ship |
| One resume per track | Network, SWE, Platform | Must-ship |
| Terraform-provisioned local Kubernetes (`kind`) cluster + NetworkPolicies | Network, Platform | Degrade-gracefully → manifests written and explained, not fully load-validated |
| HPA autoscaling (validated against a metric it can actually move on) | Platform | Degrade-gracefully → same as above |
| Self-hosted Prometheus/Grafana dashboard | Platform | Degrade-gracefully → dashboard optional; the Ephemeral Infrastructure Reconstruction Runbook stays must-ship |
| Governance-as-code admission check in CI | Platform | Degrade-gracefully → documented checklist instead of an enforced CI step |
| Minimal platform docs (golden path index) | Platform | Degrade-gracefully → single `PLATFORM.md` instead of a rendered static site |
| Container image scanning (`trivy`) in CI | SWE, Platform | Degrade-gracefully → manual scan report instead of blocking CI gate |
| Demo video polish | Network, SWE, Platform | Degrade-gracefully → shorter, less-polished cut; content stays, production value flexes |

---

## Timeline at a Glance

| Period | Phase | Focus |
|---|---|---|
| August | 0 | Baseline capture, architecture snapshot |
| September | 1 | Docker, N1 local microservice extraction, hub-and-spoke stack |
| Oct–Nov | 2 | Local CI/CD, Vagrant hypervisor bootstrap, Cloudflare Tunnel live exposure |
| December | 3 | Local chaos engineering + hypothesis-driven failure test, postmortem (Compose only) |
| January | — | Exam buffer, zero project work, entire month |
| Feb–Mar | 4 | Terraform + Kubernetes self-taught from scratch; local, cloud-portable `kind` deployment |
| April | 5 | Observability (local `kind`) + OCI on-demand pipeline — first live `terraform apply` against OCI ARM64 |
| May | 6 | Circuit breaker resilience refactor |
| June, weeks 1–2 | 7 | Golden path: scaffolding CLI, governance check, DX metric, platform docs |
| June, weeks 3–4 | 8 | Portfolio packaging: system docs, test metrics, 3 targeted resumes, video demo |

---

## Phase 0 — Baseline (August)

**Goals**
- **Capture a "before" reference point** for later comparisons across latency, infrastructure cost, and system throughput.
- **Document the system in its current state** (monolithic hub-and-spoke with managed Supabase DB and in-process execution) and establish its known operational risks without triggering failure yet.

**Tasks**
- **Conduct a full current-state architecture audit**: Document all existing module contracts, the in-process execution model inside N18, and the active Supabase PostgreSQL schema/extension baseline.
- **Run a baseline load check** against N5 activity generation under light, normal traffic; record p50/p95 latency as the reference point.
- **Document the single-provider N5 setup** and its rate-limit exposure, framed explicitly as a **hypothesis to be tested in Phase 3**.
- **Create `docs/highlights.md`** as a living log — updated at the end of every phase — capturing quantified achievements, metrics, and decision outcomes. This is the single source of truth all three resumes draw from in Phase 8.

**Docs**
- System-wide current-state snapshot and problem/risk statement in top-level `README.md`.
- `docs/architecture-as-is.md` covering existing endpoints, module boundaries, database dependency layout, and manual execution steps (`run.bat`).

**Deliverables**
- `benchmarks/results/2026-08-baseline.json`
- `docs/architecture-as-is.md`

---

## Phase 1 — Containerization & Local Hub-and-Spoke Stack (September)

> **Linux Prerequisite — Container-Level Essentials.** Before writing Dockerfiles and shell scripts, acquire working fluency in: filesystem navigation (`ls -la`, `cd`, `grep`, `find`, `cat`, `less`), file permissions & ownership (`chmod`, `chown`, standard POSIX modes like 755/644, root vs. non-root container users via `USER`), environment variables & shells (`export`, sourcing `.env`, `sh` vs `bash` differences), basic POSIX shell scripting (loops, exit codes `$?`, piping `|`, redirection `> /dev/null 2>&1`) for `scripts/pg_dump_cron.sh`, and stdout (fd 1) vs stderr (fd 2) redirection — critical for Docker's stdout-based logging model.

**Goals**
- **Replace `run.bat`** with a fully containerized, reproducible local stack.
- **Stand up N1 as an independently deployable local service**; confirm N18 calls it over the existing `/embed` contract.
- One month is realistic here — the Compose file structure, the `contracts.py` pattern, and the Postgres/pgvector wiring already exist. This phase is the N1 extraction itself, not groundwork from zero.

**Tasks**
- **Extract embedding logic** into `n1_service/app.py`, a standalone containerized FastAPI service exposing `/embed` — **run entirely inside the local Docker network**, with no external hosting dependency of any kind.
- **Author `Dockerfile.n18`** and **`Dockerfile.n16`** as multi-stage builds. For N18 and N1, target both `linux/amd64` (local i5-13500H) and `linux/arm64` (OCI Ampere A1) — cross-compiling from the start avoids a retrofit in Phase 5. N16 stays on Vercel (`linux/amd64` only, no change needed).
- **Author `docker-compose.yml`** wiring N1, N18, N16, and a local Postgres/pgvector container on a shared `travel-net` bridge network, healthcheck-gated startup, named volume for durability. **This step formally migrates the N3 database off the managed Supabase instance.**
- **Enforce environment-driven configuration** across N18 and N1: all hostnames, ports, credentials, and LLM provider URLs read from environment variables. `docker-compose.yml` supplies the local values; `oci.tfvars` will supply the OCI values in Phase 5 — the application binary never changes between environments.
- **Establish a secrets management baseline**: commit a `.env.example` with all required variable keys (no values); keep `.env` in `.gitignore`. Document the convention that secrets never appear in `docker-compose.yml` directly — they are always injected via `env_file`. This pattern upgrades to Kubernetes Secrets in Phase 4.
- **Write `scripts/pg_dump_cron.sh`** for local backup of the local Postgres/pgvector volume.
- **Diagram the container network** end to end.

**Docs**
- Decision record — why N1 is the only extracted spoke.
- Decision record — why HTTP REST over gRPC for the N18↔N1 call.
- Decision record — why Docker Compose before Kubernetes for local dev.
- Decision record — why N1 stays fully local instead of any external hosting platform (the Zero-Cost Infrastructure Guarantee applied at the microservice level).
- Decision record — secrets management strategy (`.env` → K8s Secrets → sealed-secrets migration path).
- `docs/N1-embed-api.md`.
- Service READMEs (N1, N18, N16).

**Deliverables**
- Working `docker compose up` stack, all healthchecks green.
- Container network diagram.

---

## Phase 2 — Local CI/CD & Cloudflare Tunnel Live Exposure (Oct–Nov)

> **Linux Prerequisite — System Administration & Networking.** Managing a headless Vagrant VM requires: service management (`systemctl status/start/enable`, `journalctl -u`), writing a `systemd` unit file for `cloudflared`, SSH key management (`ssh-keygen`, `~/.ssh/authorized_keys`, SSH tunnel basics), Linux networking fundamentals (loopback `127.0.0.1`, interfaces `eth0`/`docker0`, port bindings, `/etc/hosts`, `/etc/resolv.conf`), process inspection (`htop`, `df -h`, `free -m`, `ss`, `ip a`), and package management (`apt-get update && apt-get install -y`, cleaning caches to reduce image sizes).

**Goals**
- **Gate every merge to `main`** with automated checks running on local infrastructure.
- **Expose the system live** without introducing a single paid or hosted backend dependency.

**Tasks**
- **Adopt trunk-based development**: all work lands on short-lived feature branches merged to `main` via PR; no long-lived branches. The CI gate enforced below is the quality bar — if CI passes, the branch merges.
- **Enforce a lint/format gate**: `ruff`, `black --check`; `eslint` + `prettier --check` (N16) — failing, not warning-only.
- **Add container image scanning** via `trivy image` in the CI workflow — scan N18 and N1 images for HIGH/CRITICAL CVEs on every build. Non-blocking initially (report-only); promote to a blocking gate once the baseline is clean.
- **Bootstrap a local hypervisor VM** via `vagrant up`. **Phase 2 & 4 Execution Refinement:** Run Vagrant strictly as a single-node hypervisor VM for the initial Docker Compose staging stack (hosting N18, N1, Postgres/pgvector), but execute `kind` directly on the host OS in Phase 4 to eliminate nested virtualization overhead.
- **Configure a Cloudflare Tunnel** on the Vagrant VM to securely bridge the local N18 orchestrator to the public internet — this is the **only** externally reachable backend endpoint in the entire system.
- **Deploy N16 to Vercel** via native GitHub integration — the frontend remains the sole component on managed hosting, and it talks exclusively to N18 through the tunnel.
- **Run PostgreSQL + pgvector locally** inside the Vagrant VM's Compose stack — completing the migration away from Supabase so no managed database provider exists anywhere in the pipeline.
- **Enable BuildKit layer caching** for N18 and N1 builds to keep local CI fast.
- **Configure multi-arch cross-compilation in CI**: use `docker buildx` to emit both `linux/amd64` and `linux/arm64` image manifests for N18 and N1 on every build — the `linux/arm64` layers land in the local registry and are ready for Phase 5's OCI Ampere A1 target with no additional build step.
- **Wire contract tests** into the local CI pipeline, prioritizing N1 and N5 coverage gaps.
- **Add integration smoke tests** with retry-with-backoff to tolerate Vagrant VM cold-boot latency.
- **Enforce branch protection**: local CI must pass before merge.

**Docs**
- `docs/deployment-runbook.md` — Vagrant provisioning steps, Cloudflare Tunnel configuration, and tunnel-credential rotation procedure.

**Deliverables**
- `.github/workflows/ci-n1.yml`, `.github/workflows/ci-core.yml` (self-hosted runner targeting the local Vagrant VM where applicable).
- `Vagrantfile` with multi-stage provisioning.
- `cloudflared` tunnel configuration (`config.yml`) under version control (credentials excluded).
- `tests/smoke/` — 4+ integration tests.
- CI status badges.
- Trivy scan report (initially non-blocking).
- Vagrant-hosted stack and tunnel stable by end of November — Phase 3 starts in December on a finished environment, not a still-settling one.

---

## Ephemeral Infrastructure Reconstruction Runbook (every phase from Phase 2 onward)

- **Time every teardown-and-rebuild cycle** of the Vagrant hypervisor VM and, from Phase 4 onward, the local `kind` cluster — `vagrant destroy && vagrant up`, `kind delete cluster && terraform apply`.
- **Log reconstruction time and failure points** in `docs/ephemeral-infra-log.md` at the start of every phase — this replaces any cloud vendor-risk tracking, since the architecture carries no external vendor dependency to track.
- **Validate that Terraform state and Vagrant provisioning scripts fully reconstruct the environment** from a clean host with no manual intervention.
- The log itself is the artifact: it demonstrates operational discipline around ephemeral, disposable infrastructure — the zero-cost equivalent of a cloud vendor-risk review.

---

## Phase 3 — Local Chaos Engineering & Hypothesis-Driven Failure Test (December)

**Goals**
- **Confirm the reliability hypothesis from Phase 0**: the single-provider N5 chain fails under concurrent load — a designed test of a predicted failure mode, not an accidental discovery.
- **Stress the full local stack**, not just the LLM-dependent path, through application-level chaos engineering.

**Tasks**
- **Write `loadtests/locustfile.py`**: 70% search / 20% activity generation / 10% feedback.
- **Run the primary load test** against the local Docker Compose stack, ramping 10→50 concurrent users. No Kubernetes cluster exists yet — that's Phase 4 — so this run and its cascade recording are Compose-only.
- **Run a secondary confirmation** against the Cloudflare-Tunnel-exposed live N18 endpoint, short and low-concurrency, only while actively monitoring; skip and document the decision if it risks destabilizing the tunnel.
- **Inject chaos directly into the Compose stack**: drop the Postgres/pgvector container mid-request, inject artificial latency into the N1↔N18 call, and force-kill the N18 container under active load — capture recovery behavior for each.
- **Validate backup restore path**: as part of the DB-drop chaos scenario, restore from the most recent `pg_dump` backup (written in Phase 1's `pg_dump_cron.sh`) and confirm data integrity — a backup that has never been restored is not a backup.
- **Warm the stack before every run**; call out cold-start effects explicitly.
- **Capture Locust error-rate graphs**, raw provider error logs, and a screen recording of the local cascade and chaos-injection recovery.
- **Write a same-day postmortem**, framed as hypothesis confirmed, not discovered.

**Docs**
- `docs/incident-2026-12-n5-429-storm.md`.
- `docs/local-infrastructure-disruption-runbook.md` — documents each chaos scenario (DB drop + restore, latency injection, container kill), observed blast radius, and recovery time.

**Deliverables**
- `loadtests/locustfile.py`, cascade recording, chaos-injection recovery recordings (including DB restore validation), live-tunnel confirmation dataset if obtained.

---

## January — Exam Buffer

Zero project work, entire month. Phase 3 finishes clean in December, so nothing sits mid-task when exams start and nothing waits on the buffer to end before it can begin.

---

## Phase 4 — Local, Cloud-Portable Kubernetes Deployment (Terraform + `kind`) (February–March)

> **Linux Prerequisite — Kernel Primitives & Container Internals.** Understanding how Kubernetes isolates workloads requires kernel-level concepts: **namespaces** (PID, NET, MNT isolation — the actual technology behind Docker containers), **cgroups** (how the Linux kernel enforces CPU and RAM limits on pods, directly relevant to HPA and resource requests/limits), **process signals** (SIGTERM (15) vs SIGKILL (9) — how FastAPI/N18 gracefully shuts down inside a K8s pod), and **multi-arch binary awareness** (`uname -m`, understanding `x86_64`/`amd64` vs `aarch64`/`arm64` for the OCI Ampere A1 target).

**Goals**
- **Provision Kubernetes with Terraform** and deploy N18 onto it, locally, at zero cost.
- **Prove environment neutrality**: the same manifests and Terraform modules must be retargetable to a managed cloud cluster via variable file alone.
- Terraform and Kubernetes are both learned from scratch starting here — the two-month window exists specifically to absorb that curve, not because the task list alone demands it.
- **Run `kind` directly on the host OS** (not inside the Vagrant VM) to eliminate nested virtualization overhead — the Vagrant VM continues hosting the Compose staging stack and CI runner, as established in Phase 2.

**Tasks**
- **Design local network segmentation on paper first** — public/private segments via NetworkPolicies, as the free/local stand-in for a VPC.
- **Modularize `infra/`** into `infra/modules/cluster`, `infra/modules/network`, and `infra/environments/{local,oci}.tfvars` — the local module targets `kind`; the `oci` module targets OCI ARM64 Ampere A1 with no application-facing changes.
- **Author `infra/environments/oci.tfvars`** targeting OCI ARM64 Ampere A1 (4 OCPU / 24 GB RAM); run `terraform plan -var-file="environments/oci.tfvars"` and confirm zero diffs to Kubernetes manifests or application code. The first live `terraform apply` against OCI happens in Phase 5 — this phase validates the plan is zero-diff.
- **Write K8s manifests for N18**: Deployment (3 replicas), ClusterIP Service, Ingress (`ingress-nginx`), HPA — authored to be identical across local and cloud targets.
- **Configure liveness and readiness probes** for N18 and N1: liveness probes (`/health`) trigger container restarts on deadlock; readiness probes (`/ready`) gate traffic routing until the service is fully initialized (critical for N1's model-loading cold start). Document probe timeouts and failure thresholds in `k8s/README.md`.
- **Migrate secrets to Kubernetes Secrets**: move all credentials from Phase 1's `.env` files into K8s Secret objects, referenced via `envFrom` in Deployment manifests. This is the second tier of the secrets management strategy established in Phase 1.
- **Load images into `kind`** via `kind load docker-image` for local builds, or configure a local registry (`registry:2`) if image churn is high — document the chosen approach in `infra/README.md`.
- **Drive HPA scaling via KEDA targeting HTTP concurrency metrics rather than CPU utilization.** N5's bottleneck is I/O-bound, not CPU-bound, so a CPU-target HPA may never fire against real traffic. Using KEDA ensures the real Locust scenario legitimately drives autoscaling.
- **Re-run the Phase 3 Locust test** against the local cluster; confirm N5's 429 rate is unaffected by pod count — proves the bottleneck is provider-side, not compute-side. Record this run as the mid-project reproducibility baseline for the Phase 6 before/after comparison chart.
- **Document the rollback procedure**: validate `kubectl rollout undo deployment/n18` against a deliberately broken image tag; confirm traffic shifts back to the previous ReplicaSet within the readiness probe window. Log the rollback time.
- **Write `scripts/kind-teardown.sh`**; document in `infra/README.md` that Terraform state is not persisted across teardown by design, per the Ephemeral Infrastructure Reconstruction Runbook.

**Docs**
- Decision record — local `kind` vs. cloud-managed cluster.
- Decision record — HPA target metric choice.
- Decision record — Terraform module boundary design supporting the Cloud Portability Guarantee.
- Decision record — container image loading strategy (`kind load` vs. local registry).
- Local network segmentation diagram.
- `infra/README.md`.

**Deliverables**
- `infra/modules/`, `infra/environments/local.tfvars`, `infra/environments/oci.tfvars`, `k8s/` manifests, local-vs-live comparison chart, HPA validation evidence, zero-diff `terraform plan -var-file=environments/oci.tfvars` output as the Phase 4 cloud-portability proof, rollback validation log.

---

## Phase 5 — Observability & Ephemeral Infrastructure Governance (April)

**Goals**
- **Deliver operational visibility** with a fully self-hosted, zero-cost local stack.
- **Build and validate the OCI on-demand pipeline** — the Phase 4 `oci.tfvars` plan applied live for the first time: Terraform + Helm provisions N18, Prometheus, and Grafana on the OCI ARM64 cluster in a single `terraform apply`, then `terraform destroy` returns to $0.
- **Demonstrate disciplined ephemeral-infrastructure practice** in place of any external vendor tracking.
- Runs after Phase 4, not alongside it: the cluster must exist and be stable before instrumenting it, and stacking a second new tool on top of Terraform/Kubernetes while both are still being learned adds risk for no benefit.

**Tasks**
- **Continue Ephemeral Infrastructure Reconstruction Runbook logging** — heaviest use of `docs/ephemeral-infra-log.md` here, since Phase 4/5 add the most new infrastructure surface.
- **Emit structured JSON request logs** from N18, stdout-based, visible via `kubectl logs` locally and through the Cloudflare-Tunnel-exposed endpoint in the live evaluation path.
- **Deploy self-hosted Prometheus + Grafana** inside the local `kind` cluster via the Terraform Helm provider, scraping N18's `/metrics`.
- **Build a Grafana dashboard**: p50/p95/p99 latency, error rate, N5 429-per-minute, HPA pod count over time.
- **Build the OCI on-demand pipeline** — the core Phase 5 cloud deliverable: finalize `infra/environments/oci.tfvars` for OCI ARM64 Ampere A1; configure the Terraform Helm provider to deploy N18, N1, Prometheus, and Grafana onto the OCI cluster in a single `terraform apply`; validate full spin-up in under 5 minutes and teardown via `terraform destroy`.
- **Validate multi-arch images on real ARM64 hardware**: confirm the `linux/arm64` images built in Phase 2 run correctly on the OCI Ampere A1 node without emulation.
- **Deployment Policy:** All day-to-day development and instrumentation runs locally in `kind`. OCI is an on-demand target only — activated via Operational Tasks for metrics capture, demo recordings, or live interview hosting, and torn down immediately after each session.

> **Operational Task — OCI (Phase 5, first live apply):** After building the pipeline, run `terraform apply -var-file=environments/oci.tfvars`, confirm N18, Prometheus, and Grafana are live on the OCI ARM64 cluster, capture the Grafana dashboard screenshot as a deliverable, then `terraform destroy`. This is the cloud-portability proof.

**Docs**
- `docs/runbooks/embedding-service-down.md`, `docs/runbooks/high-429-rate.md`, `docs/ephemeral-infra-log.md`.

**Deliverables**
- Terraform-managed Prometheus/Grafana (local `kind`), dashboard JSON + local screenshot.
- OCI on-demand pipeline validated: live Grafana screenshot from OCI ARM64 cluster, spin-up time ≤ 5 min, `terraform destroy` teardown confirmed.
- Ephemeral infrastructure reconstruction log with 4–5+ entries.

---

## Phase 6 — Resilience: Circuit Breaker Refactor (May)

**Goals**
- **Solve the failure confirmed in Phase 3.**

**Tasks**
- **Define `providers.yaml`** and **build `ProviderChainManager`** as a three-state FSM (Closed/Open/Half-Open) with same-request cascade on failure.
- **Write six named unit tests** covering every state transition.
- **Write one integration test** exercising the manager under simulated concurrent failures — unit tests alone don't catch races under real concurrency.
- **Re-run the Phase 3 Locust scenario** locally (primary) and against the Cloudflare-Tunnel-exposed live endpoint (short confirmation) with the fallback chain active.
- **Build a comparison chart**: Dec (no fallback) vs. Feb/Mar (reproducibility check) vs. May (with fallback) — target <5% error rate at peak, down from ~100%.
- **Deployment Policy:** All chaos experiments and circuit breaker validation run locally on the `kind` cluster. OCI is activated once via the Operational Task below, solely to capture the live-cloud data point for the comparison chart.

> **Operational Task — OCI (Phase 6, one session):** After validating the circuit breaker locally, run `terraform apply -var-file=environments/oci.tfvars`, execute a short Locust confirmation with the fallback chain active against the live OCI cluster — this is the "with fallback, on real cloud hardware" data point for the before/after chart. `terraform destroy` immediately after.

**Docs**
- Decision record — circuit breaker FSM design, with state diagram.
- Update `docs/runbooks/high-429-rate.md` with the FSM reset procedure.

**Deliverables**
- `providers.yaml`, `ProviderChainManager`, `tests/unit/test_provider_fsm.py`, `tests/integration/test_provider_chain_concurrency.py`, comparison chart.

---

## Phase 7 — Golden Path: Scaffolding CLI, Governance Check, DX Metric, Platform Docs (June, weeks 1–2)

**Goals**
- **Deliver the one artifact the project is otherwise missing** for a platform-engineering story: proof that something you built made a *second* consumer's work measurably faster — not just proof the infrastructure runs.
- **Protect these two weeks specifically** — if anything upstream slips, this phase should not compress further; it is the lead artifact for the platform-engineering resume.

**Tasks**
- **Clock a timed manual baseline first**, before building anything: hand-build two small, structurally identical throwaway modules ("N19 — trip export," "N20 — trip archive," or genuinely useful ones if time allows) using the exact manual process from Phase 1/2 — write the Pydantic contract, wire it into N18, write its test scaffold, write its CI workflow, write its cloud-portable k8s manifest. **Time each build separately** with a stopwatch and log every file touched. Building two rather than one gives an honest sense of spread rather than a single noisy data point.
- **Build `n-cli new-module <name>`**: a Python CLI (Typer or Click; Cookiecutter template as an alternative) that generates, from a template — the Pydantic contract stub matching N18's existing pattern, a pytest scaffold wired to the existing contract-test harness, a CI workflow stub parameterized from the Phase 2 pipeline, a cloud-portable k8s manifest stub parameterized from the Phase 4 Deployment/Service/HPA pattern, and a checklist file.
- **Enforce governance-as-code**: build a CI job (`admission-check.yml`) that any new module must pass before N18 will route to it — naming convention, `/health` endpoint present, contract test passing. The scaffolding CLI generates a module that passes this by default; a hand-written one has to earn it.
- **Run a timed CLI-assisted build**: scaffold a comparably-sized third module using `n-cli`, clocked the same way as the manual baseline. Compare directly: time-to-first-green-CI-run, files hand-written vs. generated, manual decision points.
- **Publish minimal platform docs**: a single static site (mkdocs) or, if time is short, one well-organized `PLATFORM.md` — index of the golden path, links to runbooks, dashboards, decision records, and the ephemeral infrastructure log. Explicitly scoped as a lightweight stand-in for a real developer portal, not an attempt at Backstage.

> **Operational Task — OCI (Phase 7, demo capture):** After completing the timed CLI-assisted build locally, run `terraform apply -var-file=environments/oci.tfvars` and run the hand-build vs. CLI-build side-by-side demo on the live OCI cluster — the timed metric visible on screen. Record the session, then `terraform destroy`.

**Docs**
- Decision record — why a scaffolding CLI + static docs instead of a full internal developer portal (Backstage): a real portal is a multi-month, team-scale investment, and building one before proving a single golden path works is the over-engineering failure mode this project deliberately avoids. Write before building the CLI.
- `docs/golden-path-metrics.md` — the manual-baseline vs. CLI-assisted comparison, written immediately after the timed CLI run while the numbers are fresh. Report the manual runs as a range, not a single figure, and state plainly this is a small, self-timed sample, not a statistically rigorous study.

**Deliverables**
- `n-cli` tool + template.
- `admission-check.yml`.
- `docs/golden-path-metrics.md` with the timed before/after.
- Platform docs site (or `PLATFORM.md` under the degrade-gracefully fallback).
- Three scaffolded modules (two hand-built, one CLI-built) as evidence.

---

## Phase 8 — Wrap-Up: Docs, Resumes & Demo Video (June, weeks 3–4)

**Goals**
- **Close out the project with the least new writing possible** — everything here assembles from what Phases 0–7 already produced, not fresh composition under deadline.
- **Share the two weeks freely** across docs polish, resumes, and video — none blocks the others.

**Tasks**
- **Run a test coverage pass** on N5 and the N18 orchestration layer, target ≥70%, badge in `README.md`.
- **Auto-generate `docs/openapi.json`** — never hand-written.
- **Assemble `ARCHITECTURE.md`** from what already exists: system diagram, request lifecycle, hub-and-spoke rationale, data flow, the Zero-Cost Infrastructure Guarantee and Cloud Portability Guarantee as stated architectural constraints, and an index of every decision record written since August.
- **Draft all three resumes in parallel**, pulling directly from `docs/highlights.md` instead of writing from scratch:
  - **Network Engineer** — local network segmentation design (NetworkPolicies), Terraform-provisioned; Cloudflare Tunnel as the sole ingress path; Docker bridge network as conceptual precursor; framed honestly as translating cloud networking concepts into free, local equivalents.
  - **Software Engineer** — hub-and-spoke architecture, contract-tested boundaries; circuit breaker FSM (six unit tests + concurrency integration test); scaffolding CLI as a real Python tool-building artifact; OpenAPI docs, `ARCHITECTURE.md`, coverage metrics.
  - **Platform Engineering (Cloud/DevOps)** — multi-arch Docker builds (`linux/amd64` + `linux/arm64`), fully local CI/CD via Vagrant-hosted runners; Terraform-provisioned local Kubernetes + HPA (validated against a real or clearly-labeled synthetic metric), proven cloud-portable via `oci.tfvars` with a live OCI ARM64 apply, self-taught from a standing start; golden-path scaffolding CLI with a measured, quantified reduction in time-to-first-deploy (the lead artifact); governance-as-code admission check enforced in CI; Ephemeral Infrastructure Reconstruction Runbook demonstrating disposable-infrastructure discipline; self-hosted Prometheus/Grafana (local `kind` + validated on OCI ARM64).
  - **Check each resume** against 3–5 real entry-level postings per track for keyword alignment — for platform engineering specifically, check for "internal developer platform," "golden path," "developer experience," and "self-service."
- **Record a 6–9 minute screen-recorded demo**: containerizing and splitting N1 → Vagrant + Cloudflare Tunnel live exposure → the December chaos engineering and hypothesis test → local, cloud-portable Terraform + Kubernetes with Grafana → the circuit breaker fix and comparison chart → the golden-path CLI demo (hand-build vs. CLI-build side by side, timed metric on screen) → the OCI on-demand pipeline: live `terraform apply`, Grafana dashboard on real ARM64 hardware, `terraform destroy`. Narration is grounded entirely in numbers already captured — no new data generation.
- **Link all three resumes and the GitHub repository** in the video description; **add the video link** to `README.md` once exported.
- **Deployment Policy:** Keep the Phase 5 OCI pipeline warm — rehearse `terraform apply -var-file=environments/oci.tfvars` spin-up before each interview or recording session to confirm it still resolves in under 5 minutes.

> **Operational Task — OCI (Phase 8, demo recording + interviews):** Spin up the OCI cluster for the final demo video recording (if not captured in Phase 7) and for any live interview demos. Record the live cluster state as part of the video. `terraform destroy` after every session.

**Docs**
- `demo/script.md` before recording.

**Deliverables**
- Coverage badge.
- `docs/openapi.json`.
- `ARCHITECTURE.md`.
- `resume-network.pdf`, `resume-swe.pdf`, `resume-platform.pdf`.
- Final exported demo video.

---

## Risk Register

| Risk | Mitigation |
|---|---|
| Phase 3 slips past December and bleeds into the exam buffer | Phase 3's scope is deliberately small — one Locust scenario, three chaos-injection tests, a same-day postmortem — so a short overflow costs a few buffer days rather than delaying Phase 4 |
| Terraform and Kubernetes are both learned from scratch starting in Phase 4 | Phase 4 gets a full two months specifically because it's new material; Phase 5 no longer runs in parallel with it |
| Local `kind` cluster and Vagrant hypervisor strain the dev machine | Cap replica counts/resource requests; teardown between sessions per the Ephemeral Infrastructure Reconstruction Runbook |
| Cloudflare Tunnel drops or rate-limits mid-demo | Rehearse the tunnel start-up sequence before recording; keep the local Compose stack as an instant fallback demo path |
| OCI on-demand pipeline fails to apply cleanly during an Operational Task | Rehearse `terraform apply` before each recording session; if apply fails, the Phase 4 `terraform plan -var-file=environments/oci.tfvars` output is the accepted fallback deliverable for the cloud-portability proof |
| HPA doesn't demonstrably scale against real N5-bottlenecked traffic | Decide and document the target metric before building the test; synthetic fallback if concurrency-based isn't feasible in time |
| OCI Always Free tier capacity or availability issue during an Operational Task | OCI is activated on-demand only and torn down immediately after each session — maximum exposure is a few hours per recording or demo. If OCI is unavailable, the local `kind` stack with Cloudflare Tunnel is the instant fallback demo path |
| Phase 7 scope creep — building toward a full developer portal instead of one golden path | Decision record written before building the CLI makes the narrower scope explicit; docs site has an explicit degrade-gracefully fallback (`PLATFORM.md`) |
| The manual-vs-CLI timing comparison isn't apples-to-apples (different module complexity, fatigue, familiarity by the later runs) | Keep all modules deliberately minimal and structurally identical; run two manual baselines rather than one to get a sense of spread; note the comparison's limitations honestly in `docs/golden-path-metrics.md` |
| Phase 8's merged block (docs, resumes, video) still runs tight | Named 2–3 day flex buffer in early July, scoped to absorb slip only — if unused, the project finishes early |
| School curriculum + independent new-tech learning slows a phase | Must-ship / degrade-gracefully split gives every phase a pre-agreed fallback |
| Resume metrics inconsistent across versions | `docs/highlights.md`, updated every phase, is the single metrics source-of-truth all three resumes draw from |

---

## KPI Dashboard (update at end of each phase)

| Metric | Baseline (Aug) | Target (Jun) |
|---|---|---|
| p95 latency under load (local cluster) | From Phase 0 benchmark | ≥30% improvement, expected from the circuit breaker cutting retry/timeout tail latency |
| 429 error rate under storm load | ~100% at peak (Phase 3) | <5% |
| Contract-covered boundaries | Existing | 100% enforced in CI |
| Decision records written | 0 | 9+ (including the Cloud Portability Guarantee record and the Phase 7 golden-path scope record) |
| Test coverage (core modules) | Unmeasured | ≥70% |
| Ephemeral infrastructure reconstructions logged | 0 | One per phase from Phase 2 onward |
| Cloud-portability retarget proof (OCI) | N/A | Live `oci.tfvars` apply on OCI ARM64 validated (Phase 5) |
| OCI cluster spin-up time | N/A | ≤ 5 minutes via Phase 5 pipeline |
| Time-to-first-green-CI-run for a new module: manual vs. CLI-assisted | N/A | Quantified reduction, measured directly (Phase 7) |
| Monthly infrastructure spend | $0 | $0 |

---

## Optional Add-Ons

Attempt only once Phases 0–8 are stable and complete, using whatever time remains before the next commitment:
- OpenTelemetry distributed tracing across the N18↔N1 boundary.
- OCI multi-region stretch: provision a second OCI region for failover simulation using the same Phase 5 Terraform modules — only if the primary OCI on-demand pipeline is rock-solid and time allows.
- Split the Terraform modules further for multi-region local simulation, only if the stretch goal above is attempted.
- Add a second golden path to the CLI (e.g., `n-cli new-integration` for a Phase 5-style external provider), only if Phase 7's single golden path is solid and there's clear leftover time — resist adding this before then, per the over-engineering risk noted in Phase 7.

---

## Year 4 Preview — Platform Engineering & Cloud/DevOps Deep Specialization

- Distributed tracing and service mesh (Istio/Linkerd).
- GitOps (ArgoCD/Flux) replacing manual `terraform apply` / `kubectl apply`.
- A real managed cluster (EKS or GKE) with a real VPC, multi-AZ / multi-region failover — the natural continuation of the Cloud Portability Guarantee proven in Year 3.
- Spot instances + Karpenter for cost-optimized autoscaling.
- IAM least-privilege audit, secrets management, container image scanning in CI.
- A genuine internal developer portal (Backstage or similar), now justified by a proven, adopted golden path rather than built speculatively.
- Platform adoption metrics at team scale (not just a solo-project proxy): time-to-first-deploy across real users, golden-path usage rate, platform NPS.
- Part 2 demo video: "operating it at scale."

Do not pull this scope into Year 3 — it dilutes the tri-track balance this roadmap is built around.
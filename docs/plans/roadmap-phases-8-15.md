# Phase 8–15: Month-by-Month Plans

[← Back to roadmap index](roadmap.md)

## Phase 8: May 2027 — Observability, SLOs and Scaling

**Goal.** See the system, define what healthy means, and test whether scaling out actually helps.

**Exit.** An alert fires during a Locust run on `kind` and resolves afterwards, and the runbook is what you use to resolve it. A scaling experiment shows more replicas do not bypass the upstream limit.

**Resource note.** The full kube-prometheus-stack is heavy. Use a 30 s scrape interval, short retention and trimmed components.

- **Week 1.** Install kube-prometheus-stack through the Terraform `helm_release` (4 h). ServiceMonitors for N18 and N1, adding `/metrics` to N1 (2 h). The same stack as a Compose `obs` profile (2 h, S). Spare (2 h).
- **Week 2.** Grafana dashboard as code (JSON in the repo, provisioned through a ConfigMap): request rate, error codes, p50/p95, breaker state, in-flight requests, pod count (6 h). Choose two or three SLIs and SLOs; write `docs/slo.md` and ADR-0023 (4 h).
- **Week 3.** Alert rules: SLO burn rate, breaker open for more than five minutes, N1 down (4 h). An Alertmanager receiver that you can actually see, such as a free chat webhook (2 h). Finish `embedding-service-down.md` and link `high-429-rate.md` from the alert (3 h). Spare (1 h).
- **Week 4.** HPA on CPU with metrics-server (kind usually needs a kubelet TLS flag for it) (3 h). Locust run showing replicas rise while 429s stay bounded by the upstream limit; chart it (3 h). ADR-0009: HPA metric choice (1 h). Clean-room run (2 h). Highlights (1 h).

**Tiers.** M: Prometheus and Grafana from Terraform, dashboard as code, one SLO, one firing alert tied to a runbook, the scaling experiment. S: burn-rate alerts, a visible receiver, N1 metrics, Compose `obs` profile. X: KEDA with a Prometheus scaler, Loki for logs.

**Anywhere checkpoint.** All targets can run with the observability stack enabled.

---

## Phase 9: Jun 2027 — OCI Foundations

**Goal.** Learn real cloud primitives with Terraform before deploying anything onto them.

**Exit.** `terraform apply -var-file=environments/oci.tfvars` creates a VCN, subnets, security rules and an Ampere A1 Ubuntu VM that boots k3s through cloud-init, reachable by SSH only from your IP. `terraform destroy` leaves nothing behind. A $1 budget alert exists.

**Verify first (Appendix D).** Always Free limits and the rules for idle-instance reclamation. If A1 capacity never frees up in your home region, upgrading to pay-as-you-go can help while staying inside the free limits, but it puts a card on file, so keep the budget alert.

- **Week 1.** Account, home region (it cannot be changed later; check where A1 capacity is more likely), budget alert (2 h). A dedicated compartment, an IAM group and user with a least-privilege policy and an API key, instead of using the root identity for Terraform (4 h). ADR-0024: OCI topology (compartment, VCN layout, who can do what) (3 h). Spare (1 h).
- **Week 2.** `infra/modules/network`: VCN, public subnet, internet gateway, route table, and security rules. Learn network security groups versus security lists and pick one (6 h). Allow SSH from your IP only and 80/443 as the gateway needs; keep 6443 closed (2 h). `infra/oci/` root module (2 h).
- **Week 3.** Compute module: A1 instance with an Ubuntu arm64 image and cloud-init that runs the same `bootstrap/k3s-node.sh` used for the k3s target (6 h). A retry script for out-of-capacity errors (2 h). Basic hardening: key-only SSH, host firewall, unattended upgrades (2 h).
- **Week 4.** Three apply and destroy cycles, timed and logged (3 h). `make up TARGET=oci` for the infrastructure part (3 h). IAM review: write down what each policy statement allows (1 h). Clean-room run (2 h). Highlights (1 h).

**Tiers.** M: account and budget guard, scoped IAM, VCN, VM with k3s, clean destroy. S: capacity retry script, hardening. X: an OKE Basic cluster experiment, OCI Bastion.

**Anywhere checkpoint.** oci creates and destroys its infrastructure from one command.

---

## Phase 10: Jul 2027 — OCI Deployment and Portability Proof

**Goal.** Run the same chart on a real cloud with only values changed.

**Exit.** `make up TARGET=oci` ends healthy. The same chart and manifests run on kind, k3s and OCI, and the only differences are in `config/<target>/values.yaml` and `*.tfvars`. Multi-arch is verified on arm64.

- **Week 1.** The cloud VM cannot reach your local registry, so this is where the registry variable is tested: publish release images to GHCR (public, free) or OCIR and set the OCI values accordingly; have Jenkins push to both on release tags (4 h). `config/oci/values.yaml`: registry, storage class, gateway class, hostname (2 h). Public hostname for the gateway: either a Cloudflare quick tunnel, or a free IP-based name such as `<ip>.sslip.io` with a Let's Encrypt certificate (verify rate limits first) (4 h).
- **Week 2.** Arm64 verification: every image is multi-arch, check `uname -m` inside pods, confirm pgvector and the N1 model runtime work on aarch64 and note any speed difference (5 h). `make verify TARGET=oci` (2 h). Deploy the observability stack with the same Helm values (3 h).
- **Week 3.** Locust against OCI and a comparison with kind. Note the limitation: load generated from your Ubuntu machine also measures your internet path, so label the result accordingly (4 h). Storm test against OCI to confirm the breaker holds (2 h). Record CPU, memory, disk and egress against the free limits (2 h). Spare (2 h).
- **Week 4.** Decide ephemeral versus always-on: a small always-on k3s node is realistic practice, but check Oracle's current idle-reclamation rules first (1 h). Measure infrastructure spin-up against the 5-minute KPI (2 h). Write `docs/anywhere-matrix.md`: every capability against every target, with status and timing (3 h). Clean-room run on all four targets (2 h). Highlights (2 h).

**Tiers.** M: OCI deployment with the same chart, multi-arch proof, `make verify` green, the matrix. S: sslip.io TLS, observability on OCI, the Locust comparison. X: a second worker node to try multi-node scheduling, a second region.

**Anywhere checkpoint.** All four targets are healthy and documented.

---

## Phase 11: Aug 2027 — The CD Sprint (GitOps, Secrets, Supply Chain, Policy)

**Goal.** A merge to `main` reaches the cluster with no manual step, safely.

**Exit.** Merge, build, scan, sign, tag update in the GitOps repo, Argo CD sync, all without touching the cluster. A policy rejects an unsigned image and a pod without probes. Secrets live encrypted in git.

**Bring-up impact.** `make up` gets two modes: `MODE=gitops` (installs Argo CD pointing at the GitOps repo) and `MODE=direct` (plain `helm install`, no git remote needed). Keeping `direct` preserves the offline and anywhere promise.

- **Week 1.** Install Argo CD from the bootstrap path (3 h). App-of-apps: the chart, the monitoring stack and the policies as separate Applications (4 h). GitOps repo layout, with environment differences as values files (2 h). ADR-0025 (1 h). Argo CD polls git outbound, so it works behind NAT with no webhook.
- **Week 2.** Extend the Jenkinsfile: build, test, scan, push, then commit the new image tag to the GitOps repo (5 h). Rollback by `git revert`, proven once (1 h). Drift test: change something live with `kubectl` and watch Argo self-heal (1 h). Sync waves and health checks (3 h).
- **Week 3.** Secrets in git. Two options: sealed-secrets (simple with Argo, but the decryption key belongs to one cluster and must be backed up) or SOPS with age (more setup with Argo, but the key travels with you and decrypts on any cluster, which matches the anywhere goal). The lean here is SOPS plus age; decide in ADR-0026 (10 h including migrating the existing Secrets).
- **Week 4.** `syft` SBOM and key-based `cosign` signing in Jenkins (keyless signing needs an OIDC identity provider) (3 h). Kyverno policies: verify image signatures, require probes, require limits, disallow `latest` (5 h). Prove each policy rejects a bad manifest (1 h). ADR-0027 (1 h).

**Tiers.** M: Argo CD with app-of-apps, Jenkins updating the GitOps repo, drift self-heal, encrypted secrets in git, one Kyverno policy rejecting a bad manifest. S: cosign and image verification, SBOM, `git revert` rollback demo. X: Argo Rollouts canary, an image-updater, policy reports in Grafana.

**Anywhere checkpoint.** `make up MODE=gitops` bootstraps any kind or k3s Ubuntu cluster from the repo.

---

## Phase 12: Sep 2027 — Developer Experience and Tracing

**Goal.** Make adding a new module a measured, repeatable path, and make a request visible across services.

**Exit.** `travel-cli new-spoke <name>` produces a module with code, tests, Dockerfile, chart values and CI registration. Time to first deploy is measured against the manual baseline. A trace shows one request crossing N18 and N1.

- **Week 1.** Manual baseline: add a trivial new in-process spoke by hand, from nothing to deployed through GitOps, writing down every step and the time (4 h). Design the template and write ADR-0013 (2 h). Build it with a templating tool such as Copier or cookiecutter (4 h).
- **Week 2.** `travel-cli` (for example with Typer): `new-spoke`, `lint-module`, and a wrapper that runs `make verify` for one module (7 h). CI admission check that a new module exposes `/health` and `/metrics`, matches `contracts.py`, and has probes and limits in its chart values (3 h).
- **Week 3.** Time the CLI path and write `docs/golden-path-metrics.md` (3 h). Compile `PLATFORM.md` as the index of endpoints, workflows and runbooks (3 h). Optional docs site with MkDocs Material on GitHub Pages (4 h, S).
- **Week 4.** OpenTelemetry in N18 and N1, an OTel Collector, and a trace backend such as Tempo or Jaeger, with context propagated across the N18 to N1 HTTP call and a Grafana trace view (8 h). ADR-0028 (1 h). Highlights (1 h).

**Tiers.** M: manual baseline, CLI with one template, CI admission check, metrics doc, `PLATFORM.md`. S: tracing across N18 and N1, docs site. X: a second template, trace IDs in structured logs for log-to-trace correlation.

**Anywhere checkpoint.** A newly scaffolded module deploys on every target without edits.

---

## Phase 13: Oct 2027 — Reliability: Backups, DR and Game Days

**Goal.** Prove you can lose the cluster and the data path and recover, with numbers.

**Exit.** A full DR drill: the cluster is destroyed, rebuilt, the database restored from an off-site backup and the app redeployed through GitOps, with every step timed and RTO and RPO stated. Two to three game days are written up.

- **Week 1.** ADR-0029: logical backups with `pg_dump` as a CronJob, encrypted with age and shipped to free-tier object storage (verify the limits), with an RPO and RTO you choose and defend, for example RPO 24 h and RTO 60 min (6 h). `make restore` (3 h). Spare (1 h).
- **Week 2.** DR drill 1: destroy the cluster completely, run `make up MODE=gitops`, restore from the off-site backup, run `make verify` plus data checks, and time each step (6 h). Fix every gap the drill exposes (4 h). Write `docs/dr-drill.md`.
- **Week 3.** Game days with Chaos Mesh or Litmus: kill N18 pods, add network delay on N18 to N1, take N1 down, stop the VM (a node-loss analogue). Each one gets a hypothesis, steady-state metrics, an injection, observations and a short writeup in `docs/gamedays/` (10 h).
- **Week 4.** SLO review against real data, alert tuning, an error-budget summary (3 h). Decide whether to extract N5 as a second service (ADR-0030); if yes, scope it as stretch work (2 h). Clean-room run (2 h). Highlights (1 h). Spare (2 h).

**Tiers.** M: off-site backup, restore drill with timings, two game days. S: third game day, SLO review, `make restore`. X: extract N5 as a second service, Velero for cluster-level backup, a Postgres operator with WAL archiving for a lower RPO.

**Anywhere checkpoint.** `make up` plus `make restore` rebuilds a working system with data on any target.

---

## Phase 14: Nov 2027 — Freeze and Publish

**Goal.** Stop building, make everything legible and public.

**Exit.** Documentation is complete and consistent, write-ups are published, the demo exists, resumes are updated from `highlights.md`, all cloud resources are destroyed, and spend is still $0.

- **Week 1.** Raise core backend coverage to 70% or more and add a coverage gate in CI (6 h). Export `docs/openapi.json` (1 h). Fix flaky tests (3 h).
- **Week 2.** `ARCHITECTURE.md`: C4-style context and container views, a deployment view per target, the ADR index and the portability constraints (6 h). `README.md` with the zero-cost statement and a `make up` quick start (2 h). Update the docs tree for everything added since the original plan (2 h).
- **Week 3.** Public write-ups: the 429 storm and its fix with the before/after charts (your strongest story), and the Anywhere Contract (8 h). Update resumes per track from `highlights.md` as the single source of numbers (2 h).
- **Week 4.** Demo script in `demo/script.md` and a 6 to 9 minute recording: bring-up on a fresh Ubuntu VM, the storm and the breaker, a GitOps deploy, a DR restore (7 h). Verify every cloud resource is destroyed and spend is $0 (1 h). Clean-room run (2 h).

**Tiers.** M: coverage gate, OpenAPI, `ARCHITECTURE.md`, README, frozen highlights, resumes, teardown check. S: both write-ups, demo video. X: a third write-up on the zero-cost platform lab, the docs site.

**Anywhere checkpoint.** `docs/bring-up.md` is final.

---

## Phase 15: Dec 2027 — The Anywhere Gauntlet and v1.0

**Goal.** Prove the original promise, then release.

**Exit.** A scripted gauntlet takes a fresh clone to a healthy system on each target on clean Ubuntu machines, within the time budgets in section 3.5. A second person succeeds using only the docs. v1.0 is tagged.

- **Week 1.** `scripts/gauntlet.sh`: for each target, provision a clean Ubuntu host (Vagrant for compose and k3s, the toolbox for kind, Terraform for OCI), run `doctor`, `up`, `verify`, `down`, and collect the timings into a table (8 h). Fix whatever fails (2 h).
- **Week 2.** Second-person test: someone else follows only `docs/bring-up.md` while you watch and say nothing (3 h). Fix every stumbling point in docs and scripts (3 h). Run the gauntlet from Ubuntu, from WSL2 Ubuntu on Windows, and against arm64 on OCI (4 h).
- **Week 3.** Release v1.0: tag, images pinned by digest, signatures and SBOMs attached, `CHANGELOG.md`, runbook index, final KPI table (6 h). Cost audit and teardown (2 h). Retrospective in `docs/retrospective.md`: what worked, what to change (2 h, S).
- **Week 4.** Stretch work, chosen by interest: a second OCI region for failover with the same Terraform modules, a service mesh preview (Istio or Linkerd), a Backstage portal preview, a cost-aware autoscaling study (Karpenter-style), extracting N5 if not yet done (10 h, X).

**Tiers.** M: gauntlet script, second-person test, v1.0 tag, final KPIs. S: retrospective, cost audit. X: the stretch picks.

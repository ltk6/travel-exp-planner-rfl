# Travel Experience Planner: Platform Roadmap v2

**Aug 2026 to Dec 2027** | Real-world DevOps, cloud and infrastructure practice | 10 hours per week | Ubuntu-first, runnable anywhere

## 1. Scope

Build, break, fix and operate one real system the way a platform team would. The system runs on Ubuntu natively. Every phase ends with a clean-room bring-up test from a fresh Ubuntu clone.

**The spine:** containerize, automate CI, expose publicly, break it with load and chaos, fix it with a circuit breaker, prove the fix with before/after numbers, run it on Kubernetes, codify it in Helm and Terraform, observe it, run it on a real cloud, deploy it by GitOps, harden it, rehearse disaster recovery, and prove it runs anywhere.

## 2. Ground rules

**Platform.** Ubuntu 24.04 LTS is the primary host for all development and operations. Docker Engine (not Docker Desktop), WSL2, and macOS are secondary targets. The `make shell` toolbox brings parity on secondary hosts.

**Hours.** 10 h/week is about 43 h/month and about 600 h across the 60 weeks. Each month reserves about 6 h of standing overhead: a 1 h weekly ritual (update `docs/highlights.md` and `docs/ephemeral-infra-log.md`) plus a 2 h clean-room run in the last week. That leaves about 37 h of build time per month.

**Tiers replace buffers.** Every task is tagged:

- **M (must-ship):** the phase is not done without it. About 60% of the hours.
- **S (should-ship):** normally done, and the first thing cut when behind. About 25%.
- **X (stretch):** only when ahead. About 15%.

If a month ends with an M item unfinished, it moves into the next month, and that month's X items are dropped first, then its S items. M items are never dropped, only moved. Every phase has an exit criterion that is a command or a number, not a feeling.

**Code freeze, relaxed.** After Phase 0, application changes are limited to bring-up support (migrations, seed data, config via env), observability (`/metrics`, structured logs, trace hooks) and resilience (circuit breaker, async N5 path). No new product features.

**Zero cost.** Monthly spend stays $0. Put a budget alert ($1) on any cloud account. A domain name is the one optional purchase (see Phase 3).

**Volatile facts.** Tooling moves fast. At the start of each phase spend 30 minutes re-checking the items in [Appendix D](roadmap-appendices.md#appendix-d-volatile-facts-to-re-verify-at-each-phase-start) and record the result in `docs/volatile-facts.md`.

## 3. The Anywhere Contract

**Goal:** on a supported Ubuntu host, a fresh clone plus one command brings the whole system up healthy, one command proves it, and one command removes it.

### 3.1 Command surface

| Command | What it does |
| --- | --- |
| `make doctor` | Checks tool versions, CPU architecture, free RAM and disk, open ports, Docker access. Prints exactly what is missing. |
| `make up TARGET=compose` | Provisions the target, pulls prebuilt images (or builds with `BUILD=1`), runs migrations, seeds data and starts the stack. TARGET is one of `compose`, `kind`, `k3s`, `oci`. |
| `make verify TARGET=...` | Runs the smoke suite against the target's URL. Exit code 0 means healthy. Logs the timing. |
| `make down TARGET=...` | Removes everything `up` created. |
| `make shell` | Opens the toolbox container (terraform, kubectl, helm, kind, trivy, locust, cosign) so the host needs only git, make and Docker Engine. |

**Non-Ubuntu note.** On Windows, run these from WSL2 Ubuntu or from inside the toolbox. A thin `bootstrap.ps1` only starts the toolbox container and contains no logic.

### 3.2 Targets

| Target | What it is | Purpose |
| --- | --- | --- |
| compose | Docker Compose with profiles: core, ci, tunnel, obs, chaos | Fastest path, daily development |
| kind | Kubernetes in Docker, deployed with the Helm chart | Learning and testing Kubernetes |
| k3s | Any Linux VM reachable over SSH (Vagrant box, VPS, cloud instance). A bootstrap script installs k3s, then the same Helm chart is deployed | The portable cluster |
| oci | Terraform creates the VCN, security rules and an Ampere A1 VM. cloud-init installs k3s, then it is identical to the k3s target | Cloud proof and arm64 proof |

kind and k3s share one deploy path (the Helm chart, later Argo CD). Only the way the cluster is created differs.

### 3.3 Design rules

1. **One chart, one values file per environment.** Environment differences live only in `config/<target>/values.yaml` and `*.tfvars`, never in templates.
2. **Everything external is a variable:** registry, hostname, ingress or gateway class, storage class, upstream LLM URL, database URL, object-store endpoint.
3. **Secrets enter through one interface:** `.env.local`, then a Kubernetes Secret, later SOPS or sealed-secrets.
4. **Idempotent.** Running `up` twice changes nothing. `down` then `up` converges to the same state.
5. **Deterministic data.** Alembic migrations, a seed script and a cached embedding-model volume for N1, so a fresh machine does not depend on luck.
6. **Offline-capable.** The upstream simulator replaces Groq, N16 runs as a container, and the tunnel and Vercel are optional.
7. **Architecture-neutral.** Multi-arch images and no host-architecture assumptions.
8. **Pinned versions.** Toolbox image plus `.tool-versions`; images pinned by digest in releases.
9. **Enforced in CI.** A lint step fails on hardcoded registry hostnames, IP addresses or `latest` tags in manifests (conftest or grep first, Kyverno later).

### 3.4 External edges register (`docs/external-edges.md`)

| Edge | Used for | Required to run? | Fallback |
| --- | --- | --- | --- |
| Groq API | N5 LLM calls | No | `upstream-sim` (default in CI and tests). A real key is only for demos |
| Vercel (N16) | Public UI | No | N16 container in the stack |
| Cloudflare Tunnel | Public path from Vercel to N18 | No | Gateway or load balancer on cloud, port-forward locally |
| GitHub | Source and PRs | Dev only | Any git remote; Jenkins polls any URL |
| Image registry | Images | Yes | Local `registry:2` by default; GHCR or OCIR via variable |
| OCI | Cloud proof | No | k3s on any VM |

### 3.5 Time budgets

- compose: 10 min or less from a fresh Ubuntu clone with images pulled.
- kind: 15 min or less.
- k3s on a fresh VM: 20 min or less.
- oci: infrastructure in 5 min or less (original KPI), app healthy in 15 min or less in total.
- **Done means:** a second person, or you on a wiped Ubuntu machine, follows only `docs/bring-up.md` and succeeds without asking a question.

### 3.6 Clean-room ritual (2 h, last week of every month)

Fresh clone into a fresh Ubuntu VM (Vagrant or any new VM), then `make doctor`, `make up`, `make verify`, `make down`. Record the time and every failure in `docs/ephemeral-infra-log.md`. A failure is fixed in the scripts or docs, never only on the machine.

## 4. Timeline at a glance

| Month | Phase | Theme | Exit criterion | Targets working |
| --- | --- | --- | --- | --- |
| Aug 2026 | 0 | Baseline | Benchmarks and audit committed | Monolith |
| Sep–Oct 2026 | 1 | Docker, N1 extraction, local DB | Compose stack healthy | compose (Ubuntu dev machine) |
| Nov 2026 | 2 | Local CI, clean-room VM, bring-up v0 | Red PR blocked; green merge pushes amd64+arm64 images | compose in clean-room Ubuntu VM |
| Dec 2026 | 3 | Tunnel, simulator, load and chaos | Failure reproducible with one command; postmortem | compose + tunnel |
| Jan 2027 | 4 | Resilience: breaker, async, metrics | /health survives the 429 storm; before/after charts | compose |
| Feb 2027 | 5 | Kubernetes core | Stack on kind; rollback proven; UI works end to end | + kind (raw manifests) |
| Mar 2027 | 6 | Helm chart and Terraform | `terraform apply` rebuilds the cluster and deploys the chart | kind via Helm and Terraform |
| Apr 2027 | 7 | Network, gateway, k3s target | Denied connections proven; k3s VM bring-up works | + k3s |
| May 2027 | 8 | Observability, SLOs, scaling | Alert fires during a Locust run | all, with obs |
| Jun 2027 | 9 | OCI foundations | VCN, IAM, VM and k3s created and destroyed by Terraform | + oci (infra) |
| Jul 2027 | 10 | OCI deployment, portability proof | Same chart runs unchanged on kind, k3s and OCI | oci full |
| Aug 2027 | 11 | CD sprint: GitOps, secrets, supply chain | Merge to main deploys with no manual step; policy rejects a bad image | all via Argo CD |
| Sep 2027 | 12 | Developer experience and tracing | CLI scaffolds a module; trace spans N18 to N1 | all |
| Oct 2027 | 13 | Reliability: DR and game days | Restore drill passes with timings | all |
| Nov 2027 | 14 | Freeze and publish | Docs, posts, demo, resumes done | all |
| Dec 2027 | 15 | Anywhere gauntlet and v1.0 | Fresh clone to healthy on every target, timed | all, tagged v1.0 |

## 5. Status: Phases 0 and 1 (Aug–Oct 2026)

Tick what is actually done; anything unticked moves into November week 1.

- [x] Phase 0: `benchmarks/results/2026-08-baseline.json`, `docs/architecture-as-is.md`, `docs/highlights.md`, hypothesis about synchronous Groq calls, INC-001 (Groq model deprecation).
- [x] Phase 1: N1 extracted as a service; multi-stage Dockerfiles for N18, N1 and N16; Compose with healthchecks and a pgvector Postgres; Supabase migrated away; `.env.example`; `scripts/pg_dump_cron.sh`; network diagram; `docs/n1-embed-api.md`; ADRs 0000 to 0007.
- [ ] **Known gaps to close in November week 1:** Alembic migrations plus a seed script, a cached model volume for N1, Compose profiles, a configurable upstream URL for N5.

## 6. Month-by-month plans

- [roadmap-phases-2-7.md](roadmap-phases-2-7.md) — Phase 2 (Nov 2026) through Phase 7 (Apr 2027)
- [roadmap-phases-8-15.md](roadmap-phases-8-15.md) — Phase 8 (May 2027) through Phase 15 (Dec 2027)

## 7. Appendices

See [roadmap-appendices.md](roadmap-appendices.md) for:

- Appendix A: KPI dashboard
- Appendix B: Planned ADRs
- Appendix C: Risk register
- Appendix D: Volatile facts to re-verify at each phase start

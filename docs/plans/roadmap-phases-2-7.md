# Phase 2–7: Month-by-Month Plans

[← Back to roadmap index](roadmap.md)

## Phase 2: Nov 2026 — Local CI and Bring-up Contract v0

**Goal.** Self-hosted CI that gates every change, plus the first working `make up` in a clean-room Ubuntu VM.

**Exit.** A PR cannot merge red. A green merge produces versioned amd64+arm64 images in the local registry. `make up TARGET=compose` works inside a fresh Ubuntu Vagrant VM.

- **Week 1 (10 h).** Close the Phase 1 gaps: Alembic, seed, model cache, Compose profiles, upstream URL variable (5 h). Set up Vagrant with libvirt or VirtualBox on Ubuntu; pick the provider, write down why (1 h). `Vagrantfile` plus bootstrap script so `vagrant up` yields a healthy Compose stack on Ubuntu (3 h). Log the first rebuild time (1 h).
- **Week 2.** Makefile with `doctor`, `up`, `down`, `verify` for the compose target (3 h). Jenkins as a container inside the VM, configured as code (JCasC plus a plugin list) (4 h). Local `registry:2` and ADR-0015 (1 h). Multibranch pipeline using the GitHub Branch Source plugin: it only needs outbound access (polling, status posted back), so no inbound webhook is required (2 h).
- **Week 3.** `ruff`, `eslint`, `prettier` gates (2 h). Contract tests (3 h). Four or more smoke tests in `tests/smoke/` (3 h). BuildKit layer caching (1 h). Branch protection note: required status checks on private repos need a paid GitHub plan, so keep the repo public or enforce the gate by convention plus the Jenkins status (1 h).
- **Week 4.** `trivy` gate with an allowlist file (2 h). `buildx` multi-arch for N18 and N1; arm64 under QEMU is slow, so cache aggressively (3 h). Push `sha-<short>` tags and semver tags on release (2 h). Clean-room run and log (2 h). Runbook v1 (1 h).

**Tiers.** M: Vagrant bring-up, Jenkins as code, Jenkinsfile with all gates, multi-arch push, smoke tests. S: BuildKit cache, trivy allowlist, timing in `make verify`. X: split Jenkins agents, SBOM generation early.

**Docs.** ADR-0007 (Jenkins over GitHub Actions; Jenkins runs as a container and the Ubuntu VM is the clean room), ADR-0014 (Anywhere Contract and Makefile as the single interface), ADR-0015 (local registry as default), `docs/deployment-runbook.md` v1, `docs/bring-up.md` v0, `docs/external-edges.md` v1.

**Anywhere checkpoint.** compose works in a clean-room Ubuntu VM.

---

## Phase 3: Dec 2026 — Tunnel, Simulator, Load and Chaos

**Goal.** A public live deployment, then reproduce the Groq rate-limit failure on demand and write it up.

**Exit.** `make chaos SCENARIO=429-storm` reproduces thread exhaustion with recorded numbers. A blameless postmortem exists.

**Decision first (ADR-0017).** A named Cloudflare Tunnel needs a domain on Cloudflare (about $10/year, the only paid item in the plan). The free path is a quick tunnel, which gives a random `trycloudflare.com` URL that changes each time it starts; a small script then updates the Vercel environment variable and redeploys. Pick one and write down why.

- **Week 1.** Build `upstream-sim`: a FastAPI container that imitates Groq with configurable latency, a token bucket approximating the 8K TPM limit, `429` with `Retry-After`, and an admin endpoint to inject faults (5 h). Point N5 at it through the env variable (1 h). Tunnel Compose profile and Vercel connection, including CORS for the Vercel origin (4 h). ADR-0016.
- **Week 2.** Deploy stage in the Jenkinsfile (pull and `compose up` in the Ubuntu VM) and token rotation in the runbook (4 h). `loadtests/locustfile.py` with the 70/20/10 mix (4 h). Baseline run at low load, record p50/p95 (2 h).
- **Week 3.** Ramp users until uvicorn threads are exhausted: `/health` stalls, 429 count climbs (3 h). Chaos scenarios: kill the database container mid-request, inject latency (Toxiproxy is a simple container-based option), kill uvicorn workers (5 h). One low-volume validation run against real Groq to confirm the simulator behaves like the real thing (2 h, X).
- **Week 4.** Restore from a cron-generated backup and time it (2 h). Postmortem `docs/incidents/2026-12-n5-429-storm.md` (3 h). `docs/local-infra-disruption-runbook.md` (2 h). Record baselines in `highlights.md` (1 h). Clean-room run (2 h).

**Tiers.** M: simulator, tunnel with live deploy, locustfile, storm reproduced, postmortem, restore test. S: Toxiproxy scenarios beyond the first two, Vercel update script. X: real-Groq validation run.

**Anywhere checkpoint.** compose with the `tunnel` and `chaos` profiles; the stack runs with no real API key.

---

## Phase 4: Jan 2027 — Resilience

**Goal.** Fix the failure found in December, with evidence.

**Exit.** During the storm test `/health` stays under 200 ms at p95, user-visible failures drop below 5% of requests (degraded answers are counted separately), and before/after charts are committed.

- **Week 1.** ADR-0012: the finite-state machine (Closed, Open, Half-Open), failure threshold, rolling window, open timeout, half-open probe count, fallback chain (model names live in config), and a bulkhead (a semaphore limiting concurrent upstream calls) (3 h). Implement the breaker as a pure class with an injectable clock in `n5/breaker.py` (6 h). Re-check model names (1 h).
- **Week 2.** Make the N5 path async with `httpx.AsyncClient`, explicit timeouts and the bulkhead, so a slow upstream cannot occupy the default threadpool (5 h). Honor `Retry-After`: a 429 moves to the next provider and holds that provider's breaker open for the stated time (3 h). Final fallback is a fast degraded response, not a hang (2 h).
- **Week 3.** Unit tests for state transitions with a fake clock (3 h). `tests/integration/test_provider_chain_concurrency.py` using the simulator (3 h). `/metrics` with request latency histogram, status counter, breaker-state gauge, upstream-429 counter, in-flight gauge (3 h). Structured JSON logs with a request ID (1 h).
- **Week 4.** Re-run the December Locust test, generate before/after charts from the Locust CSVs with a script (3 h). Verify `/health` under storm (1 h). Add a protected admin endpoint to reset the breaker and update the `high-429-rate` runbook (2 h). Highlights and clean-room run (4 h).

**Tiers.** M: breaker with tests, async path, `/metrics`, before/after charts. S: Retry-After handling, structured logs, admin reset. X: per-provider adaptive thresholds.

**Docs.** ADR-0012, `docs/runbooks/high-429-rate.md`, `docs/highlights.md` with the headline numbers.

**Anywhere checkpoint.** compose with the breaker and metrics; `make verify` also checks `/metrics`.

---

## Phase 5: Feb 2027 — Kubernetes Core

**Goal.** The whole stack runs on a local Kubernetes cluster with plain manifests, and you can undo a bad release.

**Exit.** The Vercel UI works end to end against `kind`. A deliberately bad release is rolled back with `kubectl rollout undo`. `make up TARGET=kind` works.

**Resource note.** Running the Vagrant Ubuntu VM, Docker Engine and `kind` together strains RAM. Stop the VM during Kubernetes work and run one stack at a time. Use one control-plane node and one worker.

- **Week 1.** `kind` cluster config with port mappings and a local registry connected to the cluster, so images come from the same registry as everywhere else (2 h). Namespaces `app` and `data`. Deployments, Services, ConfigMaps and liveness/readiness probes for N1 and N18 (5 h). ADR-0011: local registry versus `kind load` as the image strategy (3 h).
- **Week 2.** Postgres with pgvector as a StatefulSet with a PVC (4 h). Secrets created from `.env.local` by `make up` (2 h). N16 and `upstream-sim` as Deployments (2 h). Migrations and seed as a Job (2 h).
- **Week 3.** Expose N18 through a NodePort mapped by `kind` for now; the real gateway comes in April (1 h). Re-point the Cloudflare Tunnel from the Ubuntu Vagrant VM to the `kind` port (2 h). `make up|down|verify TARGET=kind` (4 h). Baseline Locust run on `kind` (3 h).
- **Week 4.** Rollback drill: ship a release with a failing readiness probe or a bad image tag, watch the rollout stall, run `kubectl rollout undo`, log the timings (3 h). Requests and limits tuned for the machine (2 h). Re-run the storm test on `kind` to confirm the breaker holds there (2 h). ADR-0008 and clean-room run (3 h).

**Tiers.** M: manifests for N18, N1, Postgres and N16, probes, Secrets, rollback drill, tunnel re-point, `make up` for kind. S: requests and limits, migrations as a Job, storm re-run. X: Kustomize overlay experiment, k9s.

**Docs.** ADR-0008, ADR-0011, `k8s/README.md`, network flow diagram v0, ephemeral log entry for `kind delete cluster` then `make up`.

**Anywhere checkpoint.** compose and kind both work from a fresh Ubuntu clone.

---

## Phase 6: Mar 2027 — Helm Chart and Terraform

**Goal.** One parameterized deploy artifact, and the cluster itself as code.

**Exit.** `kind delete cluster && terraform apply` rebuilds the cluster, deploys the chart and passes `make verify`, in 15 minutes or less, timed and logged.

- **Week 1.** Convert the manifests into `charts/travel-planner` with a `values.schema.json` (7 h). Values layering: base `values.yaml` plus `config/kind/values.yaml`, with nothing environment-specific in templates (2 h). ADR-0018: Helm versus raw manifests versus Kustomize (1 h).
- **Week 2.** Terraform layout `infra/modules/cluster` and `infra/modules/app` (a `helm_release`), with the kind, helm and kubernetes providers (3 h). Local state, git-ignored (1 h). `environments/local.tfvars` (1 h). ADR-0010: module boundaries (2 h). ADR-0019: Terraform versus OpenTofu; choose and record the reason (1 h). Slack for provider learning curve (2 h).
- **Week 3.** Make `make up TARGET=kind` call Terraform (3 h). CI gates: `helm lint`, `helm template` piped to `kubeconform`, and the hardcoded-values lint from rule 9 (4 h). Jenkins stage that renders the chart for every environment (2 h).
- **Week 4.** Destroy and rebuild loops until the time is stable, fixing every manual step you find (3 h). `docs/bring-up.md` v1 covering compose and kind (3 h). Clean-room run (2 h). Highlights (1 h). Spare (1 h).

**Tiers.** M: Helm chart, Terraform cluster and app modules, timed rebuild, CI lint gate. S: values schema, kubeconform, both ADRs. X: Terraform remote state in free object storage, `helm-unittest`.

**Anywhere checkpoint.** kind is fully reproducible from code on Ubuntu.

---

## Phase 7: Apr 2027 — Network, Gateway and the k3s Target

**Goal.** Enforce network boundaries, put a real gateway in front, and prove the same chart runs on a plain Ubuntu VM.

**Exit.** A connection that must be denied is shown failing, by an automated test. HTTPS works through the gateway. `make up TARGET=k3s` works on a fresh Ubuntu Vagrant VM.

**Check first.** (1) `kind`'s default CNI may not enforce NetworkPolicies; verify before relying on it, and if it does not, create the cluster with the default CNI disabled and install Cilium or Calico. k3s bundles a NetworkPolicy controller, but verify that too. (2) The community `ingress-nginx` project was announced for retirement in early 2026; verify its current status and prefer the Gateway API with an implementation such as Envoy Gateway, Traefik or Cilium for new work.

- **Week 1.** Default-deny policy per namespace, plus explicit allows: gateway to N18, N18 to N1, N18 to the database, N18 to upstream, DNS egress (6 h). Automated `tests/network/` job that runs should-fail and should-pass connections (3 h). ADR-0021: CNI choice (1 h).
- **Week 2.** Gateway API CRDs, the chosen implementation, and HTTPRoutes for N18 and N16 (5 h). TLS with cert-manager and a local CA issuer; real ACME only if you own a domain (3 h). ADR-0020 (2 h).
- **Week 3.** `bootstrap/k3s-node.sh` that installs k3s, writes the kubeconfig and installs the chart; it must run on any Ubuntu VM (5 h). `Vagrantfile.k3s` for the clean-room Ubuntu VM (2 h). `make up TARGET=k3s HOST=...` (3 h).
- **Week 4.** Run `make verify` on k3s and fix every hidden assumption it reveals (storage class, gateway class, registry address) (4 h). ADR-0022: k3s as the portable target (1 h). `docs/bring-up.md` v2 (compose, kind, k3s) (1 h). Clean-room run on all three (2 h). Network diagram with namespaces and pod boundaries (2 h).

**Tiers.** M: default-deny with allows, failing-connection proof, gateway and HTTPRoutes, working k3s target. S: cert-manager TLS, automated network tests. X: Cilium Hubble flow visualization, L7 policy.

**Anywhere checkpoint.** compose, kind and k3s all work from Ubuntu.

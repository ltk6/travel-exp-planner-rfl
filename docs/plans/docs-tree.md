# Documentation Tree

Planned structure for the Aug 2026 – Dec 2027 platform roadmap. Checkboxes reflect files that exist on disk today.

Legend: `[x]` = exists | `[ ]` = planned

```text
/
├── [x] README.md                                  # Top-level entry point, system summary, zero-cost statement, demo video link
├── [ ] ARCHITECTURE.md                            # (Phase 14) C4-style architecture, hub-and-spoke rationale, ADR index
├── [ ] PLATFORM.md                                # (Phase 12) Golden-path index, links to runbooks and dashboards
├── [ ] CHANGELOG.md                               # (Phase 15) Release history
├── [x] .env.example                               # (Phase 1) All required env var keys, no values — secrets baseline
├── [ ] Makefile                                   # (Phase 2) doctor, up, down, verify, shell targets
├── [ ] .tool-versions                             # (Phase 2) Pinned tool versions (asdf/mise)
│
├── docs/
│   ├── [x] highlights.md                          # (Phase 0–15) Living log of metrics, achievements, decisions
│   ├── [ ] openapi.json                           # (Phase 14) Auto-generated FastAPI OpenAPI spec
│   ├── [x] architecture-as-is.md                  # (Phase 0) Baseline snapshot of the monolithic architecture
│   ├── [x] network-diagram.md                     # (Phase 1) Docker Compose network topology and routing
│   ├── [x] n1-embed-api.md                        # (Phase 1) API contract for the extracted N1 microservice
│   ├── [ ] deployment-runbook.md                  # (Phase 2) Vagrant provisioning, Cloudflare Tunnel config, credential rotation
│   ├── [ ] ephemeral-infra-log.md                 # (Phase 2–15) Log of time and failure points for clean-room teardowns
│   ├── [ ] external-edges.md                      # (Phase 2) Registry of external dependencies and fallbacks
│   ├── [ ] bring-up.md                            # (Phase 2) v0; updated at Phase 6 (v1), Phase 7 (v2), Phase 14 (final)
│   ├── [ ] volatile-facts.md                      # (Phase 2–15) Re-verified tooling facts per phase
│   ├── [ ] slo.md                                 # (Phase 8) SLI and SLO definitions
│   ├── [ ] anywhere-matrix.md                     # (Phase 10) All capabilities by target with status and timing
│   ├── [ ] dr-drill.md                            # (Phase 13) DR drill procedure and timing results
│   ├── [ ] golden-path-metrics.md                 # (Phase 12) Manual baseline vs CLI-assisted time-to-first-deploy
│   ├── [ ] retrospective.md                       # (Phase 15) What worked, what to change
│   │
│   ├── incidents/
│   │   ├── [x] 2026-08-27-groq-model-deprecation.md      # (Phase 0) INC-001: Groq deprecated primary LLM chain models
│   │   ├── [x] 2026-08-27-git-leftover-files-build-failure.md  # (Phase 0) Build failure from leftover git artifacts
│   │   └── [ ] 2026-12-n5-429-storm.md                   # (Phase 3) Blameless postmortem for the Locust load test failure
│   │
│   ├── adrs/
│   │   ├── [x] 0000-use-ai-for-development.md
│   │   ├── [x] 0001-record-architecture-decisions.md
│   │   ├── [x] 0002-use-hub-and-spoke-topology.md
│   │   ├── [x] 0003-n1-only-extracted-spoke.md            # (Phase 1)
│   │   ├── [x] 0004-http-rest-over-grpc.md                # (Phase 1)
│   │   ├── [x] 0005-use-docker-compose.md                 # (Phase 1)
│   │   ├── [x] 0006-env-secrets-management.md             # (Phase 1)
│   │   ├── [x] 0007-jenkins-over-github-actions.md        # (Phase 2)
│   │   ├── [ ] 0008-kind-vs-cloud-managed-cluster.md      # (Phase 5)
│   │   ├── [ ] 0009-hpa-target-metric-choice.md           # (Phase 8)
│   │   ├── [ ] 0010-terraform-module-boundaries.md        # (Phase 6)
│   │   ├── [ ] 0011-container-image-loading-strategy.md   # (Phase 5)
│   │   ├── [ ] 0012-circuit-breaker-fsm-design.md         # (Phase 4)
│   │   ├── [ ] 0013-scaffolding-cli-over-portal.md        # (Phase 12)
│   │   ├── [ ] 0014-anywhere-contract-makefile.md         # (Phase 2)
│   │   ├── [ ] 0015-local-registry-as-default.md          # (Phase 2)
│   │   ├── [ ] 0016-upstream-simulator.md                 # (Phase 3)
│   │   ├── [ ] 0017-tunnel-strategy.md                    # (Phase 3)
│   │   ├── [ ] 0018-helm-over-raw-manifests.md            # (Phase 6)
│   │   ├── [ ] 0019-terraform-vs-opentofu.md              # (Phase 6)
│   │   ├── [ ] 0020-gateway-api-vs-ingress.md             # (Phase 7)
│   │   ├── [ ] 0021-cni-networkpolicy-enforcement.md      # (Phase 7)
│   │   ├── [ ] 0022-k3s-portable-target.md                # (Phase 7)
│   │   ├── [ ] 0023-slo-sli-definitions.md                # (Phase 8)
│   │   ├── [ ] 0024-oci-topology-iam.md                   # (Phase 9)
│   │   ├── [ ] 0025-gitops-layout-argocd.md               # (Phase 11)
│   │   ├── [ ] 0026-secrets-in-git-sops-sealed.md         # (Phase 11)
│   │   ├── [ ] 0027-supply-chain-policy.md                # (Phase 11)
│   │   ├── [ ] 0028-tracing-stack.md                      # (Phase 12)
│   │   ├── [ ] 0029-backup-rpo-rto.md                     # (Phase 13)
│   │   └── [ ] 0030-n5-extraction-decision.md             # (Phase 13)
│   │
│   ├── plans/
│   │   ├── [x] roadmap.md                         # Index: scope, ground rules, Anywhere Contract, timeline, phase 0-1 status
│   │   ├── [x] roadmap-phases-2-7.md              # (Phase 2–7) Month-by-month detail
│   │   ├── [x] roadmap-phases-8-15.md             # (Phase 8–15) Month-by-month detail
│   │   ├── [x] roadmap-appendices.md              # KPI dashboard, ADR list, risk register, volatile facts
│   │   ├── [x] backlog.md                         # Living sprint backlog (populated per active phase)
│   │   └── [x] docs-tree.md                       # This document
│   │
│   ├── runbooks/
│   │   ├── [ ] embedding-service-down.md          # (Phase 8) Troubleshooting steps when N1 fails
│   │   ├── [ ] high-429-rate.md                   # (Phase 4) N5 rate-limit response steps and circuit breaker reset
│   │   └── [ ] local-infra-disruption.md          # (Phase 3) DB drop and restore, latency injection, container kill
│   │
│   └── gamedays/                                  # (Phase 13) One file per game day with hypothesis, metrics, writeup
│
├── bootstrap/
│   ├── [ ] k3s-node.sh                            # (Phase 7) Installs k3s on any Ubuntu VM; reused by oci cloud-init
│   └── [ ] bootstrap.ps1                          # (Phase 2) Windows-only: starts toolbox container, no logic
│
├── toolbox/
│   └── [ ] Dockerfile                             # (Phase 2) All dev tools pinned; used by `make shell`
│
├── config/
│   ├── [ ] compose/                               # (Phase 2) Compose-target env and values
│   ├── [ ] kind/values.yaml                       # (Phase 6) Helm values for kind
│   ├── [ ] k3s/values.yaml                        # (Phase 7) Helm values for k3s
│   └── [ ] oci/values.yaml                        # (Phase 10) Helm values for OCI
│
├── charts/
│   └── [ ] travel-planner/                        # (Phase 6) Helm chart with values.schema.json
│
├── gitops/                                        # (Phase 11) GitOps repo layout (may be a separate repo)
│
├── upstream-sim/                                  # (Phase 3) FastAPI Groq simulator container
│
├── policies/                                      # (Phase 11) Kyverno policy manifests
│
├── tools/
│   └── [ ] travel-cli/                            # (Phase 12) CLI with new-spoke, lint-module, verify wrappers
│
├── templates/                                     # (Phase 12) Module scaffolding templates (Copier or cookiecutter)
│
├── scripts/
│   ├── [x] pg_dump_cron.sh                        # (Phase 1) Local Postgres/pgvector backup script
│   ├── [ ] doctor.sh                              # (Phase 2) Checks tool versions, RAM, disk, open ports
│   └── [ ] gauntlet.sh                            # (Phase 15) Runs full bring-up/verify/teardown on every target
│
├── infra/
│   ├── [ ] README.md                              # (Phase 6) Terraform module docs, environment variables
│   ├── modules/
│   │   ├── [ ] cluster/                           # (Phase 6) kind / k3s / OCI cluster provisioning
│   │   ├── [ ] network/                           # (Phase 7/9) VCN or NetworkPolicy segmentation
│   │   └── [ ] app/                               # (Phase 6) helm_release module
│   ├── environments/
│   │   ├── [ ] local.tfvars                       # (Phase 6) Local kind variables
│   │   └── [ ] oci.tfvars                         # (Phase 9) OCI Ampere A1 variables
│   └── [ ] oci/                                   # (Phase 9) OCI root Terraform module
│
├── k8s/
│   ├── [ ] README.md                              # (Phase 5) Manifest index, probe config, rollback procedure
│   └── [ ] *.yaml                                 # (Phase 5) Deployment, Service, StatefulSet, Job, Secrets manifests
│
├── loadtests/
│   └── [ ] locustfile.py                          # (Phase 3) 70% search / 20% activity gen / 10% feedback
│
├── tests/
│   ├── [ ] smoke/                                 # (Phase 2) 4+ integration smoke tests
│   ├── [ ] network/                               # (Phase 7) Should-fail and should-pass connection checks
│   ├── unit/
│   │   └── [ ] test_provider_fsm.py               # (Phase 4) Circuit breaker FSM state transition tests
│   └── integration/
│       └── [ ] test_provider_chain_concurrency.py # (Phase 4) Concurrent failure integration test
│
├── benchmarks/
│   └── results/
│       └── [x] 2026-08-baseline.json              # (Phase 0) p50/p95 latency reference point
│
├── notes/                                         # (Git-excluded) Personal scratchpads — do not edit
│
├── resumes/                                       # (Phase 14)
│   ├── [ ] resume-network.pdf
│   ├── [ ] resume-swe.pdf
│   └── [ ] resume-platform.pdf
│
└── demo/
    └── [ ] script.md                              # (Phase 14) Narration script for the final 6–9 minute demo video
```


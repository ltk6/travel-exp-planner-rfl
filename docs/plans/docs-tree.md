# Documentation Tree

Planned structure of documentation and deliverables for throughout the 10-month capstone project.

```text
/
├── README.md                                  # Top-level entry point, system summary, Zero-Cost Guarantee, demo video link
├── ARCHITECTURE.md                            # (Phase 8) C4-style architecture, hub-and-spoke rationale, ADR index
├── PLATFORM.md                                # (Phase 7) Golden-path index, links to runbooks and dashboards
├── .env.example                               # (Phase 1) All required env var keys, no values — secrets baseline
│
├── docs/
│   ├── highlights.md                          # (Phase 0–8) Living log of metrics, achievements, and decisions for resumes
│   ├── openapi.json                           # (Phase 8) Auto-generated FastAPI OpenAPI spec
│   ├── architecture-as-is.md                  # (Phase 0) Baseline snapshot of the monolithic architecture
│   ├── n1-embed-api.md                        # (Phase 1) API contract and details for the extracted N1 microservice
│   ├── deployment-runbook.md                  # (Phase 2) Vagrant provisioning, Cloudflare Tunnel config, credential rotation
│   ├── incident-2026-12-n5-429-storm.md       # (Phase 3) Blameless postmortem for the Locust load test failure
│   ├── ephemeral-infra-log.md                 # (Phase 2–8) Log of time & failure points for Vagrant/`kind` teardowns
│   ├── golden-path-metrics.md                 # (Phase 7) Manual baseline vs. CLI-assisted time-to-first-deploy comparison
│   │
│   ├── adrs/                                  # (Phase 0–8) Architecture Decision Records
│   │   ├── 0000-use-ai-for-development.md             # (Phase 0)
│   │   ├── 0001-record-architecture-decisions.md
│   │   ├── 0002-use-hub-and-spoke-topology.md
│   │   ├── 0003-n1-only-extracted-spoke.md            # (Phase 1)
│   │   ├── 0004-http-rest-over-grpc.md                # (Phase 1)
│   │   ├── 0005-compose-before-kubernetes.md           # (Phase 1)
│   │   ├── 0006-n1-fully-local.md                     # (Phase 1)
│   │   ├── 0007-secrets-management-strategy.md         # (Phase 1) .env → K8s Secrets → sealed-secrets path
│   │   ├── 0008-kind-vs-cloud-managed-cluster.md       # (Phase 4)
│   │   ├── 0009-hpa-target-metric-choice.md            # (Phase 4)
│   │   ├── 0010-terraform-module-boundaries.md         # (Phase 4)
│   │   ├── 0011-container-image-loading-strategy.md    # (Phase 4) kind load vs local registry
│   │   ├── 0012-circuit-breaker-fsm-design.md          # (Phase 6)
│   │   └── 0013-scaffolding-cli-over-portal.md         # (Phase 7)
│   │
│   ├── plans/
│   │   ├── roadmap.md                         # The 10-month capstone roadmap
│   │   └── docs-tree.md                       # This document
│   │
│   └── runbooks/
│       ├── embedding-service-down.md          # (Phase 5) Troubleshooting steps when N1 fails
│       ├── high-429-rate.md                   # (Phase 5/6) N5 rate-limit response steps & circuit breaker reset
│       └── local-infra-disruption.md          # (Phase 3) DB drop + restore, latency injection, container kill scenarios
│
├── scripts/
│   ├── pg_dump_cron.sh                        # (Phase 1) Local Postgres/pgvector backup script
│   └── kind-teardown.sh                       # (Phase 4) Ephemeral cluster teardown
│
├── infra/
│   ├── README.md                              # (Phase 4) Terraform module docs, `oci.tfvars` vs `local.tfvars`, image loading strategy
│   ├── modules/
│   │   ├── cluster/                           # (Phase 4) kind / OCI cluster provisioning
│   │   └── network/                           # (Phase 4) NetworkPolicy segmentation
│   └── environments/
│       ├── local.tfvars                       # (Phase 4) Local kind cluster variables
│       └── oci.tfvars                         # (Phase 4) OCI ARM64 Ampere A1 variables
│
├── k8s/
│   ├── README.md                              # (Phase 4) Manifest index, probe config, rollback procedure
│   └── *.yaml                                 # (Phase 4) Deployment, Service, Ingress, HPA, Secrets manifests
│
├── loadtests/
│   └── locustfile.py                          # (Phase 3) 70% search / 20% activity gen / 10% feedback
│
├── tests/
│   ├── smoke/                                 # (Phase 2) 4+ integration smoke tests
│   ├── unit/
│   │   └── test_provider_fsm.py               # (Phase 6) Circuit breaker FSM state transition tests
│   └── integration/
│       └── test_provider_chain_concurrency.py # (Phase 6) Concurrent failure integration test
│
├── benchmarks/
│   └── results/
│       └── 2026-08-baseline.json              # (Phase 0) p50/p95 latency reference point
│
├── notes/                                     # (Git-excluded) Study guides and learning materials
│   └── study-guide.md
│
├── resumes/                                   # (Phase 8)
│   ├── resume-network.pdf
│   ├── resume-swe.pdf
│   └── resume-platform.pdf
│
└── demo/
    └── script.md                              # (Phase 8) Narration script for the final 6–9 minute demo video
```
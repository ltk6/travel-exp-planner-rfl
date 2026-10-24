# Roadmap Appendices

[← Back to roadmap index](roadmap.md)

## Appendix A: KPI Dashboard

| Metric | Baseline | Target | Measured |
| --- | --- | --- | --- |
| p95 latency under load (kind) | Phase 0 benchmark | 30% or better improvement | May 2027 |
| User-visible failure rate in 429 storm | About 100% at peak (Dec 2026) | Under 5% (degraded answers counted separately) | Jan 2027 |
| `/health` p95 during storm | Stalls (Dec 2026) | Under 200 ms | Jan 2027 |
| Contract-covered boundaries | Existing | 100% enforced in CI | Nov 2026 |
| Decision records | 7 (ADR-0000 to 0006) | 30 or more (ADR-0000 to 0030) | Nov 2027 |
| Core backend test coverage | Unmeasured | 70% or more | Nov 2027 |
| Reconstruction time logged | 0 | One per phase from Phase 2 | Monthly |
| Bring-up time, compose | Not measured | 10 min or less | Dec 2027 |
| Bring-up time, kind | Not measured | 15 min or less | Dec 2027 |
| Bring-up time, k3s on fresh Ubuntu VM | Not measured | 20 min or less | Dec 2027 |
| OCI infrastructure spin-up | N/A | 5 min or less (app healthy in 15 min or less) | Jul 2027 |
| Time to first green CI run | N/A | Quantified reduction vs manual | Nov 2026 |
| Golden path: CLI vs manual deploy | Manual baseline (Sep 2027) | At least 50% faster | Sep 2027 |
| DR drill | None | RTO and RPO stated and met (example: 60 min and 24 h) | Oct 2027 |
| Second-person bring-up with docs only | N/A | Succeeds with no questions | Dec 2027 |
| Monthly infrastructure spend | $0 | $0 | Monthly |

## Appendix B: Planned ADRs

Numbers 0000 to 0007 are done. Planned from here (renumber freely if the order changes):

- 0014 Anywhere Contract and Makefile as the single interface (Nov 2026)
- 0015 Local registry as default (Nov 2026)
- 0016 Upstream simulator for N5 (Dec 2026)
- 0017 Tunnel strategy: named tunnel with a domain, or quick tunnel (Dec 2026)
- 0012 Circuit breaker FSM, bulkhead and fallback chain (Jan 2027)
- 0008 kind versus managed cluster (Feb 2027)
- 0011 Image strategy: local registry versus `kind load` (Feb 2027)
- 0018 Helm over raw manifests and Kustomize (Mar 2027)
- 0010 Terraform module boundaries (Mar 2027)
- 0019 Terraform versus OpenTofu (Mar 2027)
- 0020 Gateway API versus an ingress controller (Apr 2027)
- 0021 CNI and NetworkPolicy enforcement (Apr 2027)
- 0022 k3s as the portable cluster target (Apr 2027)
- 0023 SLO and SLI definitions (May 2027)
- 0009 HPA target metric (May 2027)
- 0024 OCI topology and IAM (Jun 2027)
- 0025 GitOps layout and Argo CD (Aug 2027)
- 0026 Secrets in git: SOPS or sealed-secrets (Aug 2027)
- 0027 Supply-chain policy (Aug 2027)
- 0013 Scaffolding CLI over a portal (Sep 2027)
- 0028 Tracing stack (Sep 2027)
- 0029 Backup, RPO and RTO (Oct 2027)
- 0030 N5 extraction decision (Oct 2027)

If a month is tight, fold small ADRs into larger ones before skipping them.

## Appendix C: Risk Register

| Risk | Mitigation |
| --- | --- |
| Ubuntu host RAM and CPU exceeded by VM, Docker Engine, kind and monitoring together | Run one stack at a time; set requests and limits early; trim Prometheus; use one control-plane and one worker |
| Vagrant provider incompatible with host Ubuntu kernel | Test with libvirt first; fall back to VirtualBox; document the choice in Nov week 1 |
| No buffer months, so slippage compounds | Tiers: M moves forward, X then S are dropped; weeks under 5 h do only M work and are logged |
| Tunnel drops or the quick-tunnel URL changes | Port-forward fallback; a script that updates the Vercel variable; the demo uses local N16 |
| OCI A1 capacity unavailable | Retry script; pay-as-you-go upgrade inside free limits with a budget alert; k3s on Vagrant as the fallback proof |
| OCI reclaims an idle instance or limits change | Re-check rules (Appendix D); prefer apply and destroy per session; keep Terraform always ready |
| Tooling churn (ingress controller retirement, licensing changes) | Phase-start volatile-facts check; every choice recorded in an ADR |
| Groq changes models or limits | Model names only in config; the simulator keeps tests stable |
| A secret leaks into git or an image | `.env.local` git-ignored; add a secret scanner such as gitleaks to Jenkins; SOPS in August |
| Scope creep, especially the CLI and the optional extraction | One template only; no product features after Phase 0 |
| Hidden environment assumptions break the Anywhere promise | Monthly clean-room run on Ubuntu; hardcode lint in CI; the December gauntlet |
| Burnout from a 14-month run next to studies and work | 10 h/week is a ceiling, not a target; the weekly ritual is 1 h, not a deadline |
| Metrics drift between resumes, posts and docs | `docs/highlights.md` is the single source of truth |

## Appendix D: Volatile Facts to Re-verify at Each Phase Start

Record the result of each check in `docs/volatile-facts.md` with the date.

- Groq: current models, rate limits (8K TPM chain), deprecations.
- GitHub: branch protection availability for private repos; Actions and registry limits.
- Terraform and OpenTofu: licensing and provider compatibility.
- kind: whether the default CNI enforces NetworkPolicies; the local-registry setup pattern.
- Ingress: status of the community ingress-nginx project; maturity of Gateway API implementations.
- Cloudflare: quick tunnel behavior and terms; named tunnel requirements.
- OCI: Always Free limits, A1 capacity, idle-instance reclamation, object storage allowance, OCIR availability.
- Let's Encrypt and sslip.io: rate limits.
- cosign: keyless prerequisites; Kyverno image verification syntax.
- Jenkins: LTS version and plugin compatibility.
- Ubuntu: LTS release version in use; kernel compatibility with chosen Vagrant provider.

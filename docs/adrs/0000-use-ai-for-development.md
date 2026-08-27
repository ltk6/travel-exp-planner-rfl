# 0. Use AI for Development and Documentation

**Date:** 2026-08-08
**Status:** Accepted

## Context

This project builds on a legacy monolith inherited from a prior multi-person capstone group. This phase extends that system solo, adding two new tracks — network infrastructure and DevOps automation — on top of the existing software work. One engineer now owns all design, implementation, and documentation across three distinct domains.

The original scope was sized for a full team. AI is adopted as a productivity multiplier to close that capacity gap. The developer retains full ownership of architecture decisions and engineering judgment; AI accelerates execution, not decision-making.

## Decision

Use AI assistance across backend, frontend, and documentation tasks.

- **Backend:** AI co-writes code to increase productivity.
- **Frontend:** AI generates and maintains the UI so the developer focuses on architecture.
- **Documentation:** AI writes and enforces standard structure/style per `AGENTS.md`. Learning how to orchestrate a complex, multi-person team documentation process is out-of-scope and a poor use of time for a solo developer. AI entirely abstracts away this choreography.

## Consequences

- **Positive:** Development speed increases across all tracks.
- **Positive:** Developer attention stays on architecture, infrastructure, and review.
- **Positive:** Eliminates the mental overhead and wasted effort of simulating a team-level documentation process as a solo developer.
- **Negative:** AI output quality is inconsistent; logic errors and outdated patterns require active catch.
- **Negative:** Review overhead partially offsets the productivity gain. All AI output requires manual review against `AGENTS.md` before merging.

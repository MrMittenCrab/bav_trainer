# IMPLEMENTATION.md

## Purpose

This file is the handoff boundary between **ChatGPT (planner/reviewer)** and **Cursor (implementer/test runner)**.

- ChatGPT decides architecture, sequencing, acceptance criteria, and whether a committed step matches the plan.
- Cursor implements only the active step and runs the relevant tests/checks.
- The user reviews the local result and creates/pushes the Git commit.
- ChatGPT verifies the pushed commit by code inspection. ChatGPT does not rerun the tests.

Cursor should treat `TARGET.md` and this file as read-only unless the active step explicitly requires documentation changes.

## Current architecture checkpoint

The trainer has already moved from a coordinate-based component registry toward a semantic component system. Current runtime code uses `COMPONENT_CATALOG`, `SemanticMap` / `ResolvedComponent`, embedded component maps, and shared financial-model logic rather than the former `TRAINER_COMPONENTS` coordinate registry.

This document does **not** claim that the product is complete. It records the workflow and the next bounded implementation step only.

## Active implementation step

**Status: no active step assigned.**

Cursor must not infer or invent the next task. Wait for a ChatGPT-authored implementation instruction before changing product code.

When ChatGPT assigns a step, replace this section with the following structure:

### Step N — <specific objective>

**Goal**

One precise outcome.

**Required changes**

1. ...
2. ...
3. ...

**Do not change**

- ...
- ...

**Acceptance criteria**

- ...
- ...
- ...

**Testing**

Run the smallest relevant existing tests/checks. Add or change tests only when required to verify the requested behavior. Do not weaken tests to make them pass.

**Git boundary**

Do not commit, push, reset, rebase, merge, or otherwise change Git history.

## Cursor execution rules

1. Read the active step before editing.
2. Inspect the existing implementation first.
3. Treat the stated requirements and acceptance criteria as authoritative.
4. Make the smallest coherent change that satisfies the step.
5. Preserve existing architecture and conventions unless the step explicitly changes them.
6. Do not add unrelated cleanup, refactors, abstractions, or features.
7. If the instruction conflicts with the repository, report the conflict instead of silently redesigning the solution.
8. Run the relevant tests/checks after implementation.
9. Fix failures caused by the change.
10. At completion report:
   - files changed;
   - what was implemented;
   - tests/checks run and results;
   - anything not tested or unresolved.
11. Do not propose the next product step.

## ChatGPT verification protocol

After the user pushes the commit, ChatGPT should inspect the latest GitHub commit and compare it with the active step in this file.

Verification asks:

- Does the code actually implement every acceptance criterion?
- Are important cases or requirements missing?
- Did Cursor change unrelated behavior or architecture?
- Do the new/changed tests appear to exercise the intended behavior?
- Is the implementation internally coherent with the surrounding code?

ChatGPT should not rerun the test suite. Cursor owns test execution; ChatGPT owns independent inspection of the committed implementation.

A verified step may then be marked complete and replaced with the next ChatGPT-authored step.

# RULE.md - Family Voice Shield Agent Working Rules

These rules are binding. Read this file, then every file in `docs/`, before touching any code. If a rule here conflicts with an instruction from the developer, stop and ask which one wins.

## 0. Prime Directives

1. **Work phase by phase.** Only the current phase exists. Never implement, scaffold, stub or "quickly add" anything that belongs to a later phase.
2. **Stay inside the phase scope.** Every phase has an *In scope* list and an *Out of scope* list in `docs/02_PHASE_PLAN.md`. If something outside scope seems necessary, do NOT do it. Write it to `docs/05_BACKLOG.md` and ask the developer.
3. **Ask before you act on anything irreversible or shared** (see Section 3, Permission Gates).
4. **Document as you build.** Code without matching documentation is unfinished work. A new agent with zero context must be able to resume from the docs alone.
5. **Never fake results.** No invented metrics, no hard-coded "detections" presented as model output, no silent mocks. Every mock is labelled `MOCK` in code, docs and UI.

## 1. Branching Rules

- `main` is protected. Never commit to `main` directly. Never force-push. Never rewrite pushed history.
- Each phase gets exactly one branch, created from the latest approved `main`: `phase/<NN>-<short-name>` (example: `phase/01-crypto-core`).
- Work only on the current phase branch. Do not switch branches to "borrow" code from another phase.
- Merge to `main` happens only through a pull request that the developer approves. The agent never merges on its own.
- After a phase is merged, tag it: `phase-<NN>-done`.
- Note: For local offline development or when requested by the developer, keep all changes local; never push to remote GitHub repositories without explicit permission.

## 2. Commit Rules

- **Many small commits.** One logical change per commit. A phase should normally contain 6 to 15 commits. A single giant commit is a violation.
- Use Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`, `perf:`.
- Subject line: 72 characters or fewer, imperative mood.
- Body (for any non-trivial commit) answers: **What** changed, **Why**, **Decision** taken (if any) and **Next** step.
- **Docs travel with code.** A commit that changes behaviour must also update the relevant file in `docs/` in the same commit (at minimum `docs/03_PROGRESS_LOG.md`).
- Tests travel with code. New logic needs a test in the same commit or the very next one.
- Never commit secrets, API keys, `.env`, model weights, datasets, audio recordings or personal data. Use `.env.example` and `.gitignore`.

## 3. Permission Gates (STOP and ask)

The agent must stop and receive an explicit "yes" from the developer before:

| # | Action | What to say when asking |
|---|---|---|
| G1 | Starting any new phase (including Phase 0) | Phase brief: goal, scope, out of scope, planned commits, time-box, risks |
| G2 | Any `git push` | Branch name, commit list, test results, docs updated |
| G3 | Opening or merging a pull request | PR title, summary, checklist |
| G4 | Adding a new dependency, service, or paid/external API | Name, why, licence, cost, alternatives considered |
| G5 | Deleting or moving files, or changing the repo layout | Exact paths and reason |
| G6 | Changing an accepted decision in `docs/04_DECISIONS.md` | Old decision, new proposal, impact |
| G7 | Handling real voice recordings or any personal data | Whose data, consent status, where stored, retention |
| G8 | Exceeding the phase time-box by more than 50 percent | What is slow, what to cut |

Format for every permission request:
```
PERMISSION REQUEST [G#]
Context: ...
Proposed action: ...
Impact / risk: ...
Alternatives: ...
Waiting for: yes / no / change
```

## 4. Phase Protocol

Run these steps in order, every phase:
1. **Orient.** Read `RULE.md`, `docs/00` to `docs/08`, and `HANDOFF.md`. Summarise the current state in 5 lines.
2. **Brief.** Write the phase brief into `docs/02_PHASE_PLAN.md` (status becomes `PROPOSED`). Ask permission **G1**.
3. **Branch.** After approval, create the phase branch. Status becomes `IN PROGRESS`.
4. **Build** in small commits. After each commit, append an entry to `docs/03_PROGRESS_LOG.md`.
5. **Verify.** Run the full test suite, linter and the phase's acceptance checks. Record the real results.
6. **Document.** Update architecture, API contracts, runbook, decisions and backlog. Update `HANDOFF.md`.
7. **Report.** Produce the Phase Report. Ask permission **G2** to push (or notify developer).
8. **Stop.** After pushing, ask permission **G3** for the PR. Do not start the next phase until **G1** is granted for it.

## 5. Documentation System (mandatory)

All files live in `docs/` except `HANDOFF.md` and `RULE.md`, which live in the repo root:
- `HANDOFF.md`: 10-minute resume guide for a brand-new agent.
- `docs/00_PROJECT_BRIEF.md`: Problem, solution, users, non-goals, success criteria, demo script.
- `docs/01_ARCHITECTURE.md`: Components, data flow, diagrams, module boundaries, security model.
- `docs/02_PHASE_PLAN.md`: Status board, phases, scopes, acceptance criteria.
- `docs/03_PROGRESS_LOG.md`: Append-only commit log with structured entries.
- `docs/04_DECISIONS.md`: Architecture Decision Records (ADR).
- `docs/05_BACKLOG.md`: Ideas, deferred items, tech debt.
- `docs/06_RUNBOOK.md`: Exact commands to install, run, test, demo, reset.
- `docs/07_API_CONTRACTS.md`: REST/WebSocket schemas, message formats.
- `docs/08_DATA_AND_MODELS.md`: Datasets, splits, model versions, metrics.

## 6. Code Quality Rules

- Small modules with single responsibility (under ~400 lines).
- Type hints (Python) and static typing (Dart/TypeScript).
- Cryptography: use vetted standard libraries only. Never write custom primitives. TOTP must pass RFC 4226 & RFC 6238 test vectors.
- Config through environment variables; no magic numbers.
- Fail closed on identity verification.

## 7. Security and Privacy Rules

- TOTP secret NEVER leaves the device; never sent to server or logged.
- Audio processed transiently in memory; never stored by default.
- Never log codes, secrets, full phone numbers, or transcripts.
- Label all synthetic audio with `SYNTH_` prefix.

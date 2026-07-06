# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Add a Scheduler.find_next_available_slot() method that finds the earliest open time slot for a pet based on existing tasks, reuse the same overlap logic already used for conflict detection, add a test for it, and add a quick demo call to main.py.

**What did the agent do?**

- Modified pawpal_system.py to add find_next_available_slot(), plus a shared overlap helper used by detect_conflicts().
- Added a regression test in tests/test_pawpal.py covering a simple overlap case.
- Updated main.py to print a sample next-available-slot result from the demo data.
- Ran pytest and the main demo to verify the new behavior.

**What did you have to verify or fix manually?**

The first implementation returned the wrong slot because the test expectation was based on the wrong starting point, so I corrected the test to reflect the intended forward-search behavior from the provided after time. I also fixed main.py to unpack the tagged conflict tuples correctly after the scheduler’s detect_conflicts() method returned three values instead of two.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->

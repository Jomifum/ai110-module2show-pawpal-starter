# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I used four classes: Owner, Pet, Task, and Scheduler, plus a TaskType enum (feeding/walk/medication/appointment).

Owner and Pet are data-holding classes (implemented as dataclasses) that map to action 1 — registering pet and owner info. Owner also holds available_minutes_per_day, since action 3 needs a time budget to plan against.
Task is a dataclass representing one unit of care work — it holds duration_minutes and priority (1–5), which are exactly the two fields action 2 asked for.
Scheduler holds all the algorithmic behavior instead of Task or Owner, so the logic for sorting, conflict detection, and — most importantly — generate_daily_plan() lives in one testable place. I split this out specifically because action 3 isn't a simple sort; it's a constrained-selection problem (fit the highest-priority tasks into a limited time budget), which is different enough from "sort by priority" that it earns its own method.

**b. Design changes**

Initially I scaffolded a generic get_today_tasks() method, but re-reading my own action 3, I realized that's not enough — it just filters by date, it doesn't optimize anything. I added a separate generate_daily_plan() method to Scheduler and an available_minutes_per_day field to Owner so there's an actual time budget to plan against.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers three constraints: time (each task's `duration_minutes` and `scheduled_time`), priority (a 1–5 scale set per task), and a hard resource limit (`available_minutes_per_day` on Owner). I treated the time budget as the hard constraint — a plan can't exceed it, full stop — and priority as the optimization signal for deciding *which* tasks to keep when everything doesn't fit. Chronological order matters for display (so a plan reads naturally) but isn't itself a constraint on correctness. I decided the budget mattered most because it's the one constraint that's non-negotiable in real life: an owner genuinely cannot do 90 minutes of pet care in a 60-minute window, whereas priority is a judgment call that can flex.

**b. Tradeoffs**

`generate_daily_plan()` uses a greedy priority-per-minute heuristic (sort tasks by priority/duration density, take what fits in the budget) instead of an exact 0/1 knapsack solved with dynamic programming. Greedy is O(n log n) and easy to reason about; true DP knapsack would guarantee a mathematically optimal selection in every case, but at the cost of more code and memory for a problem that, in practice, rarely has more than a handful of candidate tasks per day. I verified with a hand-checked example that greedy produced the actual optimal answer for a realistic task set, and backed that with an automated test — but greedy is not *guaranteed* optimal for every possible input, only for the cases I checked. I judged that tradeoff reasonable here: a personal pet-care scheduler doesn't need provable global optimality, it needs a plan that's clearly sensible and easy to maintain.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI across the full range: design brainstorming (Phase 1's UML and class responsibilities), full-implementation agent-mode edits (Phase 2's method bodies, Phase 4's new algorithms touching multiple files at once), debugging (walking through why a test failed and whether the bug was in the test or the logic), and refactor review (asking whether `generate_daily_plan` could be simplified). I also kept planning conversations in separate chat sessions from implementation ones, one per phase, to keep each conversation focused.

The most helpful prompts weren't the ones that asked for code directly — they were the ones that forced a justification before code got written. Asking "how should Scheduler talk to Owner's pets, and why" before implementing anything settled a structural decision that would have been expensive to redo later. Similarly, asking for a literal, itemized list ("list every test function with what it asserts") rather than a summary consistently surfaced gaps that a one-line "tests passing" summary hid.

**b. Judgment and verification**

In Phase 5, after the AI proposed an 8-item test plan and then reported the suite as complete and passing, I asked it to list every test function with a one-line summary of what it actually asserted. That inventory revealed that 3 of the original 8 planned cases — filtering combinations, an unsupported-recurrence edge case, and an adjacent-tasks boundary case — had quietly been dropped between the plan and the implementation, even though the suite was reported as "passing" the whole time. Passing tests only prove what they actually test; they say nothing about what was silently left out. I verified this by refusing to accept "N tests passed" as sufficient evidence and instead comparing the original plan against the real file, line by line, before deciding what (if anything) was actually missing.

---

## 4. Testing and Verification

**a. What you tested**

The final suite (18 tests) covers: basic class behavior (`mark_complete`, pet/task counts), chronological sorting, filtering by pet and completion status (individually and combined), recurring task completion for both daily and weekly intervals plus unsupported recurrence patterns correctly producing no next instance, conflict detection for same-pet overlaps and cross-pet owner double-booking (both general overlaps and exact-duplicate-time cases), a boundary case confirming back-to-back tasks are *not* falsely flagged as conflicts, an empty-pet edge case, and a budget-respecting optimality check on `generate_daily_plan()`. These mattered because they're not incidental details — they're the specific promises the app makes to a pet owner (you won't get double-booked, a "daily plan" will actually respect your time, a recurring task won't silently disappear after you complete it once). Untested versions of any of these would mean the app could quietly fail at its core job.

**b. Confidence**

I'd put my confidence at 4/5. The core scheduling logic is thoroughly and specifically tested, including edge cases that were easy to overlook (adjacent non-conflicts, unsupported recurrence patterns). What's not covered: the Streamlit UI (`app.py`) has no automated tests, only manual browser verification; recurrence was only verified for a single completion cycle, not a chain of several consecutive completions; and conflict detection was only tested pairwise, not with three or more simultaneously overlapping tasks. If I had more time, those three would be next — especially a multi-cycle recurrence test, since a bug that only appears on the second or third occurrence would currently go undetected.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with `generate_daily_plan()` — it's the one piece of the system that isn't just "manage a list," it's a genuine constrained-optimization decision, and I have both a hand-verified example and an automated test confirming it picks the mathematically correct combination of tasks for a given time budget, not just a plausible-looking one.

**b. What you would improve**

I'd add automated tests for the Streamlit UI layer instead of relying on manual clicking, and I'd address data persistence — right now everything resets when the app restarts, which is a real limitation for something meant to manage a pet's *daily* routine over time, not a single session.

**c. Key takeaway**

The biggest thing I learned is that an AI reporting "done" or "tests passed" describes that something *ran*, not that it *did the right thing*. Across this project, several real gaps hid behind confident-sounding verification language: a leftover placeholder UI section that "worked" but wasn't actually connected to anything, a test plan that quietly shrank between being proposed and being implemented, and a "simplified" code suggestion that wasn't actually different from what I already had. None of these were the AI lying — they were completion and correctness drifting apart in ways that only showed up when I checked the actual file, the actual test list, or the actual diff instead of trusting the summary. Being the lead architect meant exactly that: treating every AI claim of success as something to verify, not something to build the next step on top of unchecked.

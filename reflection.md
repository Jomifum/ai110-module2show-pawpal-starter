# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I used four classes: Owner, Pet, Task, and Scheduler, plus a TaskType enum (feeding/walk/medication/appointment).

Owner and Pet are data-holding classes (implemented as dataclasses) that map to action 1 — registering pet and owner info. Owner also holds available_minutes_per_day, since action 3 needs a time budget to plan against.
Task is a dataclass representing one unit of care work — it holds duration_minutes and priority (1–5), which are exactly the two fields action 2 asked for.
Scheduler holds all the algorithmic behavior instead of Task or Owner, so the logic for sorting, conflict detection, and — most importantly — generate_daily_plan() lives in one testable place. I split this out specifically because action 3 isn't a simple sort; it's a constrained-selection problem (fit the highest-priority tasks into a limited time budget), which is different enough from "sort by priority" that it earns its own method.

- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

Initially I scaffolded a generic get_today_tasks() method, but re-reading my own action 3, I realized that's not enough — it just filters by date, it doesn't optimize anything. I added a separate generate_daily_plan() method to Scheduler and an available_minutes_per_day field to Owner so there's an actual time budget to plan against.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

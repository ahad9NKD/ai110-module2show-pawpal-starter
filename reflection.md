# PawPal+ Project Reflection

## 1. System Design

### Core User Actions

1. Add and manage pets  
The user should be able to create a profile for their pet, including basic information such as name, species, and age. This allows the system to organize tasks around a specific animal and keep care routines personalized.

2. Create and manage tasks  
The user should be able to add, edit, and manage pet care tasks such as feeding, walking, medication, and grooming. Each task should include at least a duration and a priority level, so the system can make intelligent scheduling decisions.

3. Generate and view a daily plan  
The user should be able to generate a daily schedule based on their available time and task priorities. The system should select the most important tasks and display them clearly, along with a brief explanation of why those tasks were chosen.

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

For the initial design of PawPal+, I chose four main classes: `Owner`, `Pet`, `Task`, and `SchedulePlanner`, plus a small `DailyPlan` class to represent the final schedule.

The `Owner` class represents the pet owner. Its responsibility is to store basic information about the person using the system, such as their name, daily available time, and scheduling preferences.

The `Pet` class represents the animal being cared for. Its responsibility is to store pet-specific information such as name, species, and age. This helps the system organize care tasks around a specific pet.

The `Task` class represents an individual care activity, such as feeding, walking, medication, grooming, or playtime. Its responsibility is to store the task details, including duration, priority, whether it is required, and whether it has been completed.

The `SchedulePlanner` class is the main logic class of the system. Its responsibility is to manage tasks, rank them, and generate a daily plan based on time constraints and priorities. This class is where the scheduling logic lives.

The `DailyPlan` class represents the result of the planner. Its responsibility is to store the selected tasks, the total time used, and the reasoning behind the plan so the user can understand why certain tasks were chosen.

This design separates data objects from decision-making logic. That makes the system easier to test, easier to extend, and cleaner to connect to the Streamlit interface later.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The conflict detector only flags tasks that share an **exact** time string (e.g., two tasks both stored as `"09:00"`). It does not model task duration, so a 30-minute walk starting at `"08:45"` and a feeding task at `"09:00"` are never flagged even though they may overlap in practice.

This tradeoff is reasonable at the current scale for two reasons. First, pet care tasks in a home setting are rarely measured to the minute — owners already allow informal buffers between activities. Second, adding duration-based overlap detection would require every task to carry a duration field and would push conflict-checking from O(n) to O(n²) comparisons. For a single owner with a handful of pets and fewer than ~20 daily tasks, the simpler exact-match approach catches the most obvious scheduling mistakes (double-booking the same time slot) without adding complexity the user would rarely benefit from.

---

## 3. AI Collaboration

**a. How you used AI**

AI tools were used in three distinct ways across the project phases. During design, I used chat prompts to brainstorm which scheduling behaviors were most important for a pet owner and to surface edge cases I might have missed (such as a pet with no tasks, or a one-time task that should not recur). During implementation, I used inline suggestions to draft the `sort_by_time` lambda, the `timedelta` arithmetic in `mark_task_complete`, and the `defaultdict` grouping in `detect_conflicts`. During testing, I used AI to generate an initial list of test scenarios, which I then reviewed and extended to make sure each test was actually asserting the right thing.

The most useful prompts were specific and scoped: for example, "how should `detect_conflicts` handle a task that is already completed?" forced a concrete design decision (exclude completed tasks) rather than producing a generic answer.

**b. Judgment and verification**

The AI initially suggested that `detect_conflicts` should flag conflicts between tasks belonging to the same pet only, on the reasoning that tasks for different pets could theoretically run in parallel. I rejected this because a single owner manages all pets simultaneously — if Rocky's vet appointment and Milo's grooming are both at 09:00, the owner is still double-booked. I verified the decision by writing `test_detect_conflicts_across_multiple_pets`, which confirms that cross-pet same-time conflicts are correctly flagged.

---

## 4. Testing and Verification

**a. What you tested**

The test suite (26 tests) covers task completion state, pet-name stamping, chronological sort correctness (including insertion-order independence), case-insensitive pet filtering, pending/completed status filtering, daily and weekly recurrence (correct `due_date` arithmetic and correct pet assignment), one-time task completion (no follow-up created), conflict detection (same time flagged, different times clean, completed tasks excluded, multi-slot conflicts, cross-pet conflicts), and edge cases for owners or pets with no tasks.

These tests matter because scheduling bugs are silent — the app does not crash, it just shows the wrong plan. Automated tests are the only reliable way to catch a mis-sorted schedule or a recurrence appearing on the wrong date.

**b. Confidence**

Confidence level: **4 out of 5 stars**. All documented behaviors pass and edge cases for empty data are covered. The remaining gap is duration-based overlap detection: two tasks scheduled 15 minutes apart with 30-minute durations would not be flagged. Testing that would require adding a `duration` field to `Task` and rewriting the conflict algorithm.

---

## 5. Reflection

**a. What went well**

The separation between data classes (`Task`, `Pet`, `Owner`) and scheduling logic (`Scheduler`) made the system straightforward to test in isolation. Every method in `Scheduler` can be called with a freshly built owner object, so no shared state bleeds between tests. That clean boundary was the most valuable design decision in the project.

**b. What you would improve**

The `Task` time field is a plain string. This works as long as every task uses zero-padded 24-hour format, but nothing enforces that. A future iteration should validate the format on creation (or switch to a `datetime.time` field), so a typo like `"9:00"` instead of `"09:00"` does not silently break sort order.

**c. Key takeaway**

AI tools are most valuable when the human architect has already defined the problem clearly. When I asked "how do I sort tasks by time?", the suggestions were immediately useful because the data model and the desired outcome were already specified. When I asked a vague question like "how should I handle conflicts?", I had to do more follow-up work to refine the answer into a concrete design decision. The lesson is that AI accelerates implementation but does not replace the upfront thinking needed to know exactly what you want to build.

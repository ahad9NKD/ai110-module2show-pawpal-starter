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

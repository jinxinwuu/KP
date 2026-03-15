# Kill Procrastination

**One tiny step at a time** — an AI-powered momentum generator to help you overcome starting resistance and actually begin the thing you're procrastinating on.

### What it does
You input a goal (big or small), and the app uses AI to give you **one stupidly small, concrete action** that takes <2 minutes, has zero decisions, and has a clear stopping point.

- If the step still feels too hard → click "Make it smaller" (it shrinks even more while staying meaningful)
- Do it → click "I finished"
- Build a streak and get calm encouragement
- Next time → it remembers what you've done and gives the logical next micro-step

The core idea:  
You don't need motivation or a perfect plan.  
You just need to **start** with something so tiny that resistance disappears.  
Once momentum begins, the rest often follows.

### Why I built this
I'm a beginner coder who struggles with procrastination a lot.  
Instead of reading more books or making grand plans, I decided to build a tool that forces me to take one real tiny action every day.  
This is my personal anti-procrastination coach — and maybe it can help others too.

### Current status (March 2026)
- MVP v0.2 running on Streamlit
- Core loop works: goal → tiny step → shrink if needed → do it → finished → streak + next step
- Using OpenAI (gpt-4o-mini) for smart, adaptive prompts
- History memory to avoid regressions
- Basic safety check for dangerous goals
- Still iterating daily on step quality (vague/repetitive steps are the main thing I'm fixing)

### How to run it locally (for developers / curious people)
1. Clone the repo:
   ```bash
   git clone https://github.com/YOUR-USERNAME/kill-procrastination.git
   cd kill-procrastination

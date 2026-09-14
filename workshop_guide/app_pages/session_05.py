import streamlit as st
from components import render_session_header, render_prompt, render_explanation, render_technologies_used, render_key_concepts, render_what_you_built

render_session_header(5, "Data Engineer Skill (Stretch)", "10:45 AM", "10 min", "Reusable Cortex Code skill that packages the code review workflow for any dbt project")

st.info("This is a **stretch session** — complete it if time allows. It builds on the code review workflow from Session 4.")

st.space("small")

render_technologies_used([
    {"name": "Cortex Code Skills", "description": "Reusable prompt workflows that can be triggered by name. Skills encapsulate expert knowledge into repeatable, shareable patterns.", "icon": "psychology"},
    {"name": "Workflow Automation", "description": "Packaging multi-step processes (review → analyze → report) into a single invokable unit that produces consistent output.", "icon": "repeat"},
    {"name": "Prompt Engineering", "description": "Structuring prompts with clear inputs, constraints, and output formats to get reliable, high-quality results from AI assistants.", "icon": "edit_note"},
])


PROMPT_5_1 = """Create a Cortex Code skill called "dbt-code-review" that packages the code review workflow from Session 4 into a reusable skill.

The skill should:

1. Accept as input: a dbt project path or a list of SQL model files to review
2. Perform these steps automatically:
   - Scan all SQL models for anti-patterns (SELECT *, implicit casts, non-sargable predicates, cartesian risks)
   - Check coding standards (CTE naming, column ordering, aliasing)
   - Check Snowflake best practices (QUALIFY usage, NULL handling, table types)
   - Analyze clustering opportunities for tables > 1GB
   - Produce a prioritized findings report

3. Output format: structured markdown report with severity levels, file references, and recommended fixes

4. Include trigger phrases: "review my dbt project", "code review", "check my SQL for anti-patterns"

Generate the skill definition file (SKILL.md format) with:
- Name and description
- Trigger phrases
- The full prompt template
- Example usage

Show me the complete skill file."""

render_prompt("Prompt 5.1", "Create the Code Review Skill", PROMPT_5_1)

render_explanation("What this prompt does", """
Creates a reusable skill definition that can be invoked in future Cortex Code sessions:

```markdown
# dbt Code Review Skill

## Triggers
- "review my dbt project"
- "code review"
- "check my SQL for anti-patterns"
- "scan for performance issues"

## Inputs
- Project path or list of SQL files

## Workflow
1. Scan for SQL anti-patterns
2. Check coding standards
3. Check Snowflake best practices
4. Analyze clustering opportunities
5. Produce prioritized report

## Output Format
Structured markdown with severity, location, issue, fix
```

**Why package as a skill?** The code review workflow took 3 prompts in Session 4. As a skill, it becomes a one-command operation that any data engineer on your team can invoke. Consistent quality, zero ramp-up time.
""")


PROMPT_5_2 = """Test the dbt-code-review skill by running it against just the dimension models in our project.

Use the trigger phrase "review my dbt project" and point it at the dimension models only (models/marts/).

Compare the output to what we got in Session 4:
- Does it find the same issues?
- Is the report format consistent?
- Are the severity levels appropriate?

Show the skill output and your assessment of its quality."""

render_prompt("Prompt 5.2", "Test the Skill", PROMPT_5_2)

render_explanation("What this prompt does", """
Validates that the skill produces consistent, useful output by running it on a subset of models.

**What to look for:**
- Findings should be a subset of Session 4 results (dimension models only)
- Report format should match the template defined in the skill
- No false positives (issues flagged that aren't real problems)
- Severity levels should be calibrated (a CTE naming issue shouldn't be HIGH)

This is the feedback loop: build the skill, test it, refine it. In production, you'd iterate 2-3 times before sharing with the team.
""")


render_key_concepts([
    {"term": "Cortex Code Skill", "definition": "A reusable prompt workflow defined in a SKILL.md file. Skills have trigger phrases, structured inputs, and defined output formats. They encapsulate expertise into repeatable patterns."},
    {"term": "Trigger Phrases", "definition": "Natural language phrases that activate a skill (e.g., 'review my dbt project'). Multiple triggers can map to the same skill for flexibility."},
    {"term": "Prompt Template", "definition": "A structured prompt with placeholders for inputs. The skill fills in the template with the user's specific context (project path, file list) at invocation time."},
])

render_what_you_built([
    "dbt-code-review skill definition (SKILL.md)",
    "Trigger phrases for natural language invocation",
    "Validated skill output against Session 4 baseline",
    "Reusable workflow any team member can invoke",
], session_num=5)

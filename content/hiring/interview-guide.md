# Interview and demonstration practice

## A grounded introduction

I am a Computer Science graduate based in São Paulo. During my data analysis internship at FIPE, I worked with data preparation, SQL, automation in Python and R, and reporting. My personal projects let me explore how those analytical workflows connect to software: from an IBGE data pipeline to DataFlow's quality and transformation workspace. I am looking for junior data and business intelligence roles where I can contribute to reliable analysis and communicate results clearly.

## Demonstration sequence

Open the income case study. State the question, grain, source and snapshot date before quoting a number. Show the latest snapshot, filter to one state, then explain why the mean across states is not the official national estimate. Demonstrate a period with no prior-year comparison and export the selected rows. Open queries.sql and explain the explicit prior-year join and NULL behavior.

For DataFlow, state that this is a synthetic frontend demo, not the running backend. Show a transformation preview, apply it, inspect the history and undo. Explain what additional integration testing would be needed to validate durable recovery with PostgreSQL, Redis and worker processes.

## Two FIPE stories to prepare from actual events

Data quality: choose a real inconsistency you investigated. Record the source, how you noticed it, how you checked the rule, who helped decide the correct treatment and what changed. Do not invent a particular incident or disclose restricted data.

Automation: choose a routine you actually automated or supported. Explain the manual steps, your code's role, how you tested its output and how another person used it. Quote time savings only when you can support both the earlier and later measurements. A qualitative outcome is preferable to an invented percentage.

## Questions to rehearse

What is the grain of this dataset? How could a join multiply records? Why not average already-aggregated values without weights? What does a missing comparison mean? Which rule belongs to business policy rather than technical validity? What did you choose not to build, and why? Which parts did you implement, which were existing libraries, and how did you verify them?

## Application routine

Use the English résumé for relevant international processes and adapt its emphasis to the actual role. Keep professional experience separate from personal projects. Link the most relevant case study rather than every repository. Record the role, company, link, application date and response; avoid duplicate applications. This guide does not submit applications or schedule reminders.

## Evidence you still need to create personally

Record and present your own explanation after rehearsing it. A screen recording without a speaker is a product demonstration, not evidence that you taught an audience. Publish talks, attendance counts and community feedback only after they occur. Maintain a sustainable publishing and maintenance cadence rather than backdating activity.

# Demonstration and interview scripts

Use the first-person passages only after checking that they describe your own work accurately. These scripts prepare a recording; they are not a record of a completed talk. The two FIPE passages below summarize the duties stated in the supplied résumé. No specific incident, client, saving, audience or measurement is invented.

## Opening

Hello, I am Maurício Taguchi, a Computer Science graduate based in São Paulo. During my data analysis internship at FIPE, I worked with economic and collective bargaining data, SQL, automation in Python and R, and reporting in Power BI. I am looking for data analyst and business intelligence roles. I will show one analytical project and one data-quality workflow, explain the decisions, and make their limitations clear.

## Income demonstration

Open the income case study, then the interactive dashboard. Start with all regions and the latest quarter in the snapshot.

The question is how real average monthly labor income differs across Brazil's federal units and how the same quarter compares with the previous year. Each observation represents one federal unit in one quarter. This fixed snapshot covers 27 federal units and 20 quarters; it is not a live feed.

For Q1 2026, the simple mean of the 27 state-level values is BRL 3,437.41. That is a territorial summary, not the official national average. I do not have population weights or confidence intervals in this dataset, so I avoid interpreting it as either a national estimate or a measure of individual earnings.

Select Distrito Federal. Its Q1 2026 value is BRL 6,720. Next, select Q2 2021. The previous-year comparison is unavailable because the matching quarter is outside this snapshot. A missing comparison must not become a zero-percent change.

Open the SQL lab and show the explicit join on state and the same quarter in the previous year. Explain why joining on an incomplete key can multiply records, and why this implementation checks the state-quarter grain. Export the selected rows and compare the export with the visible selection.

My conclusion is descriptive: the dashboard makes differences and changes inspectable. It does not explain their causes or establish an individual's salary.

## DataFlow demonstration

Open the isolated DataFlow demo. Dismiss or follow the tour, then open Transformations.

This is the project's actual frontend running with synthetic sample data. It does not connect to the live backend, accept private files or persist dataset changes. The point is to inspect the workflow, not to claim production reliability.

Preview duplicate removal, apply it, and show the count moving from six records to five. Inspect the history, undo the transformation, and show the six records again. Explain the difference between restoring content and erasing its history. Then reload to show that these demo changes are temporary.

The full repository describes expected revisions, operation receipts and recovery boundaries. Those backend behaviors require separate process-integration tests against PostgreSQL, Redis and workers. The browser demonstration alone does not verify them.

## FIPE: data-quality scope summary

At FIPE, I handled data quality checks for collective bargaining reports. I investigated inconsistent records, consolidated the data, and documented how I validated it. Researchers and managers used the resulting dataset to analyze trends and prepare reports.

Before using this answer as a specific example, reconstruct one real episode privately: What inconsistency did you observe? What evidence confirmed it? What exactly did you do? Who made the final business decision? What was the verified outcome? Leave unknown details blank instead of inventing them. Do not publish confidential input data.

## FIPE: automation scope summary

During my internship, I automated recurring collection and processing with Python, R, Excel and VBA to reduce manual work. I also built and maintained Power BI, DAX and Excel dashboards and metrics for analysis and reporting. My focus was not just running a script, but documenting the processing and preparing information other people could use.

Before describing a specific episode, identify a routine you actually worked on, your contribution, how its output was checked and what changed. The supplied résumé does not establish a measured percentage or number of hours saved. Use a qualitative result unless you have comparable before-and-after evidence.

## Practice questions

What is the dataset grain? Which join keys preserve it? Why is averaging state means not a national estimate? What happens when the prior quarter is unavailable? What does the frontend demo prove, and what does it not prove? Which part was your own implementation? What would you change next, and what evidence would justify that change?

## Recording check

Capture only the demo and public/synthetic data. Explain the actions in your own words, include readable captions, and check that the sound and screen are understandable. Publish it as a tutorial or product demonstration. Add an event or workshop entry only after a real event takes place.

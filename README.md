# jira_sprint_slides

Use JIRA APIs to get sprint data dump and [python-pptx](https://python-pptx.readthedocs.io/en/latest/)
module to generate sprint review PPT.

## Why

Our team updates project stakeholders with a sprint review presentation at the end of each sprint. This
involves categorizing JIRA stories by projects and creating a PPT out of them. Updating the stakeholders
adds value, but manually creating the ppt by copy pasting JIRA ids and summaries doesn't. So I wrote 
this tool.

## It lacks cool JIRA API feature X. Will you add it?

Nope. This is a one time get-it-done script. It satisfies the minimal requirement. I will not
be updating it with any more features. Feel free to fork it and update it.

## How do I use it

1. Install and activate virtualenv - [here](https://gist.github.com/saurabh-hirani/3a2d582d944a792d0e896892e0ee0dea)

2. Install required modules

```sh
pip3 install -r requirements.txt
```

3. Set the sprint name and dump JIRA issues

```sh
export JIRA_SPRINT_NAME='Sample Sprint 22'
export JIRA_USER_NAME='your_jira_user_name'
export JIRA_PASSWORD='your_jira_password'
python dump_sprint_jira_issues.py
```

This creates `data/sample_sprint_22/output.json` and `data/sample_sprint_22/summary.json`

4. Copy `data/sample_sprint_22/summary.json` to `data/sample_sprint_22/summary_updated.json` and
   manually update `data/sample_sprint_22/summary_updated.json` - e.g. ordering the topics, marking
   those who will demo. 

   You can do a diff to see sample manual changes.

```sh
vimdiff data/sample_sprint_22/summary.json data/sample_sprint_22/summary_updated.json
```

5. Generate ppt

```sh
python generate_sprint_review_ppt.py
```

6. Profit

```sh
open output/sample_sprint_22.pptx
```

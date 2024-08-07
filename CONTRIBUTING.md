# Welcome to qunicorn contributing guide
Thank you for investing your time in contributing to our project! 

# New contributor guide
To get an overview of qunicorn, read our **[README](README.md)** or check our **[readTheDocs](https://qunicorn-core.readthedocs.io/en/latest/#)**.


# Git Workflow 
This Section Describes the different collumns in the project view, aswell as the workflow in which issues get moved between them.

## Sprint Backlog
### Short Description:
“This item hasn’t been started”
### Issue-Status: 
Issues, which are yet to be worked on during the Sprint, but have not been started yet.
### What needs to be done?
Issue is assigned to the person working on it and moved to "In Progress".

## In Progress
### Short Description:
“This is actively being worked on”
### Issue-Status: 
Issue is not implemented yet, but is already being worked on.
### What needs to be done?
Editing person implements feature on separate feature branch (see Naming).
When the editing person perceives the issue as done, a pull request is created on the dev-main branch and the issue is pushed to "Ready to Review".

## In Pending
### Short Description:
“This item is awaiting further clarification or resources”
### Issue-Status: 
Issue was already "In Progress".
There are ambiguities/questions that cannot be clarified directly.
In order to close the issue, other previously finished issues are required.
### What needs to be done?
Issue remains here until everything is clarified/completed and editor can continue working on it
Meanwhile the editor can work on other issues.

## Ready to Review
### Short Description:
“This Item is ready for review by other dev”
### Issue-Status: 
Pull request for dev-main is created, issue is done from developer's point of view.
### What needs to be done?
Non-involved person reviews and approves request or denies it
Creator of pull request resolves it, merged into dev-main (with or without squash) and tests there already.
Then issue is pulled to "Done" and unassigned

## Done
### Short Description:
“This Item is ready for review by supervisor”
### Issue-Status: 
Feature is merged into dev-main and already successfully tested there.
### What needs to be done?
Issue is reviewed here by supervisors.
All issues in "Done" are presented in the sprint review.
If everything fits according to the reviewers, the issue is moved to "Ready for Upstream".
At the end of the Sprint Review no Issue should be here anymore.

## Ready for Upstream
### Short Description:
“This Item is ready to be merged into upstream”
### Issue-Status: 
Feature is approved by supervisors.
### What needs to be done?
At the end of the sprint a "bundled" pull request is created by the special devs and the dev-main is merged into the upstream - always without squashing (or without pull request, tbd).
Before the dev-main is not merged into the upstream, it is blocked for everyone.

# Conventions
## Branch Naming convention
Convention is based on: <https://gist.github.com/digitaljhelms/4287848>
* Feature Branch: feature/{IssueNumber}-{ShortIssueDescription}
* Bug Branch: bug/{bugNumber}-{ShortBugDescription}
* Descriptions should not be much longer than 4,5 words

## Commit message convention
Convention is based on: <https://github.com/joelparkerhenderson/git-commit-message>
* Short Description
    * Start with an imperative present active verb: Add, Drop, Fix, Refactor, Optimize, etc.
    * Up to 50 characters
    * Ends without a period
    * Examples: Add feature for a user to like a post; Optimize search speed for a user to see posts
    * No meta data in commit message
* Body
    * Optional
    * More Detailed Description
    * Include any kind of notes, links, examples, etc. as you want.
    * If the commit is related to one issue, we can add the issue number here
* General
    * Commit features.
    * Do not commit too much at once.
    * Git-squash if necessary


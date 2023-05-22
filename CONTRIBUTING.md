# Welcome to qunicorn contributing guide
Thank you for investing your time in contributing to our project! 

# New contributor guide
To get an overview of qunicorn, read our **[README](README.md)** or check our **[readTheDocs](https://qunicorn-core.readthedocs.io/en/latest/#)**.


# Git Workflow 
This section contains our git workflow.

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
    * Do not commit to much at once.
    * Git-squash if necessary


Development Guidelines
======================

Contribution Process
----------------------
1. Issues are moved from the Product Backlog to the Sprint Backlog if:
    * The issue is well defined (Definition of Ready)
    * it is sprint planing
    * no other issues are in the sprint backlog and no other developer requires support.
2. The developer moves the issue to "In Progress" and starts working on it.
    * Developer assigns ticket to themself
3. Document important information during development within the issue
4. After completion of development (check DoD) issue is moved to "Ready for Review" and developer is unassigned
5. Pull Request: Before creating the pull request branch should be up to date with the master. Developer is assigned to PR.
6. After review by another developer, issue is moved to "Done". The reviewer unassigns themself.
    * In the case of feedback, notify developer and leave the feedback in the PR
7. Merge Pull Request
8. Supervisors review issue when they are in "Ready for Release"

Definition of Done
--------------------

* The code should be functional
* The code should have sufficient test coverage (depending on the implemented component)
* All "public" methods need a docstring
* Public endpoints need a tutorial/documentation on how to use them
* Linter and formatter have been run
* The DoD is checked by another developer, who was not involved in the creation

Definition of Ready
--------------------
Issue has been captured in one of the following templates:

Issue template for new features:
********************************

Problem Statement
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

[Why do we need this feature? Description of the problem you're trying to solve, including any relevant background information]

Sketch (Optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

[Attach or embed a sketch or diagram that illustrates the problem or proposed solution]

References (Optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

[List any relevant articles, websites, or other resources that may be helpful]

Expected Behavior
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

[What is the feature? Describe what you expect to happen when the problem is solved, or when the proposed solution is implemented]

Tasks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

[List with all the tasks]

Notes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

[Any additional notes or context that may be helpful in understanding the issue]


Issue template for bug reports:
********************************

Describe the bug
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

[A clear and concise description of what the bug is]

Steps To Reproduce
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

[Steps to reproduce the behavior:]

Expected behavior
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

[A clear and concise description of what you expected to happen]

Screenshots
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

[If applicable, add screenshots to help explain your problem]

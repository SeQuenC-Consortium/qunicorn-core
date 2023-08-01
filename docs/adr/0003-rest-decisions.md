# REST Decisions

* Status:  accepted
* Date: 2023-07-13 <!-- optional -->

## Context and Problem Statement

Use the HTTP Status Codes and Verbs correctly

## Decision Drivers <!-- optional -->

* Consistency
* Correctness

## Decision Outcome

* Status Codes:
    * 200: To Get a resource or a list of resources
    * 202: To Create new objects with POST
    * 4XX: Return The Status Code of the Error Message, if an error occurs
* Verbs:
    * GET: Get a resource or a list of resources
    * POST: Create/Run/Pause/Cancel a resource
    * PUT: Update a resource
    * DELETE: Delete a resource
* Decision on Patch Verb
    * Not used due to similarity to update

<!-- markdownlint-disable-file MD013 -->

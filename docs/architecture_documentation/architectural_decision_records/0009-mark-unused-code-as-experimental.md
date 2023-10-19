# How to mark unused code

* Status: accepted

## Context and Problem Statement

We have several Job Types which could not be tested due to missing access to the cloud provider.
These include:

* IBM_RUNNER
* IBM_UPLOAD

These features should be marked as unfinished, or experimental in code and for the end user.

## Decision Drivers <!-- optional -->

* Clear destinction between finished and unfinished code

## Considered Options

* Mark code as experimental
* Mark code as unfinished

## Decision Outcome

The code will be marked as experimental.

## Description of Changes

The two methods connected with the IBM_RUNNER and IBM_UPLOAD will be marked as experimental.
A warning will be thrown whenever one of the methods is called.

Furthermore, the JobType Enum was extended to include some documentation which informs about the experimental nature.

Lastly, the read the docs documentation was extended to include information about the experimental nature for the end
user.


<!-- markdownlint-disable-file MD013 -->

# Update Python Version to 3.11.0

* Status:  accepted
* Date: 2023-07-05 <!-- optional -->


## Context and Problem Statement

Select a new python version for the qunicorn project

## Decision Drivers <!-- optional -->

* Use of newer python features
* Use of newer ubuntu runner for github actions

## Considered Options

* python 3.11.0
* python 3.10.0

## Decision Outcome

Chosen option: "python 3.11.0", because:
* it supports StrEnum 
* It supports "|" in attribute definition
* Is supported by Ubuntu 22.04
* Compatible with all 3.11. versions
* Not the newest Python Version (3.11.4 as of writing this file)


<!-- markdownlint-disable-file MD013 -->

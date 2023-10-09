# Refactoring of the pilots

* Status: accepted

## Context and Problem Statement

The pilots are currently not very readable and not very clean. Furthermore, logic from multiple pilots is duplicated.

## Decision Drivers <!-- optional -->

* Clean Pilots
* Easily extendable structure
* Defined methods for each pilot

## Considered Options

* Introduction of Base Pilot

## Decision Outcome

It was decided to introduce a Base Pilot.

## Description of Changes

A Base Pilot was introduced.
It defines every method which needs to be implemented by a pilot.
It contains all the logic which is shared between the pilots.
The other Pilots extend from this Base Pilot.


<!-- markdownlint-disable-file MD013 -->

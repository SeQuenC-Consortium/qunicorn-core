# Introducing the transpile manager

* Status: accepted

## Context and Problem Statement

QuantumCircuits from different providers and in different languages should be usable in a variety of ways.

## Decision Drivers <!-- optional -->

* Flexibility of usage of QuantumCircuits
* Don't be restricted to one provider and language
* Provide Extendability to new providers and languages

## Considered Options

* Introduction of transpile manager

## Decision Outcome

It was decided to introduce a transpile manager

## Description of Changes

The transpile manager transpiles QuantumCircuits from different languages into different languages.
It does this most effectively by using the shorted route between languages.
For this it creates a graph and finds the shortest route using the Dijkstra algorithm.
When multiple languages are available, the language with the least transpile steps is used.


<!-- markdownlint-disable-file MD013 -->

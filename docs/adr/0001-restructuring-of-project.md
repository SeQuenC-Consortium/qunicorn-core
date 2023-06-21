# Restructuring of Qunicorn Project

* Status: accepted

## Context and Problem Statement

The Project Structure needed to be restructured in order to have api and logic seperated.

## Decision Drivers <!-- optional -->

* api and logic separation
* better readability of project

## Considered Options

* "Core" Folder with logic

## Decision Outcome

Chosen option: "[option 1]"
Core Folder created, which includes:
* services classes for computation
* mapper classes to map from dtos to db objects

Api Folder edited, which includes:
* Api Definition (Views, Routes, etc.)
* Model definitions (Schemas and dtos)

DB Folder edited, which includes:
* Database services, which serve to access the database
* Database model definitions

<!-- markdownlint-disable-file MD013 -->

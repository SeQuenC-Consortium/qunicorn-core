# Restructuring of Qunicorn Project
* Status: accepted

## Context and Problem Statement
The Project Structure needed to be restructured in order to have api and logic seperated.

## Decision Drivers <!-- optional -->
* Api and logic separation
* Better readability of project

## Considered Options
* "Core" Folder with logic
* Not doing anything

## Decision Outcome
Chosen option: ""Core" Folder with logic"

## Description of Changes
A core package was added. Most of the computational logic was moved to it. 

### Project Restructuring
Below is a description of the different packages and what they  include:
#### api package:
* api_models: DTOs and Schemas for all Objects.
  * These are used for Computation and to define the Schemas for the API Views
* {object}_api:
  * These include the Definition of the different Views
#### core package:
* mapper:
  * This Includes Mapper from DTOs to Database Objects, Helper Class
* {object}manager:
  * Computational Classes for different Object
  * Service Classes, which get called from API
    * All calls from API should be forwarded to these classes.
    * Celery tasks
#### db package:
* database_services:
  * Services to access the database (add, get, update, remove)
* models:
  * Definition of various database models

### This lead to other various changes:
#### relationship attributes in database:
* Used to access whole Database Objects, instead of doing another load via ID.
* Not represented in database itself, only in code.
* Its "good practice" of accessing and saving whole objects instead of id. (Unless you really know what you are doing.) 

#### Job_dtos were extended:
* JobCoreDto: Internal Job Handling: includes most data and links to other DTOs, furthermore used for internal 
communication.
* JobRequestDto: Request received from API
* JobResponseDto: DTO used to respond via API

#### Flask/poetry methods defined:
* flask create-and-load-db: Drops the current db, creates a new one, and loads example data
* poetry run invoke check-linting: Checks flake8 and black linting/formatting. 



<!-- markdownlint-disable-file MD013 -->

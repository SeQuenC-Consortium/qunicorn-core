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

Chosen option: ""Core" Folder with logic"

## Description of Changes
Below is a description of the different packages and what they  include:
* api package:
  * api_models: DTOs and Schemas for all Objects.
    * These are used for Computation and to define the Schemas for the API Views
  * object_api
    * These include the Definition of the different Views
* core package:
  * mapper:
    * This Includes Mapper from DTOs to Database Objects, Helper Class
  * (object)manager
    * Computational Classes for different Object
    * Service Classes, which get called from API
    * Celery tasks
* db package:
  * database_services
    * Services to access the database (add, get, update, remove)
  * models
    * Definition of various database models

<!-- markdownlint-disable-file MD013 -->

# How to Map Dtos to Database Objects and wise versa

* Status: accepted

## Context and Problem Statement

We need multiple data transfer objects (DTOs) for different purposes.

* One for the requests
* One for the internal logic
* One for the database
* One for the responses

Normally they need to map from request to core and then back to a response-dto.
To save the updates to the database they need to be mapepd to the database object.
To map all of these, we need a mapper.

## Decision Drivers <!-- optional -->

* Have all mapper at one place
* Clean and readable code
* Automatically map objects

## Considered Options

* object-mapper
* py-automapper
* map-struct

## Decision Outcome

py-automapper

## Description of Changes

A library was added. And used in the "core/mapper/" folder.

### Folder Structure

* core/mapper/
    * \__init\__.py: Contains all imports for the mapper
    * general_mapper.py: Contains a helper method which can be used to map objects with automapper
    * mapper.py: Multiple mapper, one for each model

### Naming Pattern

The naming pattern for the mapper-methods is as follows:
If a dataclass object needs to be mapped to a dto the name would be dataclass_to_dto.
If there exists multiple dtos for one dataclass model, the name does not anymore include "dto".
For example for the job_request_dto the mapper name is: dataclass_to_request.


<!-- markdownlint-disable-file MD013 -->

# Copyright 2023 University of Stuttgart
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Module containing all API schemas for tasks in the Deployment API."""

import marshmallow as ma
from marshmallow import fields, ValidationError
from ..util import MaBaseSchema

__all__ = ["PreDeploymentSchema",]


class PreDeploymentSchema(MaBaseSchema):
    uid = ma.fields.Integer(required=False)
    name = ma.fields.Str(required=True, metadata={
        "description": "An optional Name for the deployment."
    })
    mode = ma.fields.Str(required=True, metadata={
        "description": "Describes whether a Job should be pre-deployed or executed ad-hoc."
    })
    description = ma.fields.Str(required=False, metadata={
        "description" :  "Description for the Pre-deployment."
    })
    credentials = ma.fields.Dict(
       keys=ma.fields.Str(), values=ma.fields.Str(), required=False, 
    )
    parameters = ma.fields.List(
        ma.fields.Integer(), metadata={
        "description" :  "List of Parameters for Quantum Circuits."
    })
    shots = ma.fields.Int(required=False, metadata={
        "description" :  "Specifying shots for ad-hoc execution."
    })
    deploymentType = ma.fields.Str(required=True, metadata={
        "description": "Decide between [Circuit], [CodeFile] ,[Container]."
    })
    resourceURI = ma.fields.Str(required=True)
    tags = ma.fields.List(fields.Str(), required=False, metadata={
      "description": "A list of Tags, for grouping and searching deployments"        
    })
    source = ma.fields.Str(required=False, metadata={
        "description": "The source format of a quantum circuit."
    })
    target = ma.fields.Str(required=False, metadata={
        "description": "The Target Service, needed for translation between formats. Decides which Pilot needs to be used"
    })
    
class DeploymentResponseSchema(MaBaseSchema):
    pass
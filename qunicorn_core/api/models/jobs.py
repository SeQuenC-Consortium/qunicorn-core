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


"""Module containing all API schemas for tasks in the Jobmanager API."""

import marshmallow as ma
from marshmallow import fields, ValidationError
from qiskit import QuantumCircuit

from ..util import MaBaseSchema

__all__ = ["JobIDSchema", "JobRegisterSchema"]


class CircuitField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str) or isinstance(value, list):
            return value
        else:
            raise ValidationError("Field should be str or list")


def get_quasm_string() -> str:
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    return qc.qasm()


class JobRegisterSchema(MaBaseSchema):
    circuit = CircuitField(required=True, example=get_quasm_string())
    provider = ma.fields.String(required=True, example="IBMQ")
    token = ma.fields.String(required=True, example="")
    qpu = ma.fields.String(required=True)
    credentials = ma.fields.Dict(
        keys=ma.fields.Str(), values=ma.fields.Str(), required=True
    )
    shots = ma.fields.Int(required=False, allow_none = True, metada={
        "label" : "Shots",
        "description" : "Number of shots",
        "input_type" : "number"
    }, example=4000)
    circuit_format = ma.fields.String(required=False)
    noise_model = ma.fields.String(required=False)
    only_measurement_errors = ma.fields.Boolean(required=False)
    parameters = ma.fields.List(ma.fields.Float(), required=False)


class JobIDSchema(MaBaseSchema):
    uid = ma.fields.Integer(required=True, allow_none=False, dump_only=True, example=123)
    description = ma.fields.String(required=False, allow_none=False, dump_only=True)
    taskmode = ma.fields.Integer(required=False, allow_none=False, dump_only=True)

class JobResponseSchema(MaBaseSchema):
    pass

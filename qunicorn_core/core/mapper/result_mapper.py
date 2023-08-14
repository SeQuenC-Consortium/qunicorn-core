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
import traceback

from braket.tasks import GateModelQuantumTaskResult
from qiskit.primitives import EstimatorResult, SamplerResult
from qiskit.result import Result

from qunicorn_core.api.api_models import ResultDto
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.result_type import ResultType


def runner_result_to_db_results(ibm_result: Result, circuit: str) -> list[ResultDataclass]:
    result_dtos: list[ResultDataclass] = []

    for i in range(len(ibm_result.results)):
        counts: dict = ibm_result.results[i].data.counts
        result_dtos.append(
            ResultDataclass(
                circuit=circuit,
                result_dict=counts,
                result_type=ResultType.COUNTS,
                meta_data=ibm_result.results[i].to_dict(),
            )
        )
    return result_dtos


def estimator_result_to_db_results(
    ibm_result: EstimatorResult, circuits: [str], observer: str
) -> list[ResultDataclass]:
    return [
        ResultDataclass(
            circuit=circuit,
            result_dict={"value": str(result_values), "variance": str(metadata["variance"])},
            result_type=ResultType.VALUE_AND_VARIANCE,
            meta_data={"observer": f"SparsePauliOp-{observer}"},
        )
        for result_values, metadata, circuit in zip(ibm_result.values, ibm_result.metadata, circuits)
    ]


def sampler_result_to_db_results(ibm_result: SamplerResult, circuits: [str]) -> list[ResultDataclass]:
    return [
        ResultDataclass(
            circuit=circuit,
            result_dict=quasi_dist,
            result_type=ResultType.QUASI_DIST,
        )
        for quasi_dist, circuit in zip(ibm_result.quasi_dists, circuits)
    ]


def aws_local_simulator_result_to_db_results(
    aws_result: GateModelQuantumTaskResult, circuit: str
) -> list[ResultDataclass]:
    result_dtos: list[ResultDataclass] = [
        ResultDataclass(
            result_dict={
                "counts": dict(aws_result.measurement_counts.items()),
                "probabilities": aws_result.measurement_probabilities,
            },
            circuit=circuit,
            meta_data="",
            result_type=ResultType.COUNTS,
        )
    ]
    return result_dtos


def result_to_result_dto(result: ResultDataclass) -> ResultDto:
    return ResultDto(
        id=result.id,
        circuit=result.circuit,
        result_dict=result.result_dict,
        header=result.meta_data,
        result_type=result.result_type,
    )


def get_error_results(exception: Exception, circuit: str | None = None) -> list[ResultDataclass]:
    exception_message: str = str(exception)
    stack_trace: str = traceback.format_exc()
    return [
        ResultDataclass(
            result_type=ResultType.ERROR,
            circuit=circuit,
            result_dict={"exception_message": exception_message},
            meta_data={"stack_trace": stack_trace},
        )
    ]

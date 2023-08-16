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

from qunicorn_core.api.api_models import JobCoreDto, ResultDto
from qunicorn_core.core.mapper.general_mapper import map_from_to
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.result_type import ResultType


def dataclass_to_dto(result: ResultDataclass) -> ResultDto:
    return map_from_to(result, ResultDto)


def ibm_runner_to_dataclass(ibm_result: Result, job_dto: JobCoreDto) -> list[ResultDataclass]:
    result_dtos: list[ResultDataclass] = []

    for i in range(len(ibm_result.results)):
        counts: dict = ibm_result.results[i].data.counts
        circuit: str = job_dto.deployment.programs[i].quantum_circuit
        result_dtos.append(
            ResultDataclass(
                circuit=circuit,
                result_dict=counts,
                result_type=ResultType.COUNTS,
                meta_data=ibm_result.results[i].to_dict(),
            )
        )
    return result_dtos


def ibm_estimator_to_dataclass(ibm_result: EstimatorResult, job: JobCoreDto, observer: str) -> list[ResultDataclass]:
    result_dtos: list[ResultDataclass] = []
    for i in range(ibm_result.num_experiments):
        value: float = ibm_result.values[i]
        variance: float = ibm_result.metadata[i]["variance"]
        circuit: str = job.deployment.programs[i].quantum_circuit
        result_dtos.append(
            ResultDataclass(
                circuit=circuit,
                result_dict={"value": str(value), "variance": str(variance)},
                result_type=ResultType.VALUE_AND_VARIANCE,
                meta_data={"observer": f"SparsePauliOp-{observer}"},
            )
        )
    return result_dtos


def ibm_sampler_to_dataclass(ibm_result: SamplerResult, job_dto: JobCoreDto) -> list[ResultDataclass]:
    result_dtos: list[ResultDataclass] = []
    for i in range(ibm_result.num_experiments):
        quasi_dist: dict = ibm_result.quasi_dists[i]
        circuit: str = job_dto.deployment.programs[i].quantum_circuit
        result_dtos.append(
            ResultDataclass(
                circuit=circuit,
                result_dict=quasi_dist,
                result_type=ResultType.QUASI_DIST,
            )
        )
    return result_dtos


def aws_runner_to_dataclass(
    aws_results: list[GateModelQuantumTaskResult],
    job_dto: JobCoreDto,
) -> list[ResultDataclass]:
    result_dtos: list[ResultDataclass] = [
        ResultDataclass(
            result_dict={
                "counts": dict(aws_result.measurement_counts.items()),
                "probabilities": aws_result.measurement_probabilities,
            },
            job_id=job_dto.id,
            circuit=aws_result.additional_metadata.action.source,
            meta_data="",
            result_type=ResultType.COUNTS,
        )
        for aws_result in aws_results
    ]
    return result_dtos


def exception_to_error_results(exception: Exception, circuit: str | None = None) -> list[ResultDataclass]:
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

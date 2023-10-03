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

from qunicorn_core.api.api_models import ResultDto
from qunicorn_core.core.mapper.general_mapper import map_from_to
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.result_type import ResultType


def dataclass_to_dto(result: ResultDataclass) -> ResultDto:
    return map_from_to(result, ResultDto)


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

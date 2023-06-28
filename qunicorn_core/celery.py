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

from celery import Celery, Task
from flask.app import Flask


class FlaskTask(Task):
    def __call__(self, *args, **kwargs):
        with self.app.flask_app.app_context():
            # run task with app context
            return self.run(*args, **kwargs)


CELERY = Celery(
    __name__,
    flask_app=None,
    task_cls=FlaskTask,
    broker="redis://localhost:6379",
    backend="redis://localhost:6379",
)


def register_celery(app: Flask):
    """Load the celery config from the app instance."""
    CELERY.conf.update(
        app.config.get("CELERY", {}),
        beat_schedule={},
    )
    CELERY.flask_app = app

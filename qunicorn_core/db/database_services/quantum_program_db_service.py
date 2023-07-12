from qunicorn_core.api.api_models import QuantumProgramDto
from qunicorn_core.core.mapper import quantum_program_mapper
from qunicorn_core.db.database_services import db_service
from qunicorn_core.db.models.quantum_program import QuantumProgramDataclass


def create_database_quantum_program(job_core: QuantumProgramDto):
    """Creates a database job with the given circuit and saves it in the database"""
    program: QuantumProgramDataclass = quantum_program_mapper.dto_to_quantum_program_without_id(job_core)
    return db_service.save_database_object(program)


def get_program(program_id: int) -> QuantumProgramDataclass:
    """Gets the job with the job_id from the database"""
    return db_service.get_database_object(program_id, QuantumProgramDataclass)

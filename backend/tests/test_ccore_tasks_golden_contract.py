from backend.src.ccore.tasks.task import CCoreTask
from backend.src.ccore.tasks.task_contracts import CCoreTaskRequestParser
from backend.src.ccore.tasks.task_mapper import CCoreTaskMapper
from backend.src.ccore.tasks.task_repository_contract import (
    CCoreTaskRepositoryProtocol,
)
from backend.src.ccore.tasks.task_service import CCoreTaskService
from backend.src.ccore.tasks.task_validator import CCoreTaskValidator


class FakeStatusRepository:
    def find_all_statuses(self):
        return []

    def status_exists(self, status_code: str) -> bool:
        return status_code in {"PENDING", "ACTIVE", "DONE"}


class FakeTaskRepository:
    def __init__(self):
        self.created_task = None

    def find_all_tasks(self):
        return []

    def find_by_id(self, task_id: str):
        return None

    def create_task(self, task: CCoreTask):
        self.created_task = CCoreTask(
            task_id="task-1",
            task_name=task.task_name,
            status_code=task.status_code,
            status_label="Pending",
            created_at="2026-06-22T09:00:00",
        )
        return self.created_task

    def update_task(self, task: CCoreTask):
        return task

    def delete_task(self, task_id: str):
        return True


def test_task_response_contract_exposes_only_camel_case_api_fields():
    mapper = CCoreTaskMapper()

    response = mapper.domain_to_response(
        CCoreTask(
            task_id="task-1",
            task_name="Golden Task",
            status_code="PENDING",
            status_label="Pending",
            created_at="2026-06-22T09:00:00",
        )
    )

    assert response == {
        "taskId": "task-1",
        "taskName": "Golden Task",
        "status": "PENDING",
        "statusLabel": "Pending",
        "createdAt": "2026-06-22T09:00:00",
    }
    assert "id" not in response
    assert "name" not in response


def test_create_request_parser_accepts_only_canonical_camel_case_fields():
    parser = CCoreTaskRequestParser()

    request = parser.parse_create_request(
        {
            "taskName": "Golden Task",
            "status": "PENDING",
        }
    )

    assert request.task_name == "Golden Task"
    assert request.status_code == "PENDING"


def test_create_request_parser_rejects_legacy_alias_fields():
    parser = CCoreTaskRequestParser()

    try:
        parser.parse_create_request({"name": "Legacy Task", "status": "PENDING"})
    except ValueError as error:
        assert "Unsupported task request field" in str(error)
        assert "name" in str(error)
    else:
        raise AssertionError("Expected legacy alias field to be rejected.")


def test_service_depends_on_repository_contract_and_creates_task():
    repository: CCoreTaskRepositoryProtocol = FakeTaskRepository()
    validator = CCoreTaskValidator(status_repository=FakeStatusRepository())
    service = CCoreTaskService(task_repository=repository, task_validator=validator)

    created_task = service.create_task(
        CCoreTask(
            task_id=None,
            task_name="Golden Task",
            status_code="PENDING",
        )
    )

    assert created_task.task_id == "task-1"
    assert created_task.task_name == "Golden Task"
    assert created_task.status_code == "PENDING"

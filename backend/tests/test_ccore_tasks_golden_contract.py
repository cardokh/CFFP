import io
import json

from backend.src.ccore.tasks.task import CCoreTask
from backend.src.ccore.tasks.task_contracts import CCoreTaskRequestParser
from backend.src.ccore.tasks.task_mapper import CCoreTaskMapper
from backend.src.ccore.tasks.task_repository_contract import (
    CCoreTaskRepositoryProtocol,
)
from backend.src.ccore.tasks.task_routes import handle_update_ccore_task
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
        self.updated_task = None

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
            updated_at="2026-06-22T09:00:00",
        )
        return self.created_task

    def update_task(self, task: CCoreTask):
        self.updated_task = task
        return CCoreTask(
            task_id=task.task_id,
            task_name=task.task_name,
            status_code=task.status_code,
            status_label="Done",
            created_at="2026-06-22T09:00:00",
            updated_at="2026-06-22T10:00:00",
        )

    def delete_task(self, task_id: str):
        return True


class FakeRouteHandler:
    def __init__(self, payload):
        raw_body = json.dumps(payload).encode("utf-8")
        self.headers = {
            "Content-Length": str(len(raw_body)),
        }
        self.rfile = io.BytesIO(raw_body)
        self.wfile = io.BytesIO()
        self.status_code = None
        self.response_headers = []

    def send_response(self, status_code):
        self.status_code = status_code

    def send_header(self, name, value):
        self.response_headers.append((name, value))

    def end_headers(self):
        pass

    def json_response(self):
        return json.loads(self.wfile.getvalue().decode("utf-8"))


def test_task_response_contract_exposes_only_camel_case_api_fields():
    mapper = CCoreTaskMapper()

    response = mapper.domain_to_response(
        CCoreTask(
            task_id="task-1",
            task_name="Golden Task",
            status_code="PENDING",
            status_label="Pending",
            created_at="2026-06-22T09:00:00",
            updated_at="2026-06-22T10:00:00",
        )
    )

    assert response == {
        "taskId": "task-1",
        "taskName": "Golden Task",
        "status": "PENDING",
        "statusLabel": "Pending",
        "createdAt": "2026-06-22T09:00:00",
        "updatedAt": "2026-06-22T10:00:00",
    }
    assert "id" not in response
    assert "name" not in response
    assert "created_at" not in response
    assert "updated_at" not in response


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


def test_update_request_parser_rejects_legacy_alias_fields():
    parser = CCoreTaskRequestParser()

    try:
        parser.parse_update_request(
            "task-1",
            {
                "taskName": "Golden Task",
                "name": "Legacy Task",
                "status": "PENDING",
            },
        )
    except ValueError as error:
        assert "Unsupported task request field" in str(error)
        assert "name" in str(error)
    else:
        raise AssertionError("Expected legacy alias field to be rejected.")


def test_validator_rejects_invalid_reference_status():
    validator = CCoreTaskValidator(status_repository=FakeStatusRepository())

    try:
        validator.validate_update_task(
            CCoreTask(
                task_id="task-1",
                task_name="Golden Task",
                status_code="UNKNOWN",
            )
        )
    except ValueError as error:
        assert str(error) == "Task status is not valid."
    else:
        raise AssertionError("Expected invalid task status to be rejected.")


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
    assert created_task.updated_at == "2026-06-22T09:00:00"


def test_update_route_returns_standard_error_shape_for_invalid_payload():
    repository = FakeTaskRepository()
    validator = CCoreTaskValidator(status_repository=FakeStatusRepository())
    service = CCoreTaskService(task_repository=repository, task_validator=validator)
    handler = FakeRouteHandler({"name": "Legacy Task", "status": "PENDING"})

    handle_update_ccore_task(handler, service, "/api/ccore/tasks/task-1")

    response = handler.json_response()

    assert handler.status_code == 400
    assert response == {
        "success": False,
        "error": {
            "code": "CCORE_TASK_VALIDATION_ERROR",
            "message": "Unsupported task request field.: name",
        },
    }


def test_update_route_returns_standard_success_shape_and_updated_at():
    repository = FakeTaskRepository()
    validator = CCoreTaskValidator(status_repository=FakeStatusRepository())
    service = CCoreTaskService(task_repository=repository, task_validator=validator)
    handler = FakeRouteHandler({"taskName": "Golden Task", "status": "DONE"})

    handle_update_ccore_task(handler, service, "/api/ccore/tasks/task-1")

    response = handler.json_response()

    assert handler.status_code == 200
    assert response["success"] is True
    assert response["message"] == "CCore task updated successfully."
    assert response["task"] == {
        "taskId": "task-1",
        "taskName": "Golden Task",
        "status": "DONE",
        "statusLabel": "Done",
        "createdAt": "2026-06-22T09:00:00",
        "updatedAt": "2026-06-22T10:00:00",
    }

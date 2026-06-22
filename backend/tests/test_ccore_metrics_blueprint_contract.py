from backend.src.ccore.metrics.metric import CCoreMetric
from backend.src.ccore.metrics.metric_contracts import CCoreMetricRequestParser
from backend.src.ccore.metrics.metric_mapper import CCoreMetricMapper
from backend.src.ccore.metrics.metric_repository_contract import (
    CCoreMetricRepositoryProtocol,
)
from backend.src.ccore.metrics.metric_service import CCoreMetricService
from backend.src.ccore.metrics.metric_validator import CCoreMetricValidator


class FakeMetricTypeRepository:
    def find_all_types(self):
        return []

    def type_exists(self, metric_type_code: str) -> bool:
        return metric_type_code in {"COUNTER", "GAUGE", "TIMER"}


class FakeMetricRepository:
    def __init__(self):
        self.created_metric = None

    def find_all_metrics(self):
        return []

    def find_by_id(self, metric_id: str):
        return None

    def create_metric(self, metric: CCoreMetric):
        self.created_metric = CCoreMetric(
            metric_id="metric-1",
            metric_name=metric.metric_name,
            metric_key=metric.metric_key,
            metric_type_code=metric.metric_type_code,
            metric_type_label="Counter",
            created_at="2026-06-22T10:00:00",
        )
        return self.created_metric

    def update_metric(self, metric: CCoreMetric):
        return metric

    def delete_metric(self, metric_id: str):
        return True


def test_metric_response_contract_exposes_only_camel_case_api_fields():
    mapper = CCoreMetricMapper()

    response = mapper.domain_to_response(
        CCoreMetric(
            metric_id="metric-1",
            metric_name="Task Execution Count",
            metric_key="task.execution.count",
            metric_type_code="COUNTER",
            metric_type_label="Counter",
            created_at="2026-06-22T10:00:00",
        )
    )

    assert response == {
        "metricId": "metric-1",
        "metricName": "Task Execution Count",
        "metricKey": "task.execution.count",
        "metricType": "COUNTER",
        "metricTypeLabel": "Counter",
        "createdAt": "2026-06-22T10:00:00",
    }
    assert "id" not in response
    assert "name" not in response
    assert "type" not in response


def test_create_request_parser_accepts_only_canonical_camel_case_fields():
    parser = CCoreMetricRequestParser()

    request = parser.parse_create_request(
        {
            "metricName": "Task Execution Count",
            "metricKey": "task.execution.count",
            "metricType": "COUNTER",
        }
    )

    assert request.metric_name == "Task Execution Count"
    assert request.metric_key == "task.execution.count"
    assert request.metric_type_code == "COUNTER"


def test_create_request_parser_rejects_legacy_alias_fields():
    parser = CCoreMetricRequestParser()

    try:
        parser.parse_create_request({"name": "Legacy Metric", "metricType": "COUNTER"})
    except ValueError as error:
        assert "Unsupported metric request field" in str(error)
        assert "name" in str(error)
    else:
        raise AssertionError("Expected legacy alias field to be rejected.")


def test_service_depends_on_repository_contract_and_creates_metric():
    repository: CCoreMetricRepositoryProtocol = FakeMetricRepository()
    validator = CCoreMetricValidator(type_repository=FakeMetricTypeRepository())
    service = CCoreMetricService(metric_repository=repository, metric_validator=validator)

    created_metric = service.create_metric(
        CCoreMetric(
            metric_id=None,
            metric_name="Task Execution Count",
            metric_key="task.execution.count",
            metric_type_code="COUNTER",
        )
    )

    assert created_metric.metric_id == "metric-1"
    assert created_metric.metric_name == "Task Execution Count"
    assert created_metric.metric_key == "task.execution.count"
    assert created_metric.metric_type_code == "COUNTER"

from scripts.shared.base_script import BaseScript
from scripts.shared.script_console_utils import (
    print_failed,
    print_passed,
)
from scripts.shared.script_json_utils import (
    write_json_file,
)


class WriteBlueprintRules(BaseScript):
    def __init__(self):
        super().__init__(__file__)

    def get_target_folder(self) -> str:
        target_folder = self.config.get("targetFolder")

        if not isinstance(target_folder, str):
            raise ValueError("Config must contain 'targetFolder'.")

        return target_folder

    def get_output_file_name(self) -> str:
        output_file_name = self.config.get("outputFileName")

        if not isinstance(output_file_name, str):
            raise ValueError("Config must contain 'outputFileName'.")

        return output_file_name

    def get_rule_files(self) -> list[str]:
        rule_files = self.config.get("ruleFiles")

        if not isinstance(rule_files, list):
            raise ValueError("Config must contain 'ruleFiles'.")

        for rule_file in rule_files:
            if not isinstance(rule_file, str):
                raise ValueError("Every rule file must be a string.")

        return rule_files

    def rule(
        self,
        rule_id: str,
        name: str,
        description: str,
        severity: str,
    ) -> dict:
        return {
            "ruleId": rule_id,
            "name": name,
            "description": description,
            "severity": severity,
        }

    def configurable_rule(
        self,
        rule_id: str,
        name: str,
        description: str,
        severity: str,
        config: dict,
    ) -> dict:
        rule = self.rule(
            rule_id,
            name,
            description,
            severity,
        )

        rule["config"] = config

        return rule

    def build_naming_convention_rules(self) -> dict:
        return {
            "ruleSetName": "naming-convention-rules",
            "description": "Defines naming conventions across frontend, API boundary, backend internals, database, and routes.",
            "rules": [
                self.rule(
                    "NAMING-001",
                    "Frontend uses camelCase",
                    "Frontend JavaScript variables, functions, request payload fields, response payload fields, and query parameters must use camelCase.",
                    "ERROR",
                ),
                self.rule(
                    "NAMING-002",
                    "Backend internals use snake_case",
                    "Python variables, methods, functions, DTO properties, domain object properties, and database fields must use snake_case internally.",
                    "ERROR",
                ),
                self.rule(
                    "NAMING-003",
                    "Routes use kebab-case",
                    "URL path segments must use kebab-case.",
                    "ERROR",
                ),
                self.rule(
                    "NAMING-004",
                    "Constants use UPPER_SNAKE_CASE",
                    "Constants in frontend and backend code must use UPPER_SNAKE_CASE.",
                    "ERROR",
                ),
                self.rule(
                    "NAMING-005",
                    "Mapping boundary owns naming conversion",
                    "camelCase API payloads must be converted to snake_case internal objects at the mapper/contract boundary, and snake_case internals must be converted back to camelCase only at the API response boundary.",
                    "ERROR",
                ),
                self.rule(
                    "NAMING-006",
                    "Entity and module names should remain semantically consistent",
                    "Singular/plural naming, module ownership, and entity terminology should remain consistent across frontend, backend, routes, repositories, DTOs, and database structures.",
                    "WARNING",
                ),
            ],
        }

    def build_hardcoding_rules(self) -> dict:
        return {
            "ruleSetName": "hardcoding-rules",
            "description": "Defines rules for avoiding hardcoded paths, endpoints, field names, statuses, and magic values.",
            "rules": [
                self.rule(
                    "HARDCODING-001",
                    "Do not hardcode API endpoints in page controllers",
                    "Frontend page controllers must use shared API endpoint constants or endpoint builders.",
                    "ERROR",
                ),
                self.rule(
                    "HARDCODING-002",
                    "Do not hardcode frontend navigation paths",
                    "Frontend navigation must use the shared frontend path registry.",
                    "ERROR",
                ),
                self.rule(
                    "HARDCODING-003",
                    "Do not hardcode script paths",
                    "Scripts must use shared path utilities and configuration files for paths and folders.",
                    "ERROR",
                ),
                self.rule(
                    "HARDCODING-004",
                    "Do not hardcode transport field names in services",
                    "Services must not know frontend/API field names or build raw transport dictionaries.",
                    "ERROR",
                ),
                self.rule(
                    "HARDCODING-005",
                    "Avoid magic business values",
                    "Business statuses, numeric codes, and reusable labels should come from constants, reference data, or centralized configuration.",
                    "WARNING",
                ),
                self.rule(
                    "HARDCODING-006",
                    "Do not hardcode SQL outside repositories",
                    "SQL statements must only exist in repositories or dedicated persistence infrastructure.",
                    "ERROR",
                ),
            ],
        }

    def build_scripting_blueprint_rules(self) -> dict:
        return {
            "ruleSetName": "scripting-blueprint-rules",
            "description": "Defines the standard architecture for project scripts.",
            "rules": [
                self.rule(
                    "SCRIPT-001",
                    "Scripts must use BaseScript",
                    "Project scripts must extend the shared BaseScript class unless there is a documented reason not to.",
                    "ERROR",
                ),
                self.rule(
                    "SCRIPT-002",
                    "Scripts must read from config",
                    "Script behavior must be driven by a config file in the script's config folder.",
                    "ERROR",
                ),
                self.rule(
                    "SCRIPT-003",
                    "Scripts must write reports to output",
                    "Scripts must write detailed execution output to their own output folder.",
                    "ERROR",
                ),
                self.rule(
                    "SCRIPT-004",
                    "Console output must be concise",
                    "Scripts should print one concise success or failure message to the terminal.",
                    "WARNING",
                ),
                self.rule(
                    "SCRIPT-005",
                    "Scripts must use shared utilities",
                    "Scripts should use shared utilities for JSON, paths, config loading, and console output.",
                    "ERROR",
                ),
                self.rule(
                    "SCRIPT-006",
                    "Scripts should separate configuration, execution, and reporting",
                    "Script configuration, execution logic, runtime state, and reporting/output generation should remain separated to support reusable script infrastructure and future framework evolution.",
                    "WARNING",
                ),
                self.configurable_rule(
                    "SCRIPT-007",
                    "Scripts must not contain hardcoded output path fragments",
                    "Scripts must avoid hardcoded output path fragments and should use BaseScript output architecture instead.",
                    "ERROR",
                    {
                        "disallowedPathFragments": [
                            "scripts/blueprint/governed/output",
                            "output/",
                            "\\output\\",
                        ]
                    },
                ),
            ],
        }

    def build_layering_rules(self) -> dict:
        return {
            "ruleSetName": "layering-rules",
            "description": "Defines allowed responsibilities and dependencies between frontend, routes, mappers, services, repositories, and database.",
            "rules": [
                self.rule(
                    "LAYER-001",
                    "Routes delegate business work",
                    "Route handlers must handle HTTP concerns, validation, mapping, and response sending, then delegate use cases to services.",
                    "ERROR",
                ),
                self.rule(
                    "LAYER-002",
                    "Services orchestrate only",
                    "Services must coordinate validators, repositories, and domain operations without SQL, raw HTTP payload parsing, or response dictionary construction.",
                    "ERROR",
                ),
                self.rule(
                    "LAYER-003",
                    "Repositories own persistence",
                    "Repositories must own SQL/database access and return domain objects, DTOs, booleans, or repository-level results.",
                    "ERROR",
                ),
                self.rule(
                    "LAYER-004",
                    "Mappers own conversion",
                    "Mappers must own conversion between API payloads, DTOs, domain objects, database rows, and response dictionaries.",
                    "ERROR",
                ),
                self.rule(
                    "LAYER-005",
                    "No upward dependency leakage",
                    "Lower layers must not depend on frontend, HTTP handlers, route utilities, or UI field names.",
                    "ERROR",
                ),
                self.rule(
                    "LAYER-006",
                    "Frontend must not bypass backend architecture",
                    "Frontend code must communicate through approved API/service boundaries and must not directly access persistence, infrastructure, or internal backend implementation details.",
                    "ERROR",
                ),
            ],
        }

    def build_route_conventions_rules(self) -> dict:
        return {
            "ruleSetName": "route-conventions-rules",
            "description": "Defines route naming, route-handler responsibilities, and API path ownership.",
            "rules": [
                self.rule(
                    "ROUTE-001",
                    "Route paths use centralized constants",
                    "Backend route registries must use centralized API path constants instead of hardcoded route strings.",
                    "ERROR",
                ),
                self.rule(
                    "ROUTE-002",
                    "Route handlers use mapper-created DTOs",
                    "Route handlers must convert path parameters and payloads into request DTOs through mapper functions before calling services.",
                    "ERROR",
                ),
                self.rule(
                    "ROUTE-003",
                    "Routes return consistent JSON envelopes",
                    "Routes should return consistent JSON envelopes containing success, message/error, and resource-specific response fields.",
                    "ERROR",
                ),
                self.rule(
                    "ROUTE-004",
                    "Module routes stay in module registries",
                    "Module-owned routes must be registered in the module route registry rather than the core/platform route registry.",
                    "ERROR",
                ),
                self.rule(
                    "ROUTE-005",
                    "Route paths use kebab-case",
                    "API URL path segments must use kebab-case.",
                    "ERROR",
                ),
                self.rule(
                    "ROUTE-006",
                    "Routes should remain transport-focused",
                    "Route handlers should focus on HTTP transport concerns such as request reading, validation coordination, DTO mapping, authentication/authorization integration, and response sending, while delegating business workflows to services.",
                    "ERROR",
                ),
            ],
        }

    def build_dto_rules(self) -> dict:
        return {
            "ruleSetName": "dto-rules",
            "description": "Defines DTO responsibilities, boundaries, naming, and usage rules across routes, services, repositories, and API contracts.",
            "rules": [
                self.rule(
                    "DTO-001",
                    "Routes must use DTOs",
                    "Route handlers must map request payloads and path parameters into typed request DTOs before calling services.",
                    "ERROR",
                ),
                self.rule(
                    "DTO-002",
                    "Services must receive DTOs",
                    "Service methods must receive typed DTO/request objects instead of primitive parameter lists or raw request dictionaries.",
                    "ERROR",
                ),
                self.rule(
                    "DTO-003",
                    "Repositories must receive DTOs or domain objects",
                    "Repositories must receive typed request DTOs or domain objects instead of raw transport payload dictionaries.",
                    "ERROR",
                ),
                self.rule(
                    "DTO-004",
                    "DTOs use snake_case internally",
                    "DTO properties must use snake_case internally in Python/backend code.",
                    "ERROR",
                ),
                self.rule(
                    "DTO-005",
                    "DTO mapping belongs to mapper layer",
                    "Conversion between API payloads, DTOs, domain objects, and response dictionaries must be centralized in mapper classes/functions.",
                    "ERROR",
                ),
                self.rule(
                    "DTO-006",
                    "DTOs must be responsibility-specific",
                    "DTOs should represent a specific use case or operation and should avoid becoming large generic transport objects reused across unrelated operations.",
                    "WARNING",
                ),
            ],
        }

    def build_repository_rules(self) -> dict:
        return {
            "ruleSetName": "repository-rules",
            "description": "Defines repository responsibilities, persistence boundaries, and forbidden repository dependencies.",
            "rules": [
                self.rule(
                    "REPOSITORY-001",
                    "Repositories own SQL",
                    "SQL statements and direct database operations must live in repositories or dedicated persistence infrastructure.",
                    "ERROR",
                ),
                self.rule(
                    "REPOSITORY-002",
                    "Repositories do not know HTTP",
                    "Repositories must not import route utilities, handlers, frontend field names, or HTTP request/response concepts.",
                    "ERROR",
                ),
                self.rule(
                    "REPOSITORY-003",
                    "Repositories return domain-level data",
                    "Repositories should return domain objects, DTOs, booleans, or repository-level results, not transport response dictionaries.",
                    "ERROR",
                ),
                self.rule(
                    "REPOSITORY-004",
                    "Repositories map rows centrally",
                    "Database row to domain object conversion should be centralized through mapper functions or repository-owned mapping helpers.",
                    "ERROR",
                ),
                self.rule(
                    "REPOSITORY-005",
                    "Repositories accept typed inputs",
                    "Repository methods should accept DTOs or domain objects rather than primitive parameter lists when a use case has structured input.",
                    "ERROR",
                ),
                self.rule(
                    "REPOSITORY-006",
                    "Repositories should avoid business orchestration",
                    "Repositories should focus on persistence operations and data retrieval/update logic and should not coordinate multi-step business workflows or application orchestration.",
                    "WARNING",
                ),
            ],
        }

    def build_service_rules(self) -> dict:
        return {
            "ruleSetName": "service-rules",
            "description": "Defines service-layer responsibilities and prevents business orchestration from leaking into transport or persistence concerns.",
            "rules": [
                self.rule(
                    "SERVICE-001",
                    "Services must not build raw API response dictionaries",
                    "Services must not construct frontend/API transport payload dictionaries.",
                    "ERROR",
                ),
                self.rule(
                    "SERVICE-002",
                    "Services must not contain SQL",
                    "Services must not contain SQL statements or direct database cursor operations.",
                    "ERROR",
                ),
                self.rule(
                    "SERVICE-003",
                    "Services must not parse raw request dictionaries",
                    "Services must receive DTOs/domain objects from route/mapper boundaries rather than raw HTTP payload dictionaries.",
                    "ERROR",
                ),
                self.rule(
                    "SERVICE-004",
                    "Services must not manually define API/frontend field names",
                    "Services must not know camelCase frontend/API field names or manually construct transport fields.",
                    "ERROR",
                ),
                self.rule(
                    "SERVICE-005",
                    "Services return domain-level results",
                    "Services should return domain objects, DTOs, booleans, lists, or use-case result objects rather than HTTP responses.",
                    "ERROR",
                ),
                self.rule(
                    "SERVICE-006",
                    "Services should coordinate use cases, not infrastructure",
                    "Services should orchestrate business use cases and coordinate repositories, validators, domain operations, and infrastructure abstractions without becoming infrastructure implementations themselves.",
                    "WARNING",
                ),
            ],
        }

    def build_mapper_rules(self) -> dict:
        return {
            "ruleSetName": "mapper-rules",
            "description": "Defines mapper responsibilities for conversion between API payloads, DTOs, domain objects, rows, and response dictionaries.",
            "rules": [
                self.rule(
                    "MAPPER-001",
                    "Mappers convert API payloads to DTOs",
                    "Request payload and path data must be converted to DTOs through mapper functions.",
                    "ERROR",
                ),
                self.rule(
                    "MAPPER-002",
                    "Mappers convert domain objects to responses",
                    "API response dictionaries should be produced through mapper or contract utilities.",
                    "ERROR",
                ),
                self.rule(
                    "MAPPER-003",
                    "Mappers own naming conversion",
                    "camelCase to snake_case and snake_case to camelCase conversion must happen at mapper/contract boundaries.",
                    "ERROR",
                ),
                self.rule(
                    "MAPPER-004",
                    "Mappers should be reusable",
                    "Mapping logic should be centralized and reusable rather than duplicated in routes, services, or repositories.",
                    "WARNING",
                ),
                self.rule(
                    "MAPPER-005",
                    "Mappers must remain transformation-focused",
                    "Mappers should only perform structural/data transformation and must not contain orchestration logic, persistence logic, or business decision-making.",
                    "ERROR",
                ),
            ],
        }

    def build_validator_rules(self) -> dict:
        return {
            "ruleSetName": "validator-rules",
            "description": "Defines validation responsibilities and placement.",
            "rules": [
                self.rule(
                    "VALIDATOR-001",
                    "Validators validate external input",
                    "Incoming request payloads must be validated before they are mapped into service request DTOs.",
                    "ERROR",
                ),
                self.rule(
                    "VALIDATOR-002",
                    "Validators use API boundary names",
                    "Payload validators at the route/API boundary must validate camelCase JSON field names.",
                    "ERROR",
                ),
                self.rule(
                    "VALIDATOR-003",
                    "Validators centralize reusable validation",
                    "Reusable validation logic must live in validator modules/classes rather than being duplicated in route handlers.",
                    "ERROR",
                ),
                self.rule(
                    "VALIDATOR-004",
                    "Validators do not perform persistence",
                    "Validators must not contain SQL or direct repository persistence logic.",
                    "ERROR",
                ),
                self.rule(
                    "VALIDATOR-005",
                    "Validators should remain rule-focused",
                    "Validators should focus on validation concerns only and should not perform orchestration, transport formatting, persistence coordination, or business workflow execution.",
                    "WARNING",
                ),
            ],
        }

    def build_frontend_architecture_rules(self) -> dict:
        return {
            "ruleSetName": "frontend-architecture-rules",
            "description": "Defines frontend architecture rules for page controllers, shared utilities, endpoint usage, and modularity.",
            "rules": [
                self.rule(
                    "FRONTEND-001",
                    "Page controllers use shared API utilities",
                    "Frontend page controllers must use shared API helper functions rather than raw fetch calls where project utilities exist.",
                    "ERROR",
                ),
                self.rule(
                    "FRONTEND-002",
                    "Page controllers use shared endpoint registry",
                    "Frontend page controllers must use LLA_API_ENDPOINTS or equivalent shared endpoint registries for backend calls.",
                    "ERROR",
                ),
                self.rule(
                    "FRONTEND-003",
                    "Page controllers use shared path registry",
                    "Frontend navigation should use the shared frontend path registry instead of hardcoded page URLs when a path exists there.",
                    "WARNING",
                ),
                self.rule(
                    "FRONTEND-004",
                    "Frontend files should remain responsibility-focused",
                    "Large frontend files should be split into smaller responsibility-based modules when they become difficult to maintain.",
                    "WARNING",
                ),
                self.rule(
                    "FRONTEND-005",
                    "Frontend must escape rendered data",
                    "Dynamic data rendered into HTML strings must be escaped using shared escaping utilities.",
                    "ERROR",
                ),
                self.rule(
                    "FRONTEND-006",
                    "Frontend pages should separate rendering from orchestration",
                    "DOM rendering, state management, navigation, API communication, and interaction orchestration should be separated into focused modules/helpers when frontend complexity grows.",
                    "WARNING",
                ),
            ],
        }

    def build_css_architecture_rules(self) -> dict:
        return {
            "ruleSetName": "css-architecture-rules",
            "description": "Defines CSS architecture rules for shared layout, reusable components, page-specific styling, and future theming.",
            "rules": [
                self.rule(
                    "CSS-001",
                    "Prefer shared CSS for reusable UI patterns",
                    "Reusable layout, tables, forms, buttons, panels, cards, spacing, and theme primitives should live in shared CSS files.",
                    "ERROR",
                ),
                self.rule(
                    "CSS-002",
                    "Page CSS is only for page-specific styling",
                    "Page-level CSS should only contain styling that is genuinely unique to that page.",
                    "WARNING",
                ),
                self.rule(
                    "CSS-003",
                    "Avoid duplicated page overrides",
                    "Repeated page-level overrides should be moved into shared CSS or design-system files.",
                    "WARNING",
                ),
                self.rule(
                    "CSS-004",
                    "Use content-driven protected layouts where appropriate",
                    "Protected desktop content panels should generally be content-driven in width unless there is a clear layout reason to stretch.",
                    "WARNING",
                ),
                self.rule(
                    "CSS-005",
                    "Avoid inline styles",
                    "Inline styles should be avoided except for dynamic runtime-calculated styling that cannot reasonably live in CSS classes.",
                    "WARNING",
                ),
            ],
        }

    def build_api_contract_rules(self) -> dict:
        return {
            "ruleSetName": "api-contract-rules",
            "description": "Defines API contract rules for frontend/backend alignment, payload naming, and endpoint governance.",
            "rules": [
                self.rule(
                    "API-001",
                    "API JSON uses camelCase",
                    "External API request and response JSON fields must use camelCase.",
                    "ERROR",
                ),
                self.rule(
                    "API-002",
                    "Frontend endpoints must match backend routes",
                    "Frontend endpoint registry entries must match backend API path constants and registered routes.",
                    "ERROR",
                ),
                self.rule(
                    "API-003",
                    "API paths are centralized",
                    "Backend API path strings must be defined in centralized API path files.",
                    "ERROR",
                ),
                self.rule(
                    "API-004",
                    "Response envelopes are consistent",
                    "API responses should use consistent success/error/message/data envelope patterns.",
                    "WARNING",
                ),
                self.rule(
                    "API-005",
                    "Backend and frontend endpoint contracts must be inspectable",
                    "Frontend and backend endpoint definitions should be structured so they can be extracted, compared, and validated automatically by inspection scripts.",
                    "WARNING",
                ),
            ],
        }

    def build_inspection_framework_rules(self) -> dict:
        return {
            "ruleSetName": "inspection-framework-rules",
            "description": "Defines architecture rules for inspection scripts, governance checks, and future rule-engine evolution.",
            "rules": [
                self.rule(
                    "INSPECTION-001",
                    "Inspection scripts use rule catalogues",
                    "Inspection scripts should read rule definitions from JSON rule catalogues rather than embedding rule metadata only in code.",
                    "ERROR",
                ),
                self.rule(
                    "INSPECTION-002",
                    "Entity-specific deviations use overrides",
                    "Entity-specific CRUD deviations must be represented through ruleOverrides rather than hardcoded exceptions.",
                    "ERROR",
                ),
                self.rule(
                    "INSPECTION-003",
                    "Disabled rules are reported",
                    "Disabled rules must produce structured findings explaining that the rule is disabled and why.",
                    "ERROR",
                ),
                self.rule(
                    "INSPECTION-004",
                    "Console output stays concise",
                    "Inspection scripts should print one-line terminal summaries and write detailed reports to output folders.",
                    "WARNING",
                ),
                self.rule(
                    "INSPECTION-005",
                    "Inspection framework evolves toward generic rule evaluation",
                    "Inspection scripts should move toward reusable rule evaluation infrastructure rather than isolated ad-hoc checks.",
                    "WARNING",
                ),
                self.rule(
                    "INSPECTION-006",
                    "Inspection scripts must separate rule definitions from rule execution",
                    "Rule metadata/configuration should remain externalized from rule execution logic so the framework can evolve toward reusable rule engines and DSL-style inspection architectures.",
                    "WARNING",
                ),
            ],
        }

    def build_rule_file_content(self, file_name: str) -> dict:
        content_builders = {
            "naming-convention-rules.json": self.build_naming_convention_rules,
            "hardcoding-rules.json": self.build_hardcoding_rules,
            "scripting-blueprint-rules.json": self.build_scripting_blueprint_rules,
            "layering-rules.json": self.build_layering_rules,
            "route-conventions-rules.json": self.build_route_conventions_rules,
            "dto-rules.json": self.build_dto_rules,
            "repository-rules.json": self.build_repository_rules,
            "service-rules.json": self.build_service_rules,
            "mapper-rules.json": self.build_mapper_rules,
            "validator-rules.json": self.build_validator_rules,
            "frontend-architecture-rules.json": self.build_frontend_architecture_rules,
            "css-architecture-rules.json": self.build_css_architecture_rules,
            "api-contract-rules.json": self.build_api_contract_rules,
            "inspection-framework-rules.json": self.build_inspection_framework_rules,
        }

        builder = content_builders.get(file_name)

        if builder is None:
            raise ValueError(f"No rule builder configured for '{file_name}'.")

        return builder()

    def run(self) -> None:
        target_folder = self.project_root / self.get_target_folder()

        target_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        written_files = []

        for file_name in self.get_rule_files():
            file_path = target_folder / file_name

            write_json_file(
                file_path,
                self.build_rule_file_content(file_name),
            )

            written_files.append(self.to_project_relative_path(file_path))

        output_file_path = self.output_directory / self.get_output_file_name()

        write_json_file(
            output_file_path,
            {
                "success": True,
                "targetFolder": self.to_project_relative_path(target_folder),
                "writtenFileCount": len(written_files),
                "writtenFiles": written_files,
            },
        )

        print_passed(
            (
                "Blueprint rules written. "
                f"Files: {len(written_files)}. "
                "Output: "
                f"{self.to_project_relative_path(output_file_path)}"
            )
        )


def main() -> None:
    try:
        WriteBlueprintRules().run()

    except Exception as error:
        print_failed(str(error))


if __name__ == "__main__":
    main()

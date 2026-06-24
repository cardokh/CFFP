from __future__ import annotations

import hashlib
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.factory.context_compiler.context_compiler_contracts import ProviderResult
from scripts.factory.context_compiler.context_compiler_providers import (
    ApprovedDocumentSetProvider,
    GoldenReferenceProvider,
    RepositoryInspectionProvider,
)
from scripts.shared.base_script import BaseScript
from scripts.shared.script_json_utils import write_json_file


PROVIDER_TYPES = {
    "approved-document-set": ApprovedDocumentSetProvider,
    "golden-reference": GoldenReferenceProvider,
    "repository-inspection": RepositoryInspectionProvider,
}


class MasterContextCompiler(BaseScript):
    """Compiles approved provider context into one deterministic master-context.md file."""

    def __init__(self):
        super().__init__(__file__)
        self.provider_results: list[ProviderResult] = []

    def run(self) -> None:
        output_config = self.config.get("outputs", {})
        master_context_path = self.project_root / output_config["masterContextPath"]
        report_path = self.project_root / output_config["reportPath"]

        provider_results = self._collect_provider_results()
        master_context = self._render_master_context(provider_results)
        report = self._build_report(provider_results, master_context, master_context_path)

        self._write_text_file(master_context_path, master_context)
        write_json_file(report_path, report)

        print(
            f"PASS {self.script_name}: compiled {report['summary']['includedItemCount']} context item(s)"
        )

    def _collect_provider_results(self) -> list[ProviderResult]:
        provider_results = []

        for provider_config in self.config.get("providers", []):
            provider_type = provider_config["type"]
            provider_class = PROVIDER_TYPES.get(provider_type)

            if provider_class is None:
                raise ValueError(f"Unknown context provider type: {provider_type}")

            provider = provider_class()
            provider_results.append(
                provider.collect(
                    self.project_root,
                    provider_config.get("config", {}),
                )
            )

        return provider_results

    def _render_master_context(
        self,
        provider_results: list[ProviderResult],
    ) -> str:
        lines = [
            "# CFFP Master Context",
            "",
            "## Compilation Identity",
            "",
            f"- compiler: `{self.config.get('compilerName', self.script_name)}`",
            f"- target: `{self.config.get('target', 'unspecified')}`",
            f"- version: `{self.config.get('compilerVersion', '1.0')}`",
            "",
            "## Provider Summary",
            "",
        ]

        for provider_result in provider_results:
            lines.append(
                f"- `{provider_result.provider_id}`: included={len(provider_result.included_items)}, excluded={len(provider_result.excluded_inputs)}, findings={len(provider_result.findings)}"
            )

        for provider_result in provider_results:
            lines.extend(
                [
                    "",
                    f"## Provider: {provider_result.provider_id}",
                    "",
                    "### Included Context Items",
                    "",
                ]
            )

            for item in provider_result.included_items:
                lines.extend(
                    [
                        f"#### {item.title}",
                        "",
                        f"- source: `{item.source_path}`",
                        f"- sha256: `{item.metadata.get('sha256', 'not-applicable')}`",
                        f"- lines: `{item.metadata.get('lineCount', 'not-applicable')}`",
                        "",
                        "```text",
                        item.content.rstrip("\n"),
                        "```",
                        "",
                    ]
                )

            lines.extend(["### Excluded Inputs", ""])

            if provider_result.excluded_inputs:
                for excluded_input in sorted(provider_result.excluded_inputs, key=lambda item: item["path"]):
                    lines.append(
                        f"- `{excluded_input['path']}` — {excluded_input['reason']}"
                    )
            else:
                lines.append("- None")

            lines.extend(["", "### Findings", ""])

            if provider_result.findings:
                for finding in provider_result.findings:
                    lines.append(
                        f"- {finding['status']} [{finding['severity']}] `{finding['path']}` — {finding['message']}"
                    )
            else:
                lines.append("- None")

        lines.append("")
        return "\n".join(lines)

    def _build_report(
        self,
        provider_results: list[ProviderResult],
        master_context: str,
        master_context_path: Path,
    ) -> dict:
        included_items = []
        excluded_inputs = []
        findings = []

        for provider_result in provider_results:
            for item in provider_result.included_items:
                included_items.append(
                    {
                        "providerId": item.provider_id,
                        "title": item.title,
                        "sourcePath": item.source_path,
                        "metadata": item.metadata,
                    }
                )

            for excluded_input in provider_result.excluded_inputs:
                excluded_inputs.append(
                    {
                        "providerId": provider_result.provider_id,
                        **excluded_input,
                    }
                )

            for finding in provider_result.findings:
                findings.append(
                    {
                        "providerId": provider_result.provider_id,
                        **finding,
                    }
                )

        status = "PASSED"
        if any(finding.get("status") == "FAILED" for finding in findings):
            status = "FAILED"

        return {
            "compiler": {
                "name": self.config.get("compilerName", self.script_name),
                "version": self.config.get("compilerVersion", "1.0"),
                "target": self.config.get("target", "unspecified"),
            },
            "summary": {
                "status": status,
                "masterContextPath": self.to_project_relative_path(master_context_path),
                "masterContextSha256": self._sha256(master_context),
                "includedItemCount": len(included_items),
                "excludedInputCount": len(excluded_inputs),
                "findingCount": len(findings),
            },
            "providers": [
                {
                    "providerId": provider_result.provider_id,
                    "summary": provider_result.summary,
                }
                for provider_result in provider_results
            ],
            "includedInputs": sorted(included_items, key=lambda item: (item["providerId"], item["sourcePath"])),
            "excludedInputs": sorted(excluded_inputs, key=lambda item: (item["providerId"], item["path"])),
            "findings": findings,
        }

    def _write_text_file(self, file_path: Path, content: str) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8", newline="\n")

    def _sha256(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    MasterContextCompiler().run()

"""
Reference data application service.

Responsibilities:
- Coordinate lookup/reference data use cases
- Provide admin form options for dropdowns
- Keep API handlers separate from reference data repositories

Architecture:
API -> ReferenceDataService -> ReferenceDataRepository -> SQLite Database
"""


class ReferenceDataService:
    def __init__(self, reference_data_repository):
        self.reference_data_repository = reference_data_repository

    def get_lesson_form_options(self):
        return {
            "lesson_categories": (
                self.reference_data_repository.find_active_lesson_categories()
            ),
            "lesson_types": (self.reference_data_repository.find_active_lesson_types()),
            "embodiment_types": (
                self.reference_data_repository.find_active_embodiment_types()
            ),
            "interaction_styles": (
                self.reference_data_repository.find_active_interaction_styles()
            ),
        }

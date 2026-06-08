"""
Student progress mapper.

Responsibilities:
- Convert student progress domain objects into response contracts.
- Centralize mapping logic between architectural layers.

Architecture:
Domain <-> Mapper <-> Contracts
"""

from src.modules.lla.student_progress.student_progress import (
    StudentProgressOverview,
)
from src.modules.lla.student_progress.student_progress_contracts import (
    StudentProgressOverviewDetails,
)


class StudentProgressMapper:
    @staticmethod
    def domain_to_details(
        overview: StudentProgressOverview,
    ) -> StudentProgressOverviewDetails:
        return StudentProgressOverviewDetails.from_domain(
            overview,
        )

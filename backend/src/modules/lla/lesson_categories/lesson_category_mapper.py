"""
Lesson category mapper.

Responsibilities:
- Convert lesson category request contracts into domain objects.
- Convert lesson category domain objects into response contracts.
- Centralize mapping logic between architectural layers.

Architecture:
Contracts <-> Mapper <-> Domain
"""

from src.modules.lla.lesson_categories.lesson_category import LessonCategory
from src.modules.lla.lesson_categories.lesson_category_contracts import (
    CreateLessonCategoryRequest,
    LessonCategoryDetails,
    UpdateLessonCategoryRequest,
)


class LessonCategoryMapper:
    @staticmethod
    def create_request_to_domain(
        request: CreateLessonCategoryRequest,
    ) -> LessonCategory:
        return LessonCategory(
            category_id=None,
            name=request.cleaned_name,
            description=request.cleaned_description,
            is_active=request.is_active,
            updated_by=request.cleaned_updated_by,
        )

    @staticmethod
    def update_request_to_domain(
        request: UpdateLessonCategoryRequest,
    ) -> LessonCategory:
        return LessonCategory(
            category_id=request.category_id,
            name=request.cleaned_name,
            description=request.cleaned_description,
            is_active=request.is_active,
            updated_by=request.cleaned_updated_by,
        )

    @staticmethod
    def category_id_to_domain(category_id: int) -> LessonCategory:
        return LessonCategory(
            category_id=category_id,
            name="",
            description=None,
            is_active=True,
        )

    @staticmethod
    def category_name_to_domain(name: str) -> LessonCategory:
        return LessonCategory(
            category_id=None,
            name=name,
            description=None,
            is_active=True,
        )

    @staticmethod
    def domain_to_details(
        lesson_category: LessonCategory,
    ) -> LessonCategoryDetails:
        return LessonCategoryDetails.from_domain(lesson_category)

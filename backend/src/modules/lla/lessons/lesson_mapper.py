"""
Lesson mapper.

Responsibilities:
- Convert lesson request contracts into domain objects.
- Convert lesson domain objects into response contracts.
- Centralize mapping logic between architectural layers.

Architecture:
Contracts <-> Mapper <-> Domain
"""

from src.modules.lla.lessons.lesson import Lesson
from src.modules.lla.lessons.lesson_contracts import (
    CreateLessonRequest,
    LessonDetails,
    UpdateLessonRequest,
)


class LessonMapper:
    @staticmethod
    def create_request_to_domain(
        request: CreateLessonRequest,
    ) -> Lesson:
        return Lesson(
            lesson_id=None,
            category_id=request.category_id,
            lesson_type_id=request.lesson_type_id,
            embodiment_type_id=request.embodiment_type_id,
            interaction_style_id=request.interaction_style_id,
            title=request.cleaned_title,
            description=request.cleaned_description,
            is_active=request.is_active,
            updated_by=request.cleaned_updated_by,
        )

    @staticmethod
    def update_request_to_domain(
        request: UpdateLessonRequest,
    ) -> Lesson:
        return Lesson(
            lesson_id=request.lesson_id,
            category_id=request.category_id,
            lesson_type_id=request.lesson_type_id,
            embodiment_type_id=request.embodiment_type_id,
            interaction_style_id=request.interaction_style_id,
            title=request.cleaned_title,
            description=request.cleaned_description,
            is_active=request.is_active,
            updated_by=request.cleaned_updated_by,
        )

    @staticmethod
    def lesson_id_to_domain(
        lesson_id: int,
    ) -> Lesson:
        return Lesson(
            lesson_id=lesson_id,
            category_id=0,
            lesson_type_id=0,
            embodiment_type_id=0,
            interaction_style_id=0,
            title="",
            description=None,
            is_active=True,
        )

    @staticmethod
    def domain_to_details(
        lesson: Lesson,
    ) -> LessonDetails:
        return LessonDetails.from_domain(lesson)

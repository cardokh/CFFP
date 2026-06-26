"""
Application service factory.

Responsibilities:
- Build application services with their required dependencies.
- Keep API handlers free from repository/database construction details.
- Centralize service, repository, validator, mapper, and assignment service construction.

Architecture:
API -> Service Factory -> Services -> Repositories -> Database
"""

from backend.src.ccore.shared.app_config import DATABASE_PATH, get_app_setting
from backend.src.ccore.shared.app_path_utils import get_path

from backend.src.ccore.automation.services import TaskExecutionService

from src.core.ai.ai_speech.ai_speech_provider_mapper import (
    AiSpeechProviderMapper,
)
from src.core.ai.ai_speech.ai_speech_result_factory import (
    AiSpeechResultFactory,
)
from src.core.ai.ai_speech.ai_speech_service import AiSpeechService
from src.core.ai.ai_speech.ai_speech_validator import AiSpeechValidator
from backend.src.ccore.infrastructure.database import (
    DatabaseManager,
    PostgresDatabaseManager,
)

from backend.src.ccore.metrics.metric_repository import (
    CCoreMetricRepository,
    CCoreMetricTypeRepository,
)
from backend.src.ccore.metrics.metric_service import (
    CCoreMetricService,
    CCoreMetricTypeService,
)
from backend.src.ccore.metrics.metric_validator import CCoreMetricValidator
from backend.src.ccore.pipelines.pipeline_repository import (
    CCorePipelineRepository,
    CCorePipelineStatusRepository,
)
from backend.src.ccore.pipelines.pipeline_service import (
    CCorePipelineService,
    CCorePipelineStatusService,
)
from backend.src.ccore.pipelines.pipeline_validator import CCorePipelineValidator

from backend.src.ccore.tasks.task_repository import (
    CCoreTaskRepository,
    CCoreTaskStatusRepository,
)
from backend.src.ccore.tasks.task_execution_repository import (
    CCoreTaskExecutionRepository,
)
from backend.src.ccore.tasks.task_service import (
    CCoreTaskService,
    CCoreTaskStatusService,
)
from backend.src.ccore.tasks.task_validator import CCoreTaskValidator
from src.core.users.password_service import PasswordService
from src.core.users.user_repository import UserRepository
from src.core.users.user_service import UserService
from src.core.users.user_validator import UserValidator

from src.modules.lla.learning_items.learning_item_example_generator import (
    LearningItemExampleGenerator,
)
from src.modules.lla.learning_items.learning_item_repository import (
    LearningItemRepository,
)
from src.modules.lla.learning_items.learning_item_service import LearningItemService
from src.modules.lla.learning_items.learning_item_validator import (
    LearningItemValidator,
)
from src.modules.lla.lesson_categories.lesson_category_repository import (
    LessonCategoryRepository,
)
from src.modules.lla.lesson_categories.lesson_category_service import (
    LessonCategoryService,
)
from src.modules.lla.lesson_categories.lesson_category_validator import (
    LessonCategoryValidator,
)
from src.modules.lla.lessons.lesson_learning_item_assignment_repository import (
    LessonLearningItemAssignmentRepository,
)
from src.modules.lla.lessons.lesson_learning_item_assignment_service import (
    LessonLearningItemAssignmentService,
)
from src.modules.lla.lessons.lesson_learning_item_assignment_validator import (
    LessonLearningItemAssignmentValidator,
)
from src.modules.lla.lessons.lesson_quiz_question_assignment_repository import (
    LessonQuizQuestionAssignmentRepository,
)
from src.modules.lla.lessons.lesson_quiz_question_assignment_service import (
    LessonQuizQuestionAssignmentService,
)
from src.modules.lla.lessons.lesson_quiz_question_assignment_validator import (
    LessonQuizQuestionAssignmentValidator,
)
from src.modules.lla.lessons.lesson_repository import LessonRepository
from src.modules.lla.lessons.lesson_service import LessonService
from src.modules.lla.lessons.lesson_validator import LessonValidator
from src.modules.lla.quiz_questions.quiz_question_option_repository import (
    QuizQuestionOptionRepository,
)
from src.modules.lla.quiz_questions.quiz_question_option_service import (
    QuizQuestionOptionService,
)
from src.modules.lla.quiz_questions.quiz_question_option_validator import (
    QuizQuestionOptionValidator,
)
from src.modules.lla.quiz_questions.quiz_question_repository import (
    QuizQuestionRepository,
)
from src.modules.lla.quiz_questions.quiz_question_service import (
    QuizQuestionService,
)
from src.modules.lla.quiz_questions.quiz_question_validator import (
    QuizQuestionValidator,
)
from src.modules.lla.reference_data.reference_data_repository import (
    ReferenceDataRepository,
)
from src.modules.lla.reference_data.reference_data_service import (
    ReferenceDataService,
)
from src.modules.lla.user_lesson_assignments.user_lesson_assignment_repository import (
    UserLessonAssignmentRepository,
)
from src.modules.lla.user_lesson_assignments.user_lesson_assignment_service import (
    UserLessonAssignmentService,
)
from src.modules.lla.user_lesson_assignments.user_lesson_assignment_validator import (
    UserLessonAssignmentValidator,
)
from src.modules.lla.student_progress.student_progress_repository import (
    StudentProgressRepository,
)
from src.modules.lla.student_progress.student_progress_service import (
    StudentProgressService,
)


def build_database_manager():
    return DatabaseManager(DATABASE_PATH)


def build_postgres_database_manager():
    return PostgresDatabaseManager()


def build_ccore_task_repositories():
    postgres_database_manager = build_postgres_database_manager()

    return (
        CCoreTaskRepository(postgres_database_manager),
        CCoreTaskStatusRepository(postgres_database_manager),
        CCoreTaskExecutionRepository(postgres_database_manager),
    )


def build_ccore_task_service():
    task_repository, status_repository, task_execution_repository = (
        build_ccore_task_repositories()
    )
    task_validator = CCoreTaskValidator(status_repository=status_repository)

    return CCoreTaskService(
        task_repository=task_repository,
        task_validator=task_validator,
        task_execution_repository=task_execution_repository,
    )


def build_task_execution_service(
    ccore_task_service: CCoreTaskService,
):
    return TaskExecutionService(
        ccore_task_service=ccore_task_service,
    )


def build_ccore_task_status_service():
    _, status_repository, _ = build_ccore_task_repositories()

    return CCoreTaskStatusService(
        status_repository=status_repository,
    )


def build_ccore_metric_repositories():
    postgres_database_manager = build_postgres_database_manager()

    return (
        CCoreMetricRepository(postgres_database_manager),
        CCoreMetricTypeRepository(postgres_database_manager),
    )


def build_ccore_metric_service():
    metric_repository, type_repository = build_ccore_metric_repositories()
    metric_validator = CCoreMetricValidator(type_repository=type_repository)

    return CCoreMetricService(
        metric_repository=metric_repository,
        metric_validator=metric_validator,
    )


def build_ccore_metric_type_service():
    _, type_repository = build_ccore_metric_repositories()

    return CCoreMetricTypeService(
        type_repository=type_repository,
    )


def build_ccore_pipeline_repositories():
    postgres_database_manager = build_postgres_database_manager()

    return (
        CCorePipelineRepository(postgres_database_manager),
        CCorePipelineStatusRepository(postgres_database_manager),
    )


def build_ccore_pipeline_service():
    pipeline_repository, status_repository = build_ccore_pipeline_repositories()
    pipeline_validator = CCorePipelineValidator(status_repository=status_repository)

    return CCorePipelineService(
        pipeline_repository=pipeline_repository,
        pipeline_validator=pipeline_validator,
    )


def build_ccore_pipeline_status_service():
    _, status_repository = build_ccore_pipeline_repositories()

    return CCorePipelineStatusService(
        status_repository=status_repository,
    )

def build_ai_speech_provider_mapper():
    return AiSpeechProviderMapper()


def build_ai_speech_result_factory():
    return AiSpeechResultFactory()


def build_ai_speech_validator():
    return AiSpeechValidator()


def build_ai_speech_service():
    ai_speech_provider_mapper = build_ai_speech_provider_mapper()

    ai_speech_result_factory = build_ai_speech_result_factory()

    return AiSpeechService(
        ai_speech_provider_mapper=ai_speech_provider_mapper,
        ai_speech_result_factory=ai_speech_result_factory,
    )


def build_users_service():
    database_manager = build_database_manager()

    user_repository = UserRepository(database_manager)
    user_validator = UserValidator()
    password_service = PasswordService()

    return UserService(
        user_repository=user_repository,
        user_validator=user_validator,
        password_service=password_service,
    )


def build_lesson_category_service():
    database_manager = build_database_manager()

    lesson_category_repository = LessonCategoryRepository(database_manager)

    lesson_category_validator = LessonCategoryValidator(
        lesson_category_repository,
    )

    return LessonCategoryService(
        lesson_category_repository=lesson_category_repository,
        lesson_category_validator=lesson_category_validator,
    )


def build_learning_item_example_generator():
    return LearningItemExampleGenerator()


def build_learning_item_service():
    database_manager = build_database_manager()

    learning_item_repository = LearningItemRepository(database_manager)

    learning_item_validator = LearningItemValidator(
        learning_item_repository,
    )

    learning_item_example_generator = build_learning_item_example_generator()

    return LearningItemService(
        learning_item_repository=learning_item_repository,
        learning_item_validator=learning_item_validator,
        learning_item_example_generator=learning_item_example_generator,
    )


def build_quiz_question_service():
    database_manager = build_database_manager()

    quiz_question_repository = QuizQuestionRepository(database_manager)

    quiz_question_validator = QuizQuestionValidator(
        quiz_question_repository,
    )

    return QuizQuestionService(
        quiz_question_repository=quiz_question_repository,
        quiz_question_validator=quiz_question_validator,
    )


def build_quiz_question_option_service():
    database_manager = build_database_manager()

    quiz_question_option_repository = QuizQuestionOptionRepository(
        database_manager,
    )

    quiz_question_option_validator = QuizQuestionOptionValidator()

    return QuizQuestionOptionService(
        quiz_question_option_repository=quiz_question_option_repository,
        quiz_question_option_validator=quiz_question_option_validator,
    )


def build_lesson_service():
    database_manager = build_database_manager()

    lesson_repository = LessonRepository(database_manager)
    lesson_validator = LessonValidator()

    return LessonService(
        lesson_repository=lesson_repository,
        lesson_validator=lesson_validator,
    )


def build_lesson_learning_item_assignment_service():
    database_manager = build_database_manager()

    assignment_repository = LessonLearningItemAssignmentRepository(
        database_manager,
    )

    assignment_validator = LessonLearningItemAssignmentValidator()

    return LessonLearningItemAssignmentService(
        assignment_repository=assignment_repository,
        assignment_validator=assignment_validator,
    )


def build_lesson_quiz_question_assignment_service():
    database_manager = build_database_manager()

    assignment_repository = LessonQuizQuestionAssignmentRepository(
        database_manager,
    )

    assignment_validator = LessonQuizQuestionAssignmentValidator()

    quiz_question_option_service = build_quiz_question_option_service()

    return LessonQuizQuestionAssignmentService(
        assignment_repository=assignment_repository,
        assignment_validator=assignment_validator,
        quiz_question_option_service=quiz_question_option_service,
    )


def build_user_lesson_assignment_service():
    database_manager = build_database_manager()

    user_lesson_assignment_repository = UserLessonAssignmentRepository(
        database_manager,
    )

    user_lesson_assignment_validator = UserLessonAssignmentValidator()

    return UserLessonAssignmentService(
        user_lesson_assignment_repository=user_lesson_assignment_repository,
        user_lesson_assignment_validator=user_lesson_assignment_validator,
    )


def build_reference_data_service():
    database_manager = build_database_manager()

    reference_data_repository = ReferenceDataRepository(database_manager)

    return ReferenceDataService(
        reference_data_repository=reference_data_repository,
    )


def build_student_progress_service():
    database_manager = build_database_manager()

    student_progress_repository = StudentProgressRepository(
        database_manager,
    )

    return StudentProgressService(
        student_progress_repository=student_progress_repository,
    )

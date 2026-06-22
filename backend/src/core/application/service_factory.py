"""
Application service factory.

Responsibilities:
- Build application services with their required dependencies.
- Keep API handlers free from repository/database construction details.
- Centralize service, repository, validator, mapper, and assignment service construction.

Architecture:
API -> Service Factory -> Services -> Repositories -> Database
"""

from src.core.shared.app_config import DATABASE_PATH, get_app_setting
from src.core.shared.app_path_utils import get_path

from src.core.ai.ai_speech.ai_speech_provider_mapper import (
    AiSpeechProviderMapper,
)
from src.core.ai.ai_speech.ai_speech_result_factory import (
    AiSpeechResultFactory,
)
from src.core.ai.ai_speech.ai_speech_service import AiSpeechService
from src.core.ai.ai_speech.ai_speech_validator import AiSpeechValidator
from src.core.infrastructure.database import DatabaseManager, PostgresDatabaseManager
from src.core.automation.automation_pipeline_registry import AutomationPipelineRegistry
from src.core.automation.automation_pipeline_service import AutomationPipelineService
from src.core.automation.automation_task_registry import AutomationTaskRegistry
from src.core.automation.automation_task_service import AutomationTaskService
from src.core.automation.automation_task_execution_service import AutomationTaskExecutionService
from src.core.automation.automation_task_validation import AutomationTaskValidationService

from src.core.tasks.task_repository import CCoreTaskRepository
from src.core.tasks.task_service import CCoreTaskService
from src.core.tasks.task_validator import CCoreTaskValidator
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


def build_ccore_task_service():
    postgres_database_manager = build_postgres_database_manager()

    task_repository = CCoreTaskRepository(postgres_database_manager)
    task_validator = CCoreTaskValidator()

    return CCoreTaskService(
        task_repository=task_repository,
        task_validator=task_validator,
    )


def build_automation_task_registry():
    return AutomationTaskRegistry(
        registry_path=get_path("automationTaskRegistry"),
        project_root=get_path("projectRoot"),
    )


def build_automation_pipeline_registry():
    return AutomationPipelineRegistry(
        registry_path=get_path("automationPipelineRegistry"),
    )


def build_automation_pipeline_service():
    return AutomationPipelineService(
        automation_pipeline_registry=build_automation_pipeline_registry(),
    )


def build_automation_task_validation_service():
    return AutomationTaskValidationService(
        project_root=get_path("projectRoot"),
    )


def build_automation_task_execution_service():
    automation_task_validation_service = build_automation_task_validation_service()

    return AutomationTaskExecutionService(
        project_root=get_path("projectRoot"),
        automation_task_validation_service=automation_task_validation_service,
        execution_report_output_directory=get_path("automationExecutionReportOutputPath"),
        task_artifact_output_directory_name=get_app_setting("automationTaskArtifactOutputDirectoryName"),
        execution_report_schema_version=get_app_setting("automationTaskExecutionReportSchemaVersion"),
        timeout_seconds=get_app_setting("automationTaskExecutionTimeoutSeconds"),
    )


def build_automation_task_service():
    automation_task_validation_service = build_automation_task_validation_service()

    return AutomationTaskService(
        automation_task_registry=build_automation_task_registry(),
        automation_task_validation_service=automation_task_validation_service,
        automation_task_execution_service=build_automation_task_execution_service(),
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

"""Tests for step handlers."""
import pytest
from packages.agent.executor.context import ExecutionContext, Permission
from packages.agent.executor.handlers import StepHandlerRegistry
from packages.agent.executor.handlers_impl import (
    BrowserExecutionHandler,
    CheckEligibilityHandler,
    CompleteHandler,
    DiscoverServiceHandler,
    ExtractDataHandler,
    GetRequirementsHandler,
    HumanReviewHandler,
    PrepareApplicationHandler,
    SubmitHandler,
    TrackApplicationHandler,
    ValidateDocumentsHandler,
    register_default_handlers,
)
from packages.agent.planner.models import StepType, WorkflowStep


@pytest.fixture
def context():
    return ExecutionContext(
        task_id="test-task",
        user_id="user-1",
        service_id="income_certificate",
        permissions=[Permission.BROWSER_NAVIGATION, Permission.READ_PAGE],
    )


@pytest.fixture
def mock_browser_context():
    from packages.browser.mock.agent import MockBrowserAgent
    browser = MockBrowserAgent()
    ctx = ExecutionContext(
        task_id="test-task",
        user_id="user-1",
        service_id="income_certificate",
        permissions=[Permission.BROWSER_NAVIGATION, Permission.READ_PAGE],
    )
    ctx.metadata["browser_agent"] = browser
    ctx.metadata["portal_url"] = "https://example.gov.in"
    return ctx


class TestDiscoverServiceHandler:
    @pytest.mark.asyncio
    async def test_execute(self, context):
        handler = DiscoverServiceHandler()
        step = WorkflowStep(id="discover", type=StepType.DISCOVER_SERVICE)
        result = await handler.execute(step, context)
        assert result["success"] is True
        assert "portal_url" in result

    def test_can_handle(self):
        handler = DiscoverServiceHandler()
        assert handler.can_handle(StepType.DISCOVER_SERVICE)
        assert not handler.can_handle(StepType.SUBMIT)


class TestGetRequirementsHandler:
    @pytest.mark.asyncio
    async def test_execute(self, context):
        handler = GetRequirementsHandler()
        step = WorkflowStep(id="requirements", type=StepType.GET_REQUIREMENTS)
        result = await handler.execute(step, context)
        assert result["success"] is True

    def test_can_handle(self):
        handler = GetRequirementsHandler()
        assert handler.can_handle(StepType.GET_REQUIREMENTS)


class TestCheckEligibilityHandler:
    @pytest.mark.asyncio
    async def test_execute(self, context):
        handler = CheckEligibilityHandler()
        step = WorkflowStep(id="eligibility", type=StepType.CHECK_ELIGIBILITY)
        result = await handler.execute(step, context)
        assert result["success"] is True
        assert result["eligible"] is True


class TestValidateDocumentsHandler:
    @pytest.mark.asyncio
    async def test_execute(self, context):
        handler = ValidateDocumentsHandler()
        step = WorkflowStep(id="documents", type=StepType.VALIDATE_DOCUMENTS)
        result = await handler.execute(step, context)
        assert result["success"] is True


class TestPrepareApplicationHandler:
    @pytest.mark.asyncio
    async def test_execute(self, context):
        handler = PrepareApplicationHandler()
        step = WorkflowStep(id="prepare", type=StepType.PREPARE_APPLICATION)
        result = await handler.execute(step, context)
        assert result["success"] is True


class TestBrowserExecutionHandler:
    @pytest.mark.asyncio
    async def test_execute_with_browser(self, mock_browser_context):
        handler = BrowserExecutionHandler()
        step = WorkflowStep(id="browser", type=StepType.BROWSER_EXECUTION)
        result = await handler.execute(step, mock_browser_context)
        assert result["success"] is True
        assert result.get("simulated") is not True

    @pytest.mark.asyncio
    async def test_execute_without_permission(self, context):
        context.permissions = []
        handler = BrowserExecutionHandler()
        step = WorkflowStep(id="browser", type=StepType.BROWSER_EXECUTION)
        result = await handler.execute(step, context)
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_execute_without_browser(self, context):
        handler = BrowserExecutionHandler()
        step = WorkflowStep(id="browser", type=StepType.BROWSER_EXECUTION)
        result = await handler.execute(step, context)
        assert result["success"] is True
        assert result.get("simulated") is True


class TestExtractDataHandler:
    @pytest.mark.asyncio
    async def test_execute(self, context):
        handler = ExtractDataHandler()
        step = WorkflowStep(id="extract", type=StepType.EXTRACT_DATA)
        result = await handler.execute(step, context)
        assert result["success"] is True
        assert result.get("simulated") is True

    @pytest.mark.asyncio
    async def test_execute_with_browser(self, mock_browser_context):
        handler = ExtractDataHandler()
        step = WorkflowStep(id="extract", type=StepType.EXTRACT_DATA)
        result = await handler.execute(step, mock_browser_context)
        assert result["success"] is True


class TestHumanReviewHandler:
    @pytest.mark.asyncio
    async def test_execute_without_approval(self, context):
        handler = HumanReviewHandler()
        step = WorkflowStep(id="review", type=StepType.HUMAN_REVIEW)
        result = await handler.execute(step, context)
        assert result["success"] is False
        assert result["requires_approval"] is True

    @pytest.mark.asyncio
    async def test_execute_with_approval(self, context):
        from packages.agent.executor.context import ApprovalState
        context.approval_state = ApprovalState(
            approval_id="approval-1",
            status="approved",
        )
        handler = HumanReviewHandler()
        step = WorkflowStep(id="review", type=StepType.HUMAN_REVIEW)
        result = await handler.execute(step, context)
        assert result["success"] is True


class TestSubmitHandler:
    @pytest.mark.asyncio
    async def test_execute_requires_approval(self, context):
        handler = SubmitHandler()
        step = WorkflowStep(id="submit", type=StepType.SUBMIT)
        from packages.agent.errors import ApprovalRequired
        with pytest.raises(ApprovalRequired):
            await handler.execute(step, context)

    @pytest.mark.asyncio
    async def test_execute_with_approval(self, context):
        from packages.agent.executor.context import ApprovalState
        context.approval_state = ApprovalState(
            approval_id="approval-1",
            status="approved",
        )
        handler = SubmitHandler()
        step = WorkflowStep(id="submit", type=StepType.SUBMIT)
        result = await handler.execute(step, context)
        assert result["success"] is True


class TestTrackApplicationHandler:
    @pytest.mark.asyncio
    async def test_execute(self, context):
        handler = TrackApplicationHandler()
        step = WorkflowStep(id="track", type=StepType.TRACK_APPLICATION)
        result = await handler.execute(step, context)
        assert result["success"] is True


class TestCompleteHandler:
    @pytest.mark.asyncio
    async def test_execute(self, context):
        handler = CompleteHandler()
        step = WorkflowStep(id="complete", type=StepType.COMPLETE)
        result = await handler.execute(step, context)
        assert result["success"] is True
        assert result["completed"] is True


class TestStepHandlerRegistry:
    def test_register_and_get(self):
        registry = StepHandlerRegistry()
        handler = DiscoverServiceHandler()
        registry.register(StepType.DISCOVER_SERVICE, handler)
        assert registry.get_handler(StepType.DISCOVER_SERVICE) is handler

    def test_has_handler(self):
        registry = StepHandlerRegistry()
        assert not registry.has_handler(StepType.DISCOVER_SERVICE)
        registry.register(StepType.DISCOVER_SERVICE, DiscoverServiceHandler())
        assert registry.has_handler(StepType.DISCOVER_SERVICE)

    def test_fallback(self):
        registry = StepHandlerRegistry()
        fallback = CompleteHandler()
        registry.register_fallback(fallback)
        assert registry.get_handler_or_fallback(StepType.SUBMIT) is fallback

    def test_list_handlers(self):
        registry = StepHandlerRegistry()
        register_default_handlers(registry)
        handlers = registry.list_handlers()
        assert "DISCOVER_SERVICE" in handlers
        assert "SUBMIT" in handlers


class TestRegisterDefaultHandlers:
    def test_all_types_covered(self):
        registry = StepHandlerRegistry()
        register_default_handlers(registry)
        for step_type in StepType:
            assert registry.has_handler(step_type), f"No handler for {step_type.value}"

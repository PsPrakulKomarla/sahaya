"""AgentOrchestrator coordinates the complete agent task lifecycle.

The orchestrator does NOT contain service-specific browser logic.
It coordinates components: intent engine, service resolver, planner,
state machine, safety engine, executor, and browser agent.
"""
from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional

from packages.agent.audit import AuditEventService, AuditEventType
from packages.agent.errors import (
    AgentError,
    ApprovalRequired,
    TaskCancelled,
    WorkflowInvalid,
)
from packages.agent.executor.context import ExecutionContext
from packages.agent.executor.handlers import StepHandlerRegistry
from packages.agent.executor.handlers_impl import register_default_handlers
from packages.agent.executor.executor import TaskExecutor
from packages.agent.planner.models import StepType, WorkflowPlan
from packages.agent.planner.planner import TaskPlanner
from packages.agent.planner.state_machine import AgentState, AgentStateMachine
from packages.agent.safety.approval import ApprovalRequest, ApprovalService
from packages.agent.safety.engine import SafetyDecisionType, SafetyPolicyEngine
from packages.services.intent.engine import IntentEngine
from packages.services.intent.models import Intent
from packages.services.registry.resolver import ServiceResolver

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Coordinates the complete task lifecycle.

    Responsibilities:
    - Understand user request (intent)
    - Resolve service
    - Build workflow plan
    - Validate plan
    - Execute plan
    - Request approval when needed
    - Resume after approval
    - Verify result
    - Complete task
    """

    def __init__(
        self,
        intent_engine: IntentEngine,
        service_resolver: ServiceResolver,
        browser_agent: Optional[Any] = None,
        approval_service: Optional[ApprovalService] = None,
        safety_engine: Optional[SafetyPolicyEngine] = None,
        audit_service: Optional[AuditEventService] = None,
    ):
        self._intent_engine = intent_engine
        self._service_resolver = service_resolver
        self._browser_agent = browser_agent

        self._approval_service = approval_service or ApprovalService()
        self._safety_engine = safety_engine or SafetyPolicyEngine()
        self._audit_service = audit_service or AuditEventService()

        self._planner = TaskPlanner()
        self._handler_registry = StepHandlerRegistry()
        register_default_handlers(self._handler_registry)

        self._executor = TaskExecutor(
            handler_registry=self._handler_registry,
            on_step_complete=self._on_step_complete,
            on_step_failed=self._on_step_failed,
        )

        self._state_machines: Dict[str, AgentStateMachine] = {}
        self._contexts: Dict[str, ExecutionContext] = {}
        self._plans: Dict[str, WorkflowPlan] = {}

    async def process_request(
        self,
        user_message: str,
        user_id: str = "",
        context: Optional[ExecutionContext] = None,
    ) -> Dict[str, Any]:
        """Process a complete user request through the full pipeline.

        Returns a result dict with the outcome.
        """
        task_id = context.task_id if context else ""

        try:
            intent = await self.understand_request(user_message, context)
            resolution = await self.resolve_service(intent, context)
            plan = await self.build_plan(intent, resolution, context)
            validation = self.validate_plan(plan)

            if not validation["valid"]:
                return {
                    "success": False,
                    "error": validation.get("error", "Invalid plan"),
                    "phase": "planning",
                }

            result = await self.execute_plan(plan, context)
            return result

        except ApprovalRequired as e:
            return {
                "success": False,
                "requires_approval": True,
                "approval_id": e.approval_id,
                "action_type": e.action_type,
                "message": str(e),
                "phase": "execution",
            }
        except TaskCancelled:
            return {
                "success": False,
                "cancelled": True,
                "task_id": task_id,
                "phase": "execution",
            }
        except AgentError as e:
            return {
                "success": False,
                "error": e.to_dict(),
                "phase": "execution",
            }
        except Exception as e:
            logger.exception("Unexpected error in orchestrator")
            return {
                "success": False,
                "error": {"code": "UNEXPECTED_ERROR", "message": str(e)},
                "phase": "execution",
            }

    async def understand_request(
        self,
        user_message: str,
        context: Optional[ExecutionContext] = None,
    ) -> Intent:
        """Parse the user message into a structured intent."""
        task_id = context.task_id if context else "unknown"
        sm = self._get_or_create_state_machine(task_id)
        sm.transition(AgentState.UNDERSTANDING, "Parsing user intent")

        self._audit_service.record(
            event_type=AuditEventType.TASK_STARTED.value,
            user_id=context.user_id if context else None,
            task_id=task_id,
            metadata={"message_length": len(user_message)},
        )

        intent = self._intent_engine.parse(user_message)
        return intent

    async def resolve_service(
        self,
        intent: Intent,
        context: Optional[ExecutionContext] = None,
    ) -> Any:
        """Resolve the intent to a specific service."""
        task_id = context.task_id if context else "unknown"
        sm = self._get_or_create_state_machine(task_id)
        sm.transition(AgentState.RESOLVING_SERVICE, "Resolving service")

        jurisdiction = None
        if intent.jurisdiction and intent.jurisdiction.state:
            jurisdiction = intent.jurisdiction.state

        response = await self._service_resolver.resolve(
            service_query=intent.service_query,
            jurisdiction=jurisdiction,
        )

        if not response.success:
            raise WorkflowInvalid(
                f"Service resolution failed: {response.error.message if response.error else 'Unknown error'}"
            )

        self._audit_service.record(
            event_type=AuditEventType.SERVICE_RESOLVED.value,
            task_id=task_id,
            metadata={"service_id": response.data.get("service_id", "")},
        )

        return response

    async def build_plan(
        self,
        intent: Intent,
        resolution: Any,
        context: Optional[ExecutionContext] = None,
    ) -> WorkflowPlan:
        """Build a workflow plan from intent and resolution."""
        task_id = context.task_id if context else "unknown"
        sm = self._get_or_create_state_machine(task_id)
        sm.transition(AgentState.PLANNING, "Building workflow plan")

        from packages.services.registry.models import ServiceResolution, ResolutionJurisdiction

        raw_jurisdiction = resolution.data.get("jurisdiction")
        if isinstance(raw_jurisdiction, str):
            jurisdiction_obj = ResolutionJurisdiction(state=raw_jurisdiction)
        elif isinstance(raw_jurisdiction, dict):
            jurisdiction_obj = ResolutionJurisdiction(**raw_jurisdiction)
        else:
            jurisdiction_obj = None

        service_resolution = ServiceResolution(
            status="RESOLVED",
            service_id=resolution.data.get("service_id", ""),
            service_name=resolution.data.get("display_name", ""),
            capabilities=resolution.data.get("capabilities", []),
            jurisdiction=jurisdiction_obj,
        )

        plan = self._planner.plan(intent, service_resolution)
        self._plans[task_id] = plan

        self._audit_service.record(
            event_type=AuditEventType.PLAN_CREATED.value,
            task_id=task_id,
            metadata={"steps": len(plan.steps), "task_type": plan.task_type},
        )

        return plan

    def validate_plan(self, plan: WorkflowPlan) -> Dict[str, Any]:
        """Validate a workflow plan."""
        step_ids = {s.id for s in plan.steps}
        for step in plan.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    return {
                        "valid": False,
                        "error": f"Step '{step.id}' depends on unknown step '{dep}'",
                    }

        if not plan.steps:
            return {"valid": False, "error": "Plan has no steps"}

        return {"valid": True}

    async def execute_plan(
        self,
        plan: WorkflowPlan,
        context: ExecutionContext,
    ) -> Dict[str, Any]:
        """Execute a workflow plan through the state machine and executor."""
        task_id = context.task_id
        sm = self._get_or_create_state_machine(task_id)
        sm.transition(AgentState.VALIDATING, "Validating before execution")
        sm.transition(AgentState.EXECUTING, "Starting execution")

        context.metadata["browser_agent"] = self._browser_agent
        self._contexts[task_id] = context

        first_approval_step = None
        for step in plan.steps:
            if step.requires_approval:
                first_approval_step = step
                break

        if first_approval_step:
            result = await self._executor.execute_up_to(
                plan, context, first_approval_step.id
            )
            if result.get("success") and not plan.is_complete():
                sm.force_state(AgentState.WAITING_FOR_APPROVAL, f"Waiting for approval: {first_approval_step.id}")
                result["requires_approval"] = True
                result["approval_step"] = first_approval_step.id
                result["message"] = f"Waiting for approval on step: {first_approval_step.description}"
                return result
        else:
            result = await self._executor.execute_plan(plan, context)

        if result.get("success") and plan.is_complete():
            sm.transition(AgentState.VERIFYING, "Verifying results")
            sm.transition(AgentState.COMPLETED, "Task completed")
        elif not result.get("success") and not sm.is_terminal():
            sm.force_state(AgentState.FAILED, result.get("error", "Unknown failure"))

        return result

    async def request_approval(
        self,
        action_type: str,
        context: ExecutionContext,
        summary: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ApprovalRequest:
        """Request approval for a sensitive action."""
        decision = self._safety_engine.evaluate(
            action_type=action_type,
            has_approval=context.approval_state.is_valid(),
            approval_valid=context.approval_state.is_valid(),
        )

        self._audit_service.record(
            event_type=AuditEventType.SAFETY_EVALUATION.value,
            user_id=context.user_id,
            task_id=context.task_id,
            metadata={"action": action_type, "decision": decision.decision.value},
        )

        if decision.decision == SafetyDecisionType.ALLOW:
            approval = self._approval_service.create_approval(
                user_id=context.user_id,
                action_type=action_type,
                summary=summary,
                task_id=context.task_id,
                metadata=metadata,
            )
            self._approval_service.approve(approval.id)
            return approval

        if decision.decision == SafetyDecisionType.DENY:
            raise AgentError(
                message=decision.reason,
                code="ACTION_DENIED",
            )

        approval = self._approval_service.create_approval(
            user_id=context.user_id,
            action_type=action_type,
            summary=summary,
            task_id=context.task_id,
            metadata=metadata,
        )

        sm = self._get_or_create_state_machine(context.task_id)
        if sm.can_transition(AgentState.WAITING_FOR_APPROVAL):
            sm.transition(AgentState.WAITING_FOR_APPROVAL, f"Waiting for approval: {action_type}")

        self._audit_service.record(
            event_type=AuditEventType.APPROVAL_REQUESTED.value,
            user_id=context.user_id,
            task_id=context.task_id,
            metadata={"approval_id": approval.id, "action": action_type},
        )

        return approval

    async def resume_after_approval(
        self,
        approval_id: str,
        context: ExecutionContext,
    ) -> Dict[str, Any]:
        """Resume execution after approval is granted."""
        is_valid = self._approval_service.validate_approval(approval_id)
        if not is_valid:
            raise ApprovalRequired(
                action_type="RESUME",
                reason=f"Approval '{approval_id}' is not valid",
                approval_id=approval_id,
            )

        approval = self._approval_service.get_approval(approval_id)
        if approval:
            context.set_approval(
                __import__("packages.agent.executor.context", fromlist=["ApprovalState"]).ApprovalState(
                    approval_id=approval.id,
                    action_type=approval.action_type,
                    status=approval.status,
                    granted_at=approval.approved_at,
                    expires_at=approval.expires_at,
                )
            )

            self._audit_service.record(
                event_type=AuditEventType.APPROVAL_GRANTED.value,
                user_id=context.user_id,
                task_id=context.task_id,
                metadata={"approval_id": approval_id},
            )

        sm = self._get_or_create_state_machine(context.task_id)
        if sm.can_transition(AgentState.EXECUTING):
            sm.transition(AgentState.EXECUTING, "Resuming after approval")

        plan = self._plans.get(context.task_id)
        if plan:
            return await self._executor.execute_plan(plan, context)

        return {"success": True, "message": "Resumed with no pending plan"}

    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """Cancel an active task."""
        sm = self._state_machines.get(task_id)
        if sm:
            sm.force_state(AgentState.CANCELLED, "User requested cancellation")

        self._audit_service.record(
            event_type=AuditEventType.TASK_CANCELLED.value,
            task_id=task_id,
        )

        return {"success": True, "task_id": task_id, "status": "cancelled"}

    def get_task_state(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the current state of a task."""
        sm = self._state_machines.get(task_id)
        if sm:
            return {
                "task_id": task_id,
                "state": sm.state.value,
                "is_terminal": sm.is_terminal(),
                "history": sm.get_state_history(),
            }
        return None

    def _get_or_create_state_machine(self, task_id: str) -> AgentStateMachine:
        if task_id not in self._state_machines:
            self._state_machines[task_id] = AgentStateMachine()
        return self._state_machines[task_id]

    def _on_step_complete(self, step_id: str, step_type: str, result: Dict[str, Any]) -> None:
        logger.info("Step completed: %s (%s)", step_id, step_type)

    def _on_step_failed(self, step_id: str, step_type: str, error: str) -> None:
        logger.error("Step failed: %s (%s): %s", step_id, step_type, error)

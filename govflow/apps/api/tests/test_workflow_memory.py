"""Tests for WorkflowMemory models."""

import pytest
from uuid import uuid4
from app.services.workflow_memory.models import (
    WorkflowStatus,
    WorkflowSource,
    BrowserActionType,
    TargetDescriptor,
    ExpectedResult,
    LearnableWorkflowStep,
    WorkflowMatch,
    WorkflowDefinition,
)


class TestTargetDescriptor:
    def test_creation(self):
        t = TargetDescriptor(role="button", text="Submit")
        assert t.role == "button"
        assert t.text == "Submit"

    def test_semantic_signature(self):
        t1 = TargetDescriptor(role="button", text="Start Application")
        t2 = TargetDescriptor(role="button", text="Start Application")
        assert t1.semantic_signature() == t2.semantic_signature()

    def test_semantic_signature_empty(self):
        t = TargetDescriptor()
        assert t.semantic_signature() == "unknown"

    def test_semantic_signature_with_label(self):
        t = TargetDescriptor(role="input", label="Full Name")
        sig = t.semantic_signature()
        assert "role=input" in sig
        assert "label=full name" in sig


class TestExpectedResult:
    def test_default(self):
        er = ExpectedResult()
        assert er.url_changed is False
        assert er.description == ""

    def test_url_changed(self):
        er = ExpectedResult(url_changed=True, expected_url_pattern="/form")
        assert er.url_changed is True


class TestLearnableWorkflowStep:
    def test_creation(self):
        step = LearnableWorkflowStep(
            step_id="step_001",
            action=BrowserActionType.CLICK,
            purpose="Start the application",
            target=TargetDescriptor(role="button", text="Start Application"),
        )
        assert step.step_id == "step_001"
        assert step.action == BrowserActionType.CLICK
        assert step.confidence == 1.0

    def test_with_expected_result(self):
        step = LearnableWorkflowStep(
            step_id="step_001",
            action=BrowserActionType.CLICK,
            target=TargetDescriptor(role="button", text="Submit"),
            expected_result=ExpectedResult(url_changed=True),
        )
        assert step.expected_result.url_changed is True

    def test_with_alternatives(self):
        step = LearnableWorkflowStep(
            step_id="step_001",
            action=BrowserActionType.CLICK,
            target=TargetDescriptor(role="button", text="Start Application"),
            alternatives=[
                TargetDescriptor(role="button", text="Begin Application"),
                TargetDescriptor(role="button", text="New Application"),
            ],
        )
        assert len(step.alternatives) == 2

    def test_optional_step(self):
        step = LearnableWorkflowStep(
            step_id="step_001",
            action=BrowserActionType.WAIT,
            target=TargetDescriptor(),
            optional=True,
        )
        assert step.optional is True

    def test_approval_required(self):
        step = LearnableWorkflowStep(
            step_id="step_001",
            action=BrowserActionType.CLICK,
            target=TargetDescriptor(role="button", text="Submit"),
            requires_human_approval=True,
        )
        assert step.requires_human_approval is True


class TestWorkflowDefinition:
    def test_creation(self):
        wf = WorkflowDefinition(
            service_id="income_cert",
            service_name="Income Certificate",
            operation="new_application",
        )
        assert wf.service_id == "income_cert"
        assert wf.status == WorkflowStatus.DRAFT

    def test_to_db_dict(self):
        wf = WorkflowDefinition(
            service_id="income_cert",
            workflow_version="2026.08.1",
            steps=[
                LearnableWorkflowStep(
                    step_id="step_001",
                    action=BrowserActionType.CLICK,
                    target=TargetDescriptor(role="button", text="Start"),
                )
            ],
        )
        d = wf.to_db_dict()
        assert d["service_id"] == "income_cert"
        assert d["workflow_version"] == "2026.08.1"
        assert len(d["steps"]) == 1

    def test_from_db_dict(self):
        data = {
            "service_id": "income_cert",
            "workflow_version": "2026.08.1",
            "status": "active",
            "source": "exploration",
            "steps": [
                {
                    "step_id": "step_001",
                    "action": "click",
                    "target": {"role": "button", "text": "Start"},
                }
            ],
            "confidence": 0.85,
        }
        wf = WorkflowDefinition.from_db_dict(data, workflow_id="test-id")
        assert wf.service_id == "income_cert"
        assert wf.workflow_id == "test-id"
        assert wf.status == WorkflowStatus.ACTIVE
        assert wf.confidence == 0.85
        assert len(wf.steps) == 1


class TestWorkflowMatch:
    def test_creation(self):
        m = WorkflowMatch(
            workflow_id="wf-123",
            service_id="income_cert",
            match_score=0.9,
            confidence=0.85,
        )
        assert m.workflow_id == "wf-123"
        assert m.match_score == 0.9


class TestWorkflowStatus:
    def test_all_statuses(self):
        assert WorkflowStatus.DRAFT == "draft"
        assert WorkflowStatus.LEARNING == "learning"
        assert WorkflowStatus.VALIDATED == "validated"
        assert WorkflowStatus.ACTIVE == "active"
        assert WorkflowStatus.OUTDATED == "outdated"
        assert WorkflowStatus.DISABLED == "disabled"
        assert WorkflowStatus.FAILED == "failed"


class TestWorkflowSource:
    def test_all_sources(self):
        assert WorkflowSource.EXPLORATION == "exploration"
        assert WorkflowSource.MANUAL == "manual"
        assert WorkflowSource.RECOVERY == "recovery"
        assert WorkflowSource.IMPORTED == "imported"

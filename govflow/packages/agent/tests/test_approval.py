import pytest
from datetime import datetime, timedelta
from packages.agent.approval.service import ApprovalService, ApprovalStatus


class TestApprovalService:
    @pytest.fixture
    def service(self):
        return Service()

    def test_create_approval(self, service):
        approval = service.create_approval(
            action_type="SUBMIT_APPLICATION",
            summary={"step": "submit", "description": "Submit application"},
            user_id="user1",
            task_id="task1",
        )
        assert approval.status == ApprovalStatus.PENDING
        assert approval.action_type == "SUBMIT_APPLICATION"

    def test_get_approval(self, service):
        approval = service.create_approval(
            action_type="SUBMIT_APPLICATION",
            summary={},
            user_id="user1",
            task_id="task1",
        )
        retrieved = service.get_approval(approval.approval_id)
        assert retrieved is not None
        assert retrieved.status == ApprovalStatus.PENDING

    def test_approve(self, service):
        approval = service.create_approval(
            action_type="SUBMIT_APPLICATION",
            summary={},
            user_id="user1",
            task_id="task1",
        )
        result = service.approve(approval.approval_id)
        assert result is not None
        assert result.status == ApprovalStatus.APPROVED
        assert result.approved_at is not None

    def test_reject(self, service):
        approval = service.create_approval(
            action_type="SUBMIT_APPLICATION",
            summary={},
            user_id="user1",
            task_id="task1",
        )
        result = service.reject(approval.approval_id)
        assert result is not None
        assert result.status == ApprovalStatus.REJECTED

    def test_validate_approval(self, service):
        approval = service.create_approval(
            action_type="SUBMIT_APPLICATION",
            summary={},
            user_id="user1",
            task_id="task1",
        )
        service.approve(approval.approval_id)
        assert service.validate_approval(approval.approval_id) is True

    def test_validate_pending_approval(self, service):
        approval = service.create_approval(
            action_type="SUBMIT_APPLICATION",
            summary={},
            user_id="user1",
            task_id="task1",
        )
        assert service.validate_approval(approval.approval_id) is False

    def test_approval_expiration(self):
        service = Service(approval_ttl_minutes=-1)
        approval = service.create_approval(
            action_type="SUBMIT_APPLICATION",
            summary={},
            user_id="user1",
            task_id="task1",
        )
        result = service.approve(approval.approval_id)
        assert result is None
        assert service.validate_approval(approval.approval_id) is False

    def test_has_pending_approval(self, service):
        service.create_approval(
            action_type="SUBMIT_APPLICATION",
            summary={},
            user_id="user1",
            task_id="task1",
        )
        assert service.has_pending_approval("task1", "SUBMIT_APPLICATION") is True
        assert service.has_pending_approval("task1", "OTHER_ACTION") is False
        assert service.has_pending_approval("task2", "SUBMIT_APPLICATION") is False

    def test_approve_nonexistent(self, service):
        result = service.approve("nonexistent")
        assert result is None

    def test_reject_nonexistent(self, service):
        result = service.reject("nonexistent")
        assert result is None

    def test_duplicate_prevention(self, service):
        approval = service.create_approval(
            action_type="SUBMIT_APPLICATION",
            summary={},
            user_id="user1",
            task_id="task1",
        )
        service.approve(approval.approval_id)
        result = service.approve(approval.approval_id)
        assert result is None


class Service(ApprovalService):
    def __init__(self, approval_ttl_minutes: int = 30):
        super().__init__(approval_ttl_minutes=approval_ttl_minutes)

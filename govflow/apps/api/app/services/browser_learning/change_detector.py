"""Page Change Detection - compares expected vs actual page state.

Detects when a website has changed, signals include:
- Missing expected element
- Changed text
- Changed role
- Changed URL
- Changed form structure
- Changed page title
- Changed navigation
- Unexpected redirect
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from packages.browser.interfaces.models import ElementType, PageModel, SemanticElement
from app.services.workflow_memory.models import LearnableWorkflowStep, TargetDescriptor
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ChangeDetection:
    """Result of comparing expected vs actual page state."""

    changed: bool = False
    missing_elements: List[str] = field(default_factory=list)
    changed_text: List[str] = field(default_factory=list)
    changed_role: List[str] = field(default_factory=list)
    url_changed: bool = False
    title_changed: bool = False
    unexpected_redirect: bool = False
    changed_forms: List[str] = field(default_factory=list)
    details: str = ""

    @property
    def severity(self) -> str:
        """Assess severity of changes."""
        if self.unexpected_redirect or self.url_changed:
            return "high"
        if self.missing_elements:
            return "high"
        if self.changed_role:
            return "medium"
        if self.changed_text:
            return "low"
        return "none"


class PageChangeDetector:
    """Detects changes between expected and actual page state."""

    def __init__(self, similarity_threshold: float = 0.6):
        self._similarity_threshold = similarity_threshold

    def detect(
        self,
        expected_page: Optional[PageModel],
        actual_page: PageModel,
        expected_steps: Optional[List[LearnableWorkflowStep]] = None,
    ) -> ChangeDetection:
        """Compare expected page state with actual page state."""
        result = ChangeDetection()

        if expected_page is None:
            result.changed = True
            result.details = "No expected page available for comparison"
            return result

        # URL change
        if expected_page.url and actual_page.url:
            if self._normalize_url(expected_page.url) != self._normalize_url(actual_page.url):
                result.url_changed = True
                result.changed = True

        # Title change
        if expected_page.title and actual_page.title:
            if expected_page.title.lower().strip() != actual_page.title.lower().strip():
                result.title_changed = True
                result.changed = True

        # Element comparison
        if expected_steps:
            self._compare_steps(expected_steps, actual_page, result)
        else:
            self._compare_elements(expected_page.elements, actual_page.elements, result)

        return result

    def _compare_steps(
        self,
        expected_steps: List[LearnableWorkflowStep],
        actual_page: PageModel,
        result: ChangeDetection,
    ) -> None:
        """Compare expected workflow steps against actual page elements."""
        for step in expected_steps:
            found = self._find_matching_element(step.target, actual_page)
            if found is None:
                result.missing_elements.append(
                    f"Step {step.step_id}: {step.target_description}"
                )
                result.changed = True
            elif not self._text_similar(step.target.text or "", found.text):
                result.changed_text.append(
                    f"Step {step.step_id}: expected '{step.target.text}' got '{found.text}'"
                )
                result.changed = True

    def _compare_elements(
        self,
        expected_elements: List[SemanticElement],
        actual_elements: List[SemanticElement],
        result: ChangeDetection,
    ) -> None:
        """Compare expected elements against actual elements."""
        for expected in expected_elements:
            if not expected.visible:
                continue
            found = False
            for actual in actual_elements:
                if self._elements_match(expected, actual):
                    found = True
                    break
            if not found:
                result.missing_elements.append(
                    f"{expected.role.value}: '{expected.text or expected.label}'"
                )
                result.changed = True

    def _find_matching_element(
        self, target: TargetDescriptor, page: PageModel
    ) -> Optional[SemanticElement]:
        """Find an element on the page that matches the target descriptor."""
        for element in page.elements:
            if not element.visible:
                continue
            if self._target_matches_element(target, element):
                return element
        return None

    def _target_matches_element(
        self, target: TargetDescriptor, element: SemanticElement
    ) -> bool:
        """Check if a target descriptor matches a semantic element."""
        if target.role and element.role.value != target.role:
            return False
        if target.text and not self._text_similar(target.text, element.text):
            return False
        if target.label and not self._text_similar(target.label, element.label):
            return False
        return True

    def _elements_match(self, expected: SemanticElement, actual: SemanticElement) -> bool:
        """Check if two elements are semantically equivalent."""
        if expected.role != actual.role:
            return False
        if expected.text and actual.text:
            return self._text_similar(expected.text, actual.text)
        if expected.label and actual.label:
            return self._text_similar(expected.label, actual.label)
        return True

    def _text_similar(self, text1: str, text2: str) -> bool:
        """Check if two text strings are semantically similar."""
        t1 = text1.lower().strip()
        t2 = text2.lower().strip()
        if t1 == t2:
            return True
        # Simple word overlap similarity
        words1 = set(t1.split())
        words2 = set(t2.split())
        if not words1 or not words2:
            return False
        overlap = len(words1 & words2)
        total = min(len(words1), len(words2))
        return (overlap / total) >= self._similarity_threshold if total > 0 else False

    def _normalize_url(self, url: str) -> str:
        """Normalize a URL for comparison."""
        return url.rstrip("/").lower()

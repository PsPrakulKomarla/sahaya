from app.core.logging import get_logger

from packages.documents.base.models import (
    DocumentRequirementItem,
    RequiredDocumentsResult,
)
from packages.services.registry.registry import ServiceRegistry

logger = get_logger(__name__)


class DocumentRequirementEngine:
    """Engine for determining document requirements for a service.

    Connects the Service Adapter to the Document System.
    """

    def __init__(self, registry: ServiceRegistry | None = None):
        self._registry = registry

    def _get_registry(self) -> ServiceRegistry:
        if self._registry is None:
            from packages.services import get_registry
            self._registry = get_registry()
        return self._registry

    async def get_requirements(
        self,
        service_id: str,
        operation: str = "new_application",
        jurisdiction: str | None = None,
    ) -> RequiredDocumentsResult:
        """Get document requirements for a service operation."""
        registry = self._get_registry()
        adapter = registry.get_service(service_id)

        if not adapter:
            logger.warning("service_not_found_for_requirements", service_id=service_id)
            return RequiredDocumentsResult(
                service_id=service_id,
                operation=operation,
                requirements=[],
            )

        try:
            response = await adapter.get_document_requirements()
            if not response.success:
                return RequiredDocumentsResult(
                    service_id=service_id,
                    operation=operation,
                    requirements=[],
                )

            raw_docs = response.data.get("documents", []) if response.data else []
            requirements = [
                DocumentRequirementItem(
                    document_type=doc.get("document_type", ""),
                    display_name=doc.get("display_name", doc.get("document_type", "")),
                    description=doc.get("description", ""),
                    mandatory=doc.get("mandatory", True),
                    accepted_formats=doc.get("accepted_formats", ["pdf", "jpg", "png"]),
                    max_file_size_mb=doc.get("max_file_size_mb", 5),
                )
                for doc in raw_docs
            ]

            return RequiredDocumentsResult(
                service_id=service_id,
                operation=operation,
                requirements=requirements,
            )

        except (RuntimeError, ValueError, KeyError, TypeError) as e:
            logger.error(
                "requirement_engine_error",
                service_id=service_id,
                error=str(e),
            )
            return RequiredDocumentsResult(
                service_id=service_id,
                operation=operation,
                requirements=[],
            )

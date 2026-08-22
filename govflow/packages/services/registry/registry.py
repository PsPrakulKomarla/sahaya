from typing import Dict, List, Optional, Type
from packages.services.base.adapter import GovernmentServiceAdapter
from packages.services.base.models import ServiceCapability, ServiceMetadata


class ServiceRegistry:
    """Central registry for government service adapters.

    Responsibilities:
    - Register services
    - Find services by ID, query, capability, or jurisdiction
    - Load the correct adapter
    - Validate service configuration
    """

    def __init__(self):
        self._adapters: Dict[str, GovernmentServiceAdapter] = {}
        self._adapter_classes: Dict[str, Type[GovernmentServiceAdapter]] = {}

    def register_service(self, adapter: GovernmentServiceAdapter) -> None:
        """Register a service adapter instance."""
        metadata = adapter.metadata()
        if not metadata.service_id:
            raise ValueError("Adapter must have a valid service_id")
        if not metadata.enabled:
            return
        self._adapters[metadata.service_id] = adapter

    def register_adapter_class(self, service_id: str, adapter_class: Type[GovernmentServiceAdapter]) -> None:
        """Register an adapter class for lazy instantiation."""
        self._adapter_classes[service_id] = adapter_class

    def get_service(self, service_id: str) -> Optional[GovernmentServiceAdapter]:
        """Get adapter by service ID."""
        if service_id in self._adapters:
            return self._adapters[service_id]
        if service_id in self._adapter_classes:
            adapter = self._adapter_classes[service_id]()
            self._adapters[service_id] = adapter
            return adapter
        return None

    def list_services(self) -> List[ServiceMetadata]:
        """List all registered services."""
        self._ensure_all_instantiated()
        return [adapter.metadata() for adapter in self._adapters.values()]

    def find_services(self, query: str) -> List[GovernmentServiceAdapter]:
        """Find services matching a text query."""
        self._ensure_all_instantiated()
        query_lower = query.lower()
        results = []
        for adapter in self._adapters.values():
            metadata = adapter.metadata()
            if (
                query_lower in metadata.service_id.lower()
                or query_lower in metadata.display_name.lower()
                or query_lower in metadata.description.lower()
                or query_lower in metadata.department.lower()
            ):
                results.append(adapter)
        return results

    def find_by_capability(self, capability: ServiceCapability) -> List[GovernmentServiceAdapter]:
        """Find all services that support a specific capability."""
        self._ensure_all_instantiated()
        return [
            adapter
            for adapter in self._adapters.values()
            if capability in adapter.get_capabilities()
        ]

    def find_by_jurisdiction(self, jurisdiction: str) -> List[GovernmentServiceAdapter]:
        """Find all services available in a specific jurisdiction."""
        self._ensure_all_instantiated()
        jurisdiction_lower = jurisdiction.lower()
        return [
            adapter
            for adapter in self._adapters.values()
            if jurisdiction_lower in adapter.metadata().jurisdiction.lower()
        ]

    def get_capabilities(self, service_id: str) -> List[ServiceCapability]:
        """Get capabilities for a specific service."""
        adapter = self.get_service(service_id)
        if not adapter:
            return []
        return adapter.get_capabilities()

    def validate_service(self, service_id: str) -> bool:
        """Validate that a service is properly configured."""
        adapter = self.get_service(service_id)
        if not adapter:
            return False
        metadata = adapter.metadata()
        return bool(
            metadata.service_id
            and metadata.display_name
            and metadata.department
            and metadata.jurisdiction
        )

    def _ensure_all_instantiated(self) -> None:
        """Instantiate any registered adapter classes."""
        for service_id, adapter_class in self._adapter_classes.items():
            if service_id not in self._adapters:
                self._adapters[service_id] = adapter_class()

    def clear(self) -> None:
        """Clear all registered services (for testing)."""
        self._adapters.clear()
        self._adapter_classes.clear()


_registry: Optional[ServiceRegistry] = None


def get_registry() -> ServiceRegistry:
    """Get the global service registry singleton."""
    global _registry
    if _registry is None:
        _registry = ServiceRegistry()
    return _registry


def reset_registry() -> ServiceRegistry:
    """Reset the global registry (for testing)."""
    global _registry
    _registry = ServiceRegistry()
    return _registry
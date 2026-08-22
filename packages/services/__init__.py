from packages.services.base import (
    GovernmentServiceAdapter,
    ServiceCapability,
    ServiceMetadata,
    ServiceResponse,
    ServiceError,
)
from packages.services.registry import ServiceRegistry, get_registry, reset_registry, ServiceResolver
from packages.services.adapters import MockIncomeCertificateAdapter, MockBirthCertificateAdapter


def register_default_services() -> ServiceRegistry:
    """Register all default service adapters."""
    registry = get_registry()
    registry.register_service(MockIncomeCertificateAdapter())
    registry.register_service(MockBirthCertificateAdapter())
    return registry


__all__ = [
    "GovernmentServiceAdapter",
    "ServiceCapability",
    "ServiceMetadata",
    "ServiceResponse",
    "ServiceError",
    "ServiceRegistry",
    "get_registry",
    "reset_registry",
    "ServiceResolver",
    "MockIncomeCertificateAdapter",
    "MockBirthCertificateAdapter",
    "register_default_services",
]
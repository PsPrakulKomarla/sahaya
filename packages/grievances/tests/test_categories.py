import pytest
from packages.grievances.categories import (
    GrievanceCategoryDefinition,
    GrievanceCategoryRegistry,
    CATEGORY_DEFINITIONS,
    GrievanceCategory,
)
from packages.grievances.models import GrievanceCategory as Cat


class TestGrievanceCategories:
    def test_category_definitions_exist(self):
        assert len(CATEGORY_DEFINITIONS) == 8
        for cat in Cat:
            assert cat in CATEGORY_DEFINITIONS

    def test_category_definition_structure(self):
        for cat, defn in CATEGORY_DEFINITIONS.items():
            assert defn.category == cat
            assert defn.label
            assert defn.description
            assert isinstance(defn.keywords, tuple)
            assert isinstance(defn.keywords_kn, tuple)
            assert isinstance(defn.keywords_hi, tuple)

    def test_registry_all(self):
        registry = GrievanceCategoryRegistry()
        all_cats = registry.all()
        assert len(all_cats) == 8

    def test_registry_get(self):
        registry = GrievanceCategoryRegistry()
        defn = registry.get(Cat.APPLICATION_DELAY)
        assert defn is not None
        assert defn.category == Cat.APPLICATION_DELAY

    def test_detect_english_application_delay(self):
        registry = GrievanceCategoryRegistry()
        cat = registry.detect("My application has been delayed for two months", "en")
        assert cat == Cat.APPLICATION_DELAY

    def test_detect_english_application_rejection(self):
        registry = GrievanceCategoryRegistry()
        cat = registry.detect("My application was rejected", "en")
        assert cat == Cat.APPLICATION_REJECTION

    def test_detect_kannada_application_delay(self):
        registry = GrievanceCategoryRegistry()
        cat = registry.detect("ನನ್ನ ಅರ್ಜಿ ವಿಳಂಬದಾಗಿ ಇರುತ್ತದೆ", "kn")
        assert cat == Cat.APPLICATION_DELAY

    def test_detect_hindi_application_delay(self):
        registry = GrievanceCategoryRegistry()
        cat = registry.detect("मेरा आवेदन विलंब से है", "hi")
        assert cat == Cat.APPLICATION_DELAY

    def test_detect_kannada_fallback_to_english(self):
        registry = GrievanceCategoryRegistry()
        cat = registry.detect("delayed pending", "kn")
        assert cat == Cat.APPLICATION_DELAY

    def test_detect_unknown_returns_other(self):
        registry = GrievanceCategoryRegistry()
        cat = registry.detect("completely unrelated text", "en")
        assert cat == Cat.OTHER

    def test_custom_registry(self):
        custom = {
            Cat.APPLICATION_DELAY: GrievanceCategoryDefinition(
                category=Cat.APPLICATION_DELAY,
                label="Delay",
                description="Delayed",
                keywords=("custom_delay",),
            ),
        }
        registry = GrievanceCategoryRegistry(custom)
        cat = registry.detect("custom_delay issue", "en")
        assert cat == Cat.APPLICATION_DELAY
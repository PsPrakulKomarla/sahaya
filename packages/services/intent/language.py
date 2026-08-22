from abc import ABC, abstractmethod
from typing import Optional, Tuple
from packages.services.intent.models import Language


class LanguageDetector(ABC):
    """Abstract interface for language detection."""

    @abstractmethod
    def detect(self, message: str) -> Tuple[Language, float]:
        """Detect the language of a message.

        Args:
            message: The input text to detect language for.

        Returns:
            A tuple of (Language, confidence) where confidence is 0.0 to 1.0.
        """
        pass


class RuleBasedLanguageDetector(LanguageDetector):
    """Rule-based language detection using character ranges.

    This is a deterministic implementation suitable for testing.
    It does not require external dependencies.
    """

    KANNADA_RANGE = range(0x0C80, 0x0CFF + 1)
    HINDI_RANGE = range(0x0900, 0x097F + 1)

    def detect(self, message: str) -> Tuple[Language, float]:
        """Detect language based on character analysis."""
        if not message or not message.strip():
            return Language.ENGLISH, 0.0

        message = message.strip()
        total_chars = len(message)
        if total_chars == 0:
            return Language.ENGLISH, 0.0

        kannada_count = 0
        hindi_count = 0
        latin_count = 0

        for char in message:
            code_point = ord(char)
            if code_point in self.KANNADA_RANGE:
                kannada_count += 1
            elif code_point in self.HINDI_RANGE:
                hindi_count += 1
            elif char.isalpha() and code_point < 128:
                latin_count += 1

        kannada_ratio = kannada_count / total_chars
        hindi_ratio = hindi_count / total_chars
        latin_ratio = latin_count / total_chars

        if kannada_ratio > 0.3:
            confidence = min(0.6 + kannada_ratio, 1.0)
            return Language.KANNADA, confidence
        elif hindi_ratio > 0.3:
            confidence = min(0.6 + hindi_ratio, 1.0)
            return Language.HINDI, confidence
        elif latin_ratio > 0.3:
            confidence = min(0.5 + latin_ratio, 0.95)
            return Language.ENGLISH, confidence
        else:
            return Language.ENGLISH, 0.3

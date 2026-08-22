from packages.documents.base.ocr_provider import OCRProvider
from packages.documents.ocr.mock_provider import MockOCRProvider
from packages.documents.ocr.paddleocr_provider import PaddleOCRProvider

__all__ = ["OCRProvider", "MockOCRProvider", "PaddleOCRProvider"]

import os
from typing import Optional, List, Dict, Any
from packages.documents.base.ocr_provider import OCRProvider
from packages.documents.base.models import OCRResult, OCRPageResult, OCRBoundingBox
from app.core.logging import get_logger

logger = get_logger(__name__)


class PaddleOCRProvider(OCRProvider):
    """PaddleOCR-based OCR provider.

    Uses PaddleOCR for local OCR processing.
    Falls back gracefully if PaddleOCR is not installed.

    This provider is NOT required for the system to function.
    MockOCRProvider can be used for development and testing.
    """

    def __init__(self, languages: Optional[List[str]] = None):
        self._languages = languages or ["en"]
        self._engine = None
        self._initialized = False

    def provider_name(self) -> str:
        return "paddleocr"

    def supported_languages(self) -> List[str]:
        return self._languages

    def _initialize_engine(self) -> None:
        """Lazy initialization of PaddleOCR engine."""
        if self._initialized:
            return

        try:
            from paddleocr import PaddleOCR

            lang_str = "+".join(self._languages)
            self._engine = PaddleOCR(use_angle_cls=True, lang=lang_str, show_log=False)
            self._initialized = True
            logger.info("paddleocr_initialized", languages=self._languages)
        except ImportError:
            logger.warning(
                "paddleocr_not_installed",
                message="PaddleOCR is not installed. Use 'pip install paddleocr' to enable.",
            )
            self._initialized = True
        except Exception as e:
            logger.error("paddleocr_init_failed", error=str(e))
            self._initialized = True

    async def process(self, file_path: str, language: Optional[str] = None) -> OCRResult:
        """Process a document using PaddleOCR."""
        self._initialize_engine()

        if self._engine is None:
            raise RuntimeError(
                "PaddleOCR engine is not available. "
                "Install PaddleOCR or use MockOCRProvider for development."
            )

        try:
            result = self._engine.ocr(file_path, cls=True)
            return self._parse_result(result, language)
        except Exception as e:
            logger.error("paddleocr_processing_failed", file_path=file_path, error=str(e))
            raise

    def _parse_result(self, raw_result: Any, language: Optional[str] = None) -> OCRResult:
        """Parse PaddleOCR raw output into OCRResult."""
        pages: List[OCRPageResult] = []
        all_text_parts: List[str] = []
        all_confidences: List[float] = []

        if not raw_result:
            return OCRResult(
                extracted_text="",
                pages=[],
                overall_confidence=0.0,
                language=language,
            )

        for page_idx, page_result in enumerate(raw_result):
            if not page_result:
                continue

            page_text_parts: List[str] = []
            page_confidences: List[float] = []
            bounding_boxes: List[OCRBoundingBox] = []

            for line in page_result:
                if len(line) >= 2:
                    box_coords = line[0]
                    text_info = line[1]
                    if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                        text = str(text_info[0])
                        conf = float(text_info[1])
                    else:
                        text = str(text_info)
                        conf = 0.0

                    page_text_parts.append(text)
                    page_confidences.append(conf)

                    if box_coords and len(box_coords) >= 4:
                        xs = [p[0] for p in box_coords]
                        ys = [p[1] for p in box_coords]
                        bounding_boxes.append(
                            OCRBoundingBox(
                                x=min(xs),
                                y=min(ys),
                                width=max(xs) - min(xs),
                                height=max(ys) - min(ys),
                                text=text,
                                confidence=conf,
                            )
                        )

            page_text = "\n".join(page_text_parts)
            page_conf = (
                sum(page_confidences) / len(page_confidences) if page_confidences else 0.0
            )

            pages.append(
                OCRPageResult(
                    page_number=page_idx + 1,
                    text=page_text,
                    confidence=page_conf,
                    bounding_boxes=bounding_boxes,
                    language=language,
                )
            )
            all_text_parts.append(page_text)
            all_confidences.extend(page_confidences)

        overall_text = "\n\n".join(all_text_parts)
        overall_conf = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0

        return OCRResult(
            extracted_text=overall_text,
            pages=pages,
            overall_confidence=overall_conf,
            language=language,
            metadata={"provider": "paddleocr", "page_count": len(pages)},
        )

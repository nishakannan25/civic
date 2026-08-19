import logging
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse

from app.schemas.ai import InferenceResponse, AIHealthResponse
from app.ai import ModelLoader, CrisisInferenceService
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Inference"])
inference_service = CrisisInferenceService()

ALLOWED_MIME_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
MAX_FILE_SIZE_BYTES = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024


@router.post(
    "/infer",
    response_model=InferenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict crisis class from civic problem image",
    description="Accepts a civic crisis image upload (JPEG, PNG, WEBP) and returns the predicted crisis class, AI confidence score, and model version.",
)
async def infer_crisis(image: UploadFile = File(...)):
    """
    Perform AI crisis image classification.
    """
    # 1. Validate model availability
    if not ModelLoader.is_loaded():
        logger.error("Inference request rejected: AI model is unavailable.")
        raise HTTPException(
            status_code=status.HTTP_537_SERVICE_UNAVAILABLE if hasattr(status, "HTTP_537_SERVICE_UNAVAILABLE") else status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI inference service unavailable",
        )

    # 2. Validate MIME type
    content_type = image.content_type or ""
    filename = image.filename or ""
    ext = filename.split(".")[-1].lower() if "." in filename else ""

    valid_mime = content_type.lower() in ALLOWED_MIME_TYPES or ext in ["jpg", "jpeg", "png", "webp"]
    if not valid_mime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image format. Allowed formats: JPEG, PNG, WEBP.",
        )

    # 3. Read image bytes
    try:
        contents = await image.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read uploaded image file.",
        )

    if not contents or len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file: File is empty.",
        )

    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image size exceeds maximum limit of {settings.MAX_IMAGE_SIZE_MB}MB.",
        )

    # 4. Run inference service
    try:
        result = inference_service.predict_bytes(contents)
        return result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image: {str(ve)}",
        )
    except RuntimeError as re:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI inference service unavailable",
        )
    except Exception as e:
        logger.error(f"Inference error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during image inference.",
        )


@router.get(
    "/health",
    response_model=AIHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="AI inference service status",
)
def ai_health():
    """
    Check status of the AI inference model.
    """
    is_ready = ModelLoader.is_loaded()
    return AIHealthResponse(
        status="ready" if is_ready else "unavailable",
        model_version=ModelLoader.get_version(),
        model_loaded=is_ready,
    )

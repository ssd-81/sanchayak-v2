import logging
import os

logging.basicConfig(
    level=logging.DEBUG if os.environ.get("DEBUG") else logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def log_request(user_query: str, has_audio: bool = False):
    mode = "audio" if has_audio else "text"
    logger.info(f"Request ({mode}): {user_query[:50]}...")


def log_response(advice: str, duration_ms: float):
    logger.info(f"Response ({len(advice)} chars) in {duration_ms}ms")


def log_error(error: Exception):
    logger.error(f"Error: {type(error).__name__}: {error}")


def log_pipeline_start(audio_size: int):
    logger.debug(f"Pipeline start (audio: {audio_size} bytes)")


def log_pipeline_end(transcript: str, advice: str):
    logger.debug(f"Pipeline: {len(transcript)} chars -> {len(advice)} chars")
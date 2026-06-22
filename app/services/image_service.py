import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


async def generate_image(prompt: str) -> str | None:
    """Generate an image for a blog post. Requires a configured image API.

    Supported providers (when API key is set):
    - OpenRouter: IMAGE_API_KEY + IMAGE_MODEL env vars
    - Future: Flux, DALL-E, Stable Diffusion

    Returns the image URL, or None if image generation is not configured.
    """
    api_key = settings.image_api_key if hasattr(settings, 'image_api_key') else None
    if not api_key:
        logger.info(
            "Image generation skipped — IMAGE_API_KEY not configured.\n"
            "  To enable: set IMAGE_API_KEY and IMAGE_MODEL env vars.\n"
            "  Prompt was: %s", prompt[:80]
        )
        return None

    model = settings.image_model if hasattr(settings, 'image_model') else "flux"
    logger.info("Generating image with %s: %s...", model, prompt[:60])

    try:
        import httpx
        if "openrouter" in model.lower():
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    "https://openrouter.ai/api/v1/images/generations",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={"model": model, "prompt": prompt, "n": 1, "size": "1024x1024"},
                )
                resp.raise_for_status()
                data = resp.json()
                url = data.get("data", [{}])[0].get("url", "")
                if url:
                    logger.info("Image generated: %s", url[:60])
                    return url
        else:
            logger.warning("Unknown image model: %s", model)
        return None
    except Exception as e:
        logger.exception("Image generation failed: %s", e)
        return None


async def generate_blog_image(title: str, image_prompt: str) -> str | None:
    """Generate a cover image for a blog post."""
    return await generate_image(image_prompt or f"Ilustrasi flat design tentang {title}")

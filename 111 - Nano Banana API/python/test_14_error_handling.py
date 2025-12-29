"""Test: Python Error Handling (lines 1074-1123)"""
import sys, os
OUTPUT_DIR = "../output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Implementation from document (lines 1074-1123)
from google import genai
from google.genai import types
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_image_safely(prompt: str, output_path: str) -> bool:
    """Generate an image with proper error handling."""

    client = genai.Client()

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
            )
        )

        image_saved = False
        for part in response.parts:
            if part.text is not None:
                logger.info(f"Response text: {part.text}")
            elif image := part.as_image():
                image.save(output_path)
                logger.info(f"Image saved to {output_path}")
                image_saved = True

        if not image_saved:
            logger.warning("No image was generated in the response")
            return False

        return True

    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        raise


def test():
    print("=" * 60)
    print("Test: Python Error Handling (lines 1074-1123)")
    print("=" * 60)

    # Test the function from the document
    output_path = os.path.join(OUTPUT_DIR, "test_14_error_handling.png")

    print("[...] Testing generate_image_safely function...")
    try:
        success = generate_image_safely(
            "A beautiful sunset over mountains",
            output_path
        )

        if success:
            print(f"[OK] Function returned True")
            print(f"[OK] File created: {output_path} ({os.path.getsize(output_path):,} bytes)")
            print("Test: PASSED")
            return True
        else:
            print("[WARN] Function returned False (no image)")
            return False

    except Exception as e:
        print(f"[ERROR] Exception raised: {e}")
        return False


if __name__ == "__main__":
    try:
        result = test()
        if not result:
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

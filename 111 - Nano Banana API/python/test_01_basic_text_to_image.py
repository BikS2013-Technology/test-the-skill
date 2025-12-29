"""
Test script for: Python Basic Text-to-Image Generation
From document: 111 - Nano-Banana-API-Guide.md
Document lines: 96-116

Tests the basic text-to-image generation example from the training guide.
"""
import sys
import os

# Ensure output directory exists
OUTPUT_DIR = "../output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def validate_environment():
    """Validate required environment variables."""
    required_vars = ["GEMINI_API_KEY"]
    missing = [var for var in required_vars if not os.environ.get(var)]
    if missing:
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")


def test_basic_text_to_image():
    """Test the basic text-to-image generation from the guide."""
    print("=" * 60)
    print("Test: Python Basic Text-to-Image (lines 96-116)")
    print("=" * 60)

    # Validate environment
    validate_environment()
    print("[OK] Environment validated - GEMINI_API_KEY present")

    # Implementation from document (lines 96-116)
    from google import genai
    from google.genai import types

    # Initialize client (reads GEMINI_API_KEY from environment)
    client = genai.Client()
    print("[OK] Client initialized")

    # Generate image from text prompt
    print("[...] Generating image - this may take a moment...")
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=["A watercolor painting of a fox in a snowy forest"],
    )
    print("[OK] Response received from API")

    # Process and save the response
    image_saved = False
    output_path = os.path.join(OUTPUT_DIR, "test_01_fox_painting.png")

    for part in response.parts:
        if part.text is not None:
            print(f"[INFO] Response text: {part.text[:200]}..." if len(part.text) > 200 else f"[INFO] Response text: {part.text}")
        elif image := part.as_image():
            image.save(output_path)
            print(f"[OK] Image saved as {output_path}")
            image_saved = True

    # Verification
    if not image_saved:
        raise RuntimeError("No image was generated in the response")

    if not os.path.exists(output_path):
        raise RuntimeError(f"Output file not created: {output_path}")

    file_size = os.path.getsize(output_path)
    print(f"[OK] Output file exists ({file_size:,} bytes)")

    print("\n" + "=" * 60)
    print("Test: PASSED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        test_basic_text_to_image()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

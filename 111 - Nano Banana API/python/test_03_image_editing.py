"""
Test script for: Python Image Editing (Inpainting)
From document: 111 - Nano-Banana-API-Guide.md
Document lines: 150-176

Tests the image editing/inpainting example from the training guide.
Uses mock living_room.png image created for validation.
"""
import sys
import os

# Ensure output directory exists
OUTPUT_DIR = "../output"
MOCK_DIR = "../mock-images"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def validate_environment():
    """Validate required environment variables."""
    required_vars = ["GEMINI_API_KEY"]
    missing = [var for var in required_vars if not os.environ.get(var)]
    if missing:
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")


def test_image_editing():
    """Test the image editing (inpainting) from the guide."""
    print("=" * 60)
    print("Test: Python Image Editing/Inpainting (lines 150-176)")
    print("=" * 60)

    # Validate environment
    validate_environment()
    print("[OK] Environment validated - GEMINI_API_KEY present")

    # Implementation from document (lines 150-176)
    from google import genai
    from google.genai import types
    from PIL import Image

    client = genai.Client()
    print("[OK] Client initialized")

    # Load the source image (using mock image)
    source_image_path = os.path.join(MOCK_DIR, 'living_room.png')
    if not os.path.exists(source_image_path):
        raise FileNotFoundError(f"Mock image not found: {source_image_path}")

    source_image = Image.open(source_image_path)
    print(f"[OK] Source image loaded: {source_image_path}")

    # Define the editing instruction
    edit_prompt = """Using the provided image of a living room, change only the
blue sofa to be a vintage, brown leather chesterfield sofa. Keep the rest
of the room, including the pillows on the sofa and the lighting, unchanged."""

    print("[...] Editing image - this may take a moment...")
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[source_image, edit_prompt],
    )
    print("[OK] Response received from API")

    # Process response
    image_saved = False
    output_path = os.path.join(OUTPUT_DIR, "test_03_living_room_edited.png")

    for part in response.parts:
        if part.text is not None:
            print(f"[INFO] Response text: {part.text[:200]}..." if len(part.text) > 200 else f"[INFO] Response text: {part.text}")
        elif part.inline_data is not None:
            image = part.as_image()
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
        test_image_editing()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

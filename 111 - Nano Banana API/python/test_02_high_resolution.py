"""
Test script for: Python High-Resolution Image Generation (Nano Banana Pro)
From document: 111 - Nano-Banana-API-Guide.md
Document lines: 120-146

Tests the high-resolution image generation with Nano Banana Pro example.
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


def test_high_resolution_generation():
    """Test the high-resolution image generation from the guide."""
    print("=" * 60)
    print("Test: Python High-Resolution Generation (lines 120-146)")
    print("=" * 60)

    # Validate environment
    validate_environment()
    print("[OK] Environment validated - GEMINI_API_KEY present")

    # Implementation from document (lines 120-146)
    from google import genai
    from google.genai import types

    client = genai.Client()
    print("[OK] Client initialized")

    # Available aspect ratios: "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"
    # Available resolutions: "1K", "2K", "4K" (Nano Banana Pro only)

    print("[...] Generating high-resolution image with Nano Banana Pro...")
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents="A detailed infographic about the water cycle with labeled diagrams",
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
            image_config=types.ImageConfig(
                aspect_ratio="16:9",
                image_size="2K"  # Must be uppercase
            ),
        )
    )
    print("[OK] Response received from API")

    # Process response
    image_saved = False
    output_path = os.path.join(OUTPUT_DIR, "test_02_water_cycle_infographic.png")

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

    # Check if it's a larger image (should be around 2K resolution)
    from PIL import Image
    with Image.open(output_path) as img:
        width, height = img.size
        print(f"[INFO] Image dimensions: {width}x{height}")

    print("\n" + "=" * 60)
    print("Test: PASSED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        test_high_resolution_generation()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

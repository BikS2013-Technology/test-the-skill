"""
Test script for: Python Multiple Reference Images for Character Consistency
From document: 111 - Nano-Banana-API-Guide.md
Document lines: 180-213

Tests the multiple reference images example from the training guide.
Uses mock person images created for validation.
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


def test_multiple_reference_images():
    """Test multiple reference images for character consistency."""
    print("=" * 60)
    print("Test: Python Multiple Reference Images (lines 180-213)")
    print("=" * 60)

    # Validate environment
    validate_environment()
    print("[OK] Environment validated - GEMINI_API_KEY present")

    # Implementation from document (lines 180-213)
    from google import genai
    from google.genai import types
    from PIL import Image

    client = genai.Client()
    print("[OK] Client initialized")

    # Load mock person images
    person_images = []
    for i in range(1, 6):
        img_path = os.path.join(MOCK_DIR, f'person{i}.png')
        if not os.path.exists(img_path):
            raise FileNotFoundError(f"Mock image not found: {img_path}")
        person_images.append(Image.open(img_path))
        print(f"[OK] Loaded: person{i}.png")

    prompt = "An office group photo of these people, they are making funny faces."

    print("[...] Generating image with multiple references - this may take a moment...")
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=[
            prompt,
            person_images[0],
            person_images[1],
            person_images[2],
            person_images[3],
            person_images[4],
        ],
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
            image_config=types.ImageConfig(
                aspect_ratio="5:4",
                image_size="2K"
            ),
        )
    )
    print("[OK] Response received from API")

    # Process response
    image_saved = False
    output_path = os.path.join(OUTPUT_DIR, "test_04_office_photo.png")

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

    file_size = os.path.getsize(output_path)
    print(f"[OK] Output file exists ({file_size:,} bytes)")

    print("\n" + "=" * 60)
    print("Test: PASSED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        test_multiple_reference_images()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

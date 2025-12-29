"""
Test script for: Python Image Blending (Logo on Clothing) - WITH response_modalities
From document: 111 - Nano-Banana-API-Guide.md
Document lines: 217-243

Testing if adding response_modalities config fixes the issue.
"""
import sys
import os

OUTPUT_DIR = "../output"
MOCK_DIR = "../mock-images"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def validate_environment():
    """Validate required environment variables."""
    required_vars = ["GEMINI_API_KEY"]
    missing = [var for var in required_vars if not os.environ.get(var)]
    if missing:
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")


def test_image_blending_with_config():
    """Test image blending with explicit response_modalities."""
    print("=" * 60)
    print("Test: Python Image Blending v2 - WITH response_modalities")
    print("=" * 60)

    validate_environment()
    print("[OK] Environment validated - GEMINI_API_KEY present")

    from google import genai
    from google.genai import types
    from PIL import Image

    client = genai.Client()
    print("[OK] Client initialized")

    # Load mock images
    person_path = os.path.join(MOCK_DIR, 'woman_tshirt.png')
    logo_path = os.path.join(MOCK_DIR, 'company_logo.png')

    person_image = Image.open(person_path)
    logo_image = Image.open(logo_path)
    print(f"[OK] Loaded images")

    prompt = """Take the first image of the woman with brown hair, blue eyes,
and a neutral expression. Add the logo from the second image onto her black
t-shirt. Ensure the woman's face and features remain completely unchanged.
The logo should look like it's naturally printed on the fabric, following
the folds of the shirt."""

    print("[...] Blending images WITH response_modalities config...")
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[person_image, logo_image, prompt],
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],  # Added this config
        )
    )
    print("[OK] Response received from API")

    # Process response
    image_saved = False
    output_path = os.path.join(OUTPUT_DIR, "test_05_woman_with_logo_v2.png")

    for part in response.parts:
        if part.text is not None:
            print(f"[INFO] Response text: {part.text[:300]}..." if len(part.text) > 300 else f"[INFO] Response text: {part.text}")
        elif image := part.as_image():
            image.save(output_path)
            print(f"[OK] Image saved as {output_path}")
            image_saved = True

    if image_saved:
        file_size = os.path.getsize(output_path)
        print(f"[OK] Output file exists ({file_size:,} bytes)")
        print("\n" + "=" * 60)
        print("Test: PASSED - Adding response_modalities FIXES the issue")
        print("=" * 60)
        return True
    else:
        print("\n" + "=" * 60)
        print("Test: FAILED - Still no image even with response_modalities")
        print("=" * 60)
        return False


if __name__ == "__main__":
    try:
        result = test_image_blending_with_config()
        if not result:
            sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

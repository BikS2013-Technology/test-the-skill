"""
Test script for: Python Infographic Generation
From document: 111 - Nano-Banana-API-Guide.md
Document lines: 478-506
"""
import sys
import os

OUTPUT_DIR = "../output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def validate_environment():
    required_vars = ["GEMINI_API_KEY"]
    missing = [var for var in required_vars if not os.environ.get(var)]
    if missing:
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")

def test_infographic():
    print("=" * 60)
    print("Test: Python Infographic (lines 478-506)")
    print("=" * 60)

    validate_environment()
    print("[OK] Environment validated")

    from google import genai
    from google.genai import types

    client = genai.Client()
    print("[OK] Client initialized")

    prompt = """Create a vibrant infographic that explains photosynthesis as if
it were a recipe for a plant's favorite food. Show the "ingredients"
(sunlight, water, CO2) and the "finished dish" (sugar/energy). The style
should be like a page from a colorful kids' cookbook, suitable for a 4th grader."""

    print("[...] Generating infographic...")
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
            image_config=types.ImageConfig(
                aspect_ratio="3:4",
                image_size="2K"
            ),
        )
    )
    print("[OK] Response received")

    image_saved = False
    output_path = os.path.join(OUTPUT_DIR, "test_06_photosynthesis_infographic.png")

    for part in response.parts:
        if part.text is not None:
            print(f"[INFO] Response text: {part.text[:150]}..." if len(part.text) > 150 else f"[INFO] Response text: {part.text}")
        elif image := part.as_image():
            image.save(output_path)
            print(f"[OK] Image saved as {output_path}")
            image_saved = True

    if not image_saved:
        raise RuntimeError("No image was generated")

    file_size = os.path.getsize(output_path)
    print(f"[OK] Output file exists ({file_size:,} bytes)")
    print("\n" + "=" * 60)
    print("Test: PASSED")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        test_infographic()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

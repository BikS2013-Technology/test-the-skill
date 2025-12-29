"""Test: Python Tutorial/Process Diagram (lines 758-795)"""
import sys, os
OUTPUT_DIR = "../output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def test():
    print("=" * 60)
    print("Test: Python Tutorial/Process Diagram (lines 758-795)")
    print("=" * 60)

    from google import genai
    from google.genai import types

    client = genai.Client()
    print("[OK] Client initialized")

    prompt = """Create a step-by-step tutorial image showing how to make
pour-over coffee in 6 steps:

Step 1: Boil water to 200°F (93°C)
Step 2: Grind coffee beans to medium-fine consistency
Step 3: Place filter in dripper and rinse with hot water
Step 4: Add ground coffee and create a small well in the center
Step 5: Pour water in circular motion, starting from center
Step 6: Wait for complete drip-through (3-4 minutes)

Style: Clean, modern illustration with numbered steps arranged in a
2x3 grid. Include helpful tips and timing for each step. Use a warm
coffee-shop color palette."""

    print("[...] Generating tutorial diagram...")
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
            image_config=types.ImageConfig(
                aspect_ratio="4:3",
                image_size="2K"
            ),
        )
    )

    output_path = os.path.join(OUTPUT_DIR, "test_11_tutorial.png")
    for part in response.parts:
        if part.text:
            print(f"[INFO] Text: {part.text[:150]}...")
        elif image := part.as_image():
            image.save(output_path)
            print(f"[OK] Saved: {output_path} ({os.path.getsize(output_path):,} bytes)")
            print("Test: PASSED")
            return True
    raise RuntimeError("No image generated")

if __name__ == "__main__":
    try:
        test()
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

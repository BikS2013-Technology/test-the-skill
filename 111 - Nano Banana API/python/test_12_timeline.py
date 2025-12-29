"""Test: Python Timeline (lines 803-848)"""
import sys, os
OUTPUT_DIR = "../output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def test():
    print("=" * 60)
    print("Test: Python Timeline (lines 803-848)")
    print("=" * 60)

    from google import genai
    from google.genai import types

    client = genai.Client()
    print("[OK] Client initialized")

    prompt = """Create a timeline visualization showing the evolution of
programming languages from 1950 to 2024:

Key milestones:
- 1957: FORTRAN
- 1959: COBOL
- 1970: Pascal
- 1972: C
- 1983: C++
- 1991: Python
- 1995: Java, JavaScript, PHP
- 2000: C#
- 2009: Go
- 2010: Rust
- 2014: Swift
- 2024: Modern AI-assisted coding

Style: Horizontal timeline with icons representing each language.
Include brief descriptions and color-code by language paradigm
(procedural, object-oriented, functional). Modern, clean design
suitable for a tech presentation."""

    print("[...] Generating timeline...")
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
            image_config=types.ImageConfig(
                aspect_ratio="21:9",
                image_size="2K"
            ),
        )
    )

    output_path = os.path.join(OUTPUT_DIR, "test_12_timeline.png")
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

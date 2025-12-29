"""Test: Python Flowchart (lines 600-644)"""
import sys, os
OUTPUT_DIR = "../output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def test():
    print("=" * 60)
    print("Test: Python Flowchart (lines 600-644)")
    print("=" * 60)

    from google import genai
    from google.genai import types

    client = genai.Client()
    print("[OK] Client initialized")

    prompt = """Create a detailed flowchart for a user authentication process
with 2-factor authentication:

1. Start: User enters credentials
2. Decision: Are credentials valid?
   - No: Show error, return to step 1
   - Yes: Continue
3. Generate 2FA code and send to user
4. User enters 2FA code
5. Decision: Is 2FA code valid?
   - No: Allow retry (max 3 attempts)
   - Yes: Grant access
6. Decision: Max retries exceeded?
   - Yes: Lock account, notify admin
   - No: Return to step 4
7. End: User authenticated

Use standard flowchart symbols (rectangles for processes, diamonds for
decisions, ovals for start/end). Use a clean, professional style with
clear labels on all connections."""

    print("[...] Generating flowchart...")
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

    output_path = os.path.join(OUTPUT_DIR, "test_08_flowchart.png")
    for part in response.parts:
        if part.text:
            print(f"[INFO] Text: {part.text[:100]}...")
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

"""Test: Python Sequence Diagram (lines 704-750)"""
import sys, os
OUTPUT_DIR = "../output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def test():
    print("=" * 60)
    print("Test: Python Sequence Diagram (lines 704-750)")
    print("=" * 60)

    from google import genai
    from google.genai import types

    client = genai.Client()
    print("[OK] Client initialized")

    prompt = """Create a sequence diagram showing REST API authentication flow:

Participants:
- Client (web browser)
- API Gateway
- Auth Service
- User Database
- Token Store (Redis)

Flow:
1. Client sends POST /login with credentials
2. API Gateway forwards to Auth Service
3. Auth Service queries User Database
4. User Database returns user data
5. Auth Service generates JWT token
6. Auth Service stores token in Token Store
7. Token Store confirms storage
8. Auth Service returns token to API Gateway
9. API Gateway returns token to Client

Include request/response details on arrows. Use standard UML sequence
diagram notation with lifelines, activation bars, and message arrows."""

    print("[...] Generating sequence diagram...")
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

    output_path = os.path.join(OUTPUT_DIR, "test_10_sequence.png")
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

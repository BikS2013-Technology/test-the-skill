"""Test: Python Architecture Diagram (lines 554-592)"""
import sys, os
OUTPUT_DIR = "../output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def test():
    print("=" * 60)
    print("Test: Python Architecture Diagram (lines 554-592)")
    print("=" * 60)

    from google import genai
    from google.genai import types

    client = genai.Client()
    print("[OK] Client initialized")

    prompt = """Create a professional system architecture diagram showing a
microservices architecture with the following components:
- API Gateway (center)
- User Service
- Product Service
- Order Service
- Payment Service
- Notification Service
- PostgreSQL databases for each service
- Redis for caching
- RabbitMQ for message queuing

Use clean lines, modern icons, and a professional color scheme.
Include arrows showing data flow between services."""

    print("[...] Generating architecture diagram...")
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
            image_config=types.ImageConfig(
                aspect_ratio="16:9",
                image_size="2K"
            ),
        )
    )

    output_path = os.path.join(OUTPUT_DIR, "test_07_architecture.png")
    for part in response.parts:
        if part.text:
            print(f"[INFO] Text: {part.text[:100]}...")
        elif image := part.as_image():
            image.save(output_path)
            print(f"[OK] Saved: {output_path}")
            print(f"[OK] Size: {os.path.getsize(output_path):,} bytes")
            print("Test: PASSED")
            return True
    raise RuntimeError("No image generated")

if __name__ == "__main__":
    try:
        test()
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

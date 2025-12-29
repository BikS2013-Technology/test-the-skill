"""Test: Python Multi-Turn Editing (lines 858-919)"""
import sys, os
OUTPUT_DIR = "../output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def test():
    print("=" * 60)
    print("Test: Python Multi-Turn Editing (lines 858-919)")
    print("=" * 60)

    from google import genai
    from google.genai import types

    client = genai.Client()
    print("[OK] Client initialized")

    # Create a chat session with image generation capabilities
    chat = client.chats.create(
        model="gemini-3-pro-image-preview",
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
            tools=[{"google_search": {}}]  # Optional: enable web search for accuracy
        )
    )
    print("[OK] Chat session created")

    # Initial image generation
    message1 = """Create a vibrant infographic that explains photosynthesis
as if it were a recipe for a plant's favorite food. Show the "ingredients"
(sunlight, water, CO2) and the "finished dish" (sugar/energy). The style
should be like a page from a colorful kids' cookbook, suitable for a 4th grader."""

    print("[...] Generating initial image...")
    response1 = chat.send_message(message1)

    image_saved = False
    output_path1 = os.path.join(OUTPUT_DIR, "test_13_multiturn_v1.png")

    for part in response1.parts:
        if part.text is not None:
            print(f"[INFO] Initial text: {part.text[:100]}...")
        elif image := part.as_image():
            image.save(output_path1)
            print(f"[OK] Saved initial: {output_path1}")
            image_saved = True

    if not image_saved:
        raise RuntimeError("No initial image generated")

    # First refinement - change language
    message2 = "Update this infographic to be in Spanish. Do not change any other elements of the image."

    print("[...] Sending refinement request...")
    response2 = chat.send_message(
        message2,
        config=types.GenerateContentConfig(
            image_config=types.ImageConfig(
                aspect_ratio="16:9",
                image_size="2K"
            ),
        )
    )

    output_path2 = os.path.join(OUTPUT_DIR, "test_13_multiturn_spanish.png")

    for part in response2.parts:
        if part.text is not None:
            print(f"[INFO] Refinement text: {part.text[:100]}...")
        elif image := part.as_image():
            image.save(output_path2)
            print(f"[OK] Saved refined: {output_path2}")

    print(f"[OK] Initial file size: {os.path.getsize(output_path1):,} bytes")
    print("Test: PASSED")
    return True

if __name__ == "__main__":
    try:
        test()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

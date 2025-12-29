"""Test: Python Database ERD (lines 652-696)"""
import sys, os
OUTPUT_DIR = "../output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def test():
    print("=" * 60)
    print("Test: Python Database ERD (lines 652-696)")
    print("=" * 60)

    from google import genai
    from google.genai import types

    client = genai.Client()
    print("[OK] Client initialized")

    prompt = """Create a database schema diagram (ERD) for an e-commerce system
with the following entities and relationships:

Entities:
- Customer (id, email, name, created_at)
- Order (id, customer_id, total, status, created_at)
- OrderItem (id, order_id, product_id, quantity, price)
- Product (id, name, description, price, stock)
- Category (id, name, parent_id)
- ProductCategory (product_id, category_id)

Relationships:
- Customer has many Orders (1:N)
- Order has many OrderItems (1:N)
- Product has many OrderItems (1:N)
- Product has many Categories through ProductCategory (M:N)
- Category has many sub-Categories (self-referential)

Use standard database diagram notation with primary keys marked (PK),
foreign keys marked (FK), and crow's foot notation for cardinality."""

    print("[...] Generating ERD...")
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

    output_path = os.path.join(OUTPUT_DIR, "test_09_erd.png")
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

"""
Create mock images for testing Nano Banana API examples.
These are simple placeholder images used for validation testing.
"""
import os
from PIL import Image, ImageDraw, ImageFont

# Output directory for mock images
MOCK_DIR = "../mock-images"
os.makedirs(MOCK_DIR, exist_ok=True)

def create_living_room_mock():
    """Create a mock living room image with a blue rectangle (representing sofa)."""
    img = Image.new('RGB', (800, 600), color='#F5F5DC')  # Beige background
    draw = ImageDraw.Draw(img)

    # Floor
    draw.rectangle([0, 400, 800, 600], fill='#8B4513')

    # Blue sofa (rectangle)
    draw.rectangle([200, 280, 600, 420], fill='#4169E1', outline='#2E4A7D', width=3)

    # Pillows on sofa
    draw.ellipse([220, 290, 280, 350], fill='#FFD700')
    draw.ellipse([520, 290, 580, 350], fill='#FF6347')

    # Window
    draw.rectangle([300, 50, 500, 200], fill='#87CEEB', outline='#8B4513', width=5)

    # Coffee table
    draw.rectangle([280, 440, 520, 480], fill='#654321', outline='#3D2314', width=2)

    img.save(os.path.join(MOCK_DIR, 'living_room.png'))
    print(f"Created: {MOCK_DIR}/living_room.png")

def create_person_mocks():
    """Create simple person silhouette images for reference testing."""
    colors = ['#FFB6C1', '#98FB98', '#87CEEB', '#DDA0DD', '#F0E68C']

    for i, color in enumerate(colors, 1):
        img = Image.new('RGB', (400, 500), color='#FFFFFF')
        draw = ImageDraw.Draw(img)

        # Simple person silhouette
        # Head
        draw.ellipse([150, 30, 250, 130], fill=color, outline='#333333', width=2)

        # Body
        draw.rectangle([160, 130, 240, 300], fill=color, outline='#333333', width=2)

        # Arms
        draw.rectangle([100, 140, 160, 250], fill=color, outline='#333333', width=2)
        draw.rectangle([240, 140, 300, 250], fill=color, outline='#333333', width=2)

        # Legs
        draw.rectangle([160, 300, 195, 450], fill=color, outline='#333333', width=2)
        draw.rectangle([205, 300, 240, 450], fill=color, outline='#333333', width=2)

        # Label
        draw.text((150, 460), f"Person {i}", fill='#333333')

        img.save(os.path.join(MOCK_DIR, f'person{i}.png'))
        print(f"Created: {MOCK_DIR}/person{i}.png")

def create_woman_tshirt_mock():
    """Create a mock woman in t-shirt image."""
    img = Image.new('RGB', (400, 500), color='#FFFFFF')
    draw = ImageDraw.Draw(img)

    # Head with brown hair
    draw.ellipse([150, 20, 250, 120], fill='#FFDAB9')  # Face
    draw.ellipse([140, 10, 260, 80], fill='#8B4513')   # Hair

    # Black t-shirt body
    draw.polygon([(130, 120), (200, 130), (270, 120), (280, 300), (120, 300)],
                 fill='#000000', outline='#333333')

    # Arms
    draw.rectangle([80, 130, 130, 250], fill='#FFDAB9')
    draw.rectangle([270, 130, 320, 250], fill='#FFDAB9')

    # T-shirt area marker
    draw.rectangle([160, 160, 240, 240], outline='#444444', width=1)
    draw.text((165, 190), "Logo\nArea", fill='#666666')

    img.save(os.path.join(MOCK_DIR, 'woman_tshirt.png'))
    print(f"Created: {MOCK_DIR}/woman_tshirt.png")

def create_logo_mock():
    """Create a simple company logo mock."""
    img = Image.new('RGB', (200, 200), color='#FFFFFF')
    draw = ImageDraw.Draw(img)

    # Simple logo: circle with text
    draw.ellipse([20, 20, 180, 180], fill='#FF4500', outline='#CC3700', width=3)
    draw.text((60, 80), "LOGO", fill='#FFFFFF')

    img.save(os.path.join(MOCK_DIR, 'company_logo.png'))
    print(f"Created: {MOCK_DIR}/company_logo.png")

if __name__ == "__main__":
    print("Creating mock images for Nano Banana API validation...")
    create_living_room_mock()
    create_person_mocks()
    create_woman_tshirt_mock()
    create_logo_mock()
    print("\nAll mock images created successfully!")

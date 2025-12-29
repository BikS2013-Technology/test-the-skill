# Google Nano Banana API Guide

A comprehensive guide for building images, diagrams, infographics, and visual artifacts using Google's Nano Banana API (Gemini Image Generation).

## Table of Contents

1. [Overview](#overview)
2. [Available Models](#available-models)
3. [Authentication Setup](#authentication-setup)
4. [Python Implementation](#python-implementation)
5. [TypeScript/Node.js Implementation](#typescriptnodejs-implementation)
6. [Image Generation Parameters](#image-generation-parameters)
7. [Visual Artifact Types](#visual-artifact-types)
8. [Multi-Turn Editing](#multi-turn-editing)
9. [Prompting Best Practices](#prompting-best-practices)
10. [Error Handling](#error-handling)
11. [Pricing and Limits](#pricing-and-limits)

---

## Overview

**Nano Banana** is Google's native image generation capability within the Gemini API. It enables:

- **Text-to-Image Generation**: Create images from text descriptions
- **Image Editing (Inpainting)**: Modify specific elements of existing images
- **Image Blending**: Combine multiple images into a single image
- **Character Consistency**: Maintain consistent characters across multiple images
- **High-Fidelity Text Rendering**: Generate images with legible text
- **Multi-Turn Editing**: Iteratively refine images through conversation

All generated images include a **SynthID watermark** to identify AI-generated content.

---

## Available Models

### Nano Banana (Gemini 2.5 Flash Image)

| Property | Value |
|----------|-------|
| **Model ID** | `gemini-2.5-flash-image` |
| **Purpose** | Speed and efficiency |
| **Best For** | High-volume, low-latency tasks |
| **Max Resolution** | 1K |
| **Pricing** | $0.039 per image |

### Nano Banana Pro (Gemini 3 Pro Image Preview)

| Property | Value |
|----------|-------|
| **Model ID** | `gemini-3-pro-image-preview` |
| **Purpose** | Professional asset production |
| **Best For** | Complex images with text, detailed visualizations |
| **Max Resolution** | 4K |
| **Features** | Advanced reasoning ("Thinking"), high-fidelity text rendering |
| **Reference Images** | Up to 14 (6 object + 5 human for character consistency) |

---

## Authentication Setup

### Getting an API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Navigate to API Keys section
4. Create a new API key

### Environment Variable Setup

```bash
# Linux/macOS
export GEMINI_API_KEY="your-api-key-here"

# Windows (PowerShell)
$env:GEMINI_API_KEY="your-api-key-here"

# Windows (CMD)
set GEMINI_API_KEY=your-api-key-here
```

---

## Python Implementation

### Installation

```bash
# Using UV (recommended per project guidelines)
uv add google-genai pillow
```

### Basic Text-to-Image Generation

```python
from google import genai
from google.genai import types

# Initialize client (reads GEMINI_API_KEY from environment)
client = genai.Client()

# Generate image from text prompt
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=["A watercolor painting of a fox in a snowy forest"],
)

# Process and save the response
for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif image := part.as_image():
        image.save("fox_painting.png")
        print("Image saved as fox_painting.png")
```

### High-Resolution Image Generation (Nano Banana Pro)

```python
from google import genai
from google.genai import types

client = genai.Client()

# Available aspect ratios: "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"
# Available resolutions: "1K", "2K", "4K" (Nano Banana Pro only)

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="A detailed infographic about the water cycle with labeled diagrams",
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
            image_size="2K"  # Must be uppercase
        ),
    )
)

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif image := part.as_image():
        image.save("water_cycle_infographic.png")
```

### Image Editing (Inpainting)

```python
from google import genai
from google.genai import types
from PIL import Image

client = genai.Client()

# Load the source image
source_image = Image.open('living_room.png')

# Define the editing instruction
edit_prompt = """Using the provided image of a living room, change only the
blue sofa to be a vintage, brown leather chesterfield sofa. Keep the rest
of the room, including the pillows on the sofa and the lighting, unchanged."""

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[source_image, edit_prompt],
)

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = part.as_image()
        image.save("living_room_edited.png")
```

### Multiple Reference Images for Character Consistency

```python
from google import genai
from google.genai import types
from PIL import Image

client = genai.Client()

prompt = "An office group photo of these people, they are making funny faces."

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[
        prompt,
        Image.open('person1.png'),
        Image.open('person2.png'),
        Image.open('person3.png'),
        Image.open('person4.png'),
        Image.open('person5.png'),
    ],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        image_config=types.ImageConfig(
            aspect_ratio="5:4",
            image_size="2K"
        ),
    )
)

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif image := part.as_image():
        image.save("office_photo.png")
```

### Image Blending (Logo on Clothing)

```python
from google import genai
from google.genai import types
from PIL import Image

client = genai.Client()

person_image = Image.open('woman_tshirt.png')
logo_image = Image.open('company_logo.png')

prompt = """Take the first image of the woman with brown hair, blue eyes,
and a neutral expression. Add the logo from the second image onto her black
t-shirt. Ensure the woman's face and features remain completely unchanged.
The logo should look like it's naturally printed on the fabric, following
the folds of the shirt."""

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[person_image, logo_image, prompt],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
    )
)

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif image := part.as_image():
        image.save("woman_with_logo.png")
```

---

## TypeScript/Node.js Implementation

### Installation

```bash
npm install @google/genai
```

### Basic Text-to-Image Generation

```typescript
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

async function generateImage(): Promise<void> {
  // Initialize client (reads GEMINI_API_KEY from environment)
  const ai = new GoogleGenAI({});

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image",
    contents: "A watercolor painting of a fox in a snowy forest",
  });

  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      console.log(part.text);
    } else if (part.inlineData) {
      const imageData = part.inlineData.data;
      const buffer = Buffer.from(imageData, "base64");
      fs.writeFileSync("fox_painting.png", buffer);
      console.log("Image saved as fox_painting.png");
    }
  }
}

generateImage();
```

### High-Resolution Image Generation (Nano Banana Pro)

```typescript
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

async function generateHighResImage(): Promise<void> {
  const ai = new GoogleGenAI({});

  const response = await ai.models.generateContent({
    model: "gemini-3-pro-image-preview",
    contents: "A detailed infographic about the water cycle with labeled diagrams",
    config: {
      responseModalities: ["TEXT", "IMAGE"],
      imageConfig: {
        aspectRatio: "16:9",  // Options: "1:1","2:3","3:2","3:4","4:3","4:5","5:4","9:16","16:9","21:9"
        imageSize: "2K",      // Options: "1K", "2K", "4K"
      },
    },
  });

  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      console.log(part.text);
    } else if (part.inlineData) {
      const buffer = Buffer.from(part.inlineData.data, "base64");
      fs.writeFileSync("water_cycle_infographic.png", buffer);
      console.log("Image saved as water_cycle_infographic.png");
    }
  }
}

generateHighResImage();
```

### Image Editing (Inpainting)

```typescript
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

async function editImage(): Promise<void> {
  const ai = new GoogleGenAI({});

  // Read and encode source image
  const imagePath = "./living_room.png";
  const imageData = fs.readFileSync(imagePath);
  const base64Image = imageData.toString("base64");

  const prompt = [
    {
      inlineData: {
        mimeType: "image/png",
        data: base64Image,
      },
    },
    {
      text: `Using the provided image of a living room, change only the
             blue sofa to be a vintage, brown leather chesterfield sofa.
             Keep the rest of the room, including the pillows on the sofa
             and the lighting, unchanged.`,
    },
  ];

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image",
    contents: prompt,
  });

  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      console.log(part.text);
    } else if (part.inlineData) {
      const buffer = Buffer.from(part.inlineData.data, "base64");
      fs.writeFileSync("living_room_edited.png", buffer);
      console.log("Image saved as living_room_edited.png");
    }
  }
}

editImage();
```

### Multiple Reference Images

```typescript
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

async function generateWithReferences(): Promise<void> {
  const ai = new GoogleGenAI({});

  // Helper function to encode images
  const encodeImage = (path: string): string => {
    return fs.readFileSync(path).toString("base64");
  };

  const contents = [
    { text: "An office group photo of these people, they are making funny faces." },
    {
      inlineData: {
        mimeType: "image/png",
        data: encodeImage("person1.png"),
      },
    },
    {
      inlineData: {
        mimeType: "image/png",
        data: encodeImage("person2.png"),
      },
    },
    {
      inlineData: {
        mimeType: "image/png",
        data: encodeImage("person3.png"),
      },
    },
  ];

  const response = await ai.models.generateContent({
    model: "gemini-3-pro-image-preview",
    contents: contents,
    config: {
      responseModalities: ["TEXT", "IMAGE"],
      imageConfig: {
        aspectRatio: "5:4",
        imageSize: "2K",
      },
    },
  });

  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      console.log(part.text);
    } else if (part.inlineData) {
      const buffer = Buffer.from(part.inlineData.data, "base64");
      fs.writeFileSync("office_photo.png", buffer);
      console.log("Image saved as office_photo.png");
    }
  }
}

generateWithReferences();
```

---

## Image Generation Parameters

### Aspect Ratios

| Ratio | Use Case |
|-------|----------|
| `1:1` | Square images, profile pictures, icons |
| `2:3` | Portrait photos, mobile wallpapers |
| `3:2` | Landscape photos, presentations |
| `3:4` | Portrait documents, tablets |
| `4:3` | Standard displays, presentations |
| `4:5` | Instagram portraits |
| `5:4` | Print photos |
| `9:16` | Vertical video, mobile stories |
| `16:9` | Widescreen, YouTube thumbnails, presentations |
| `21:9` | Ultra-wide, cinematic |

### Image Resolutions

| Resolution | Approximate Size | Model Support |
|------------|------------------|---------------|
| `1K` | ~1024px | Both models |
| `2K` | ~2048px | Nano Banana Pro only |
| `4K` | ~4096px | Nano Banana Pro only |

### Response Modalities

Always include both `TEXT` and `IMAGE` in response modalities to receive descriptive text along with generated images:

```python
config=types.GenerateContentConfig(
    response_modalities=['TEXT', 'IMAGE'],
    ...
)
```

---

## Visual Artifact Types

### 1. Infographics

Infographics are ideal for explaining complex information visually.

**Python Example:**

```python
from google import genai
from google.genai import types

client = genai.Client()

prompt = """Create a vibrant infographic that explains photosynthesis as if
it were a recipe for a plant's favorite food. Show the "ingredients"
(sunlight, water, CO2) and the "finished dish" (sugar/energy). The style
should be like a page from a colorful kids' cookbook, suitable for a 4th grader."""

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

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif image := part.as_image():
        image.save("photosynthesis_infographic.png")
```

**TypeScript Example:**

```typescript
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

async function createInfographic(): Promise<void> {
  const ai = new GoogleGenAI({});

  const prompt = `Create a vibrant infographic that explains photosynthesis
                  as if it were a recipe for a plant's favorite food.
                  Show the "ingredients" (sunlight, water, CO2) and the
                  "finished dish" (sugar/energy). The style should be like
                  a page from a colorful kids' cookbook, suitable for a 4th grader.`;

  const response = await ai.models.generateContent({
    model: "gemini-3-pro-image-preview",
    contents: prompt,
    config: {
      responseModalities: ["TEXT", "IMAGE"],
      imageConfig: {
        aspectRatio: "3:4",
        imageSize: "2K",
      },
    },
  });

  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      console.log(part.text);
    } else if (part.inlineData) {
      const buffer = Buffer.from(part.inlineData.data, "base64");
      fs.writeFileSync("photosynthesis_infographic.png", buffer);
    }
  }
}

createInfographic();
```

### 2. Architecture Diagrams

Generate system architecture and technical diagrams.

**Python Example:**

```python
from google import genai
from google.genai import types

client = genai.Client()

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

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif image := part.as_image():
        image.save("microservices_architecture.png")
```

### 3. Flowcharts

Generate process flowcharts and decision trees.

**Python Example:**

```python
from google import genai
from google.genai import types

client = genai.Client()

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

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif image := part.as_image():
        image.save("auth_flowchart.png")
```

### 4. Database Schema Diagrams

Generate entity-relationship diagrams.

> **Note:** The Gemini image generation API may return text-based descriptions or diagram syntax (like Mermaid) instead of actual images for formal ERD diagrams with specific notation (PK, FK, crow's foot). For production use cases requiring precise ERD notation, consider using dedicated diagramming tools or rendering the returned Mermaid code with a Mermaid renderer.

**Python Example:**

```python
from google import genai
from google.genai import types

client = genai.Client()

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

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif image := part.as_image():
        image.save("ecommerce_erd.png")
```

### 5. Sequence Diagrams

Generate API interaction and sequence diagrams.

> **Note:** The Gemini image generation API may return text-based diagram syntax (like Mermaid) instead of actual images for UML-style sequence diagrams. For production use cases requiring precise UML notation, consider rendering the returned Mermaid code with a Mermaid renderer or using dedicated UML diagramming tools.

**Python Example:**

```python
from google import genai
from google.genai import types

client = genai.Client()

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

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif image := part.as_image():
        image.save("auth_sequence.png")
```

### 6. Process Diagrams and Tutorials

Generate step-by-step visual guides.

**Python Example:**

```python
from google import genai
from google.genai import types

client = genai.Client()

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

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif image := part.as_image():
        image.save("coffee_tutorial.png")
```

### 7. Timeline Visualizations

Generate historical or project timelines.

**Python Example:**

```python
from google import genai
from google.genai import types

client = genai.Client()

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

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif image := part.as_image():
        image.save("programming_timeline.png")
```

---

## Multi-Turn Editing

Multi-turn editing allows you to iteratively refine images through conversation, maintaining context between requests.

### Python Multi-Turn Editing

```python
from google import genai
from google.genai import types

client = genai.Client()

# Create a chat session with image generation capabilities
chat = client.chats.create(
    model="gemini-3-pro-image-preview",
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        tools=[{"google_search": {}}]  # Optional: enable web search for accuracy
    )
)

# Initial image generation
message1 = """Create a vibrant infographic that explains photosynthesis
as if it were a recipe for a plant's favorite food. Show the "ingredients"
(sunlight, water, CO2) and the "finished dish" (sugar/energy). The style
should be like a page from a colorful kids' cookbook, suitable for a 4th grader."""

response1 = chat.send_message(message1)

for part in response1.parts:
    if part.text is not None:
        print("Initial response:", part.text)
    elif image := part.as_image():
        image.save("photosynthesis_v1.png")
        print("Saved initial image")

# First refinement - change language
message2 = "Update this infographic to be in Spanish. Do not change any other elements of the image."

response2 = chat.send_message(
    message2,
    config=types.GenerateContentConfig(
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
            image_size="2K"
        ),
    )
)

for part in response2.parts:
    if part.text is not None:
        print("Refinement response:", part.text)
    elif image := part.as_image():
        image.save("photosynthesis_spanish.png")
        print("Saved Spanish version")

# Second refinement - add more detail
message3 = "Add a section showing the chemical equation: 6CO2 + 6H2O + light → C6H12O6 + 6O2"

response3 = chat.send_message(message3)

for part in response3.parts:
    if part.text is not None:
        print("Final response:", part.text)
    elif image := part.as_image():
        image.save("photosynthesis_final.png")
        print("Saved final version")
```

### TypeScript Multi-Turn Editing

```typescript
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

async function multiTurnEditing(): Promise<void> {
  const ai = new GoogleGenAI({});

  // Create chat session
  const chat = ai.chats.create({
    model: "gemini-3-pro-image-preview",
    config: {
      responseModalities: ["TEXT", "IMAGE"],
      tools: [{ googleSearch: {} }],
    },
  });

  // Initial generation
  const message1 = `Create a vibrant infographic that explains photosynthesis
                    as if it were a recipe for a plant's favorite food.`;

  let response = await chat.sendMessage({ message: message1 });

  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      console.log("Initial:", part.text);
    } else if (part.inlineData) {
      const buffer = Buffer.from(part.inlineData.data, "base64");
      fs.writeFileSync("photosynthesis_v1.png", buffer);
    }
  }

  // Refinement
  const message2 = "Update this infographic to be in Spanish.";

  response = await chat.sendMessage({
    message: message2,
    config: {
      responseModalities: ["TEXT", "IMAGE"],
      imageConfig: {
        aspectRatio: "16:9",
        imageSize: "2K",
      },
    },
  });

  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      console.log("Refined:", part.text);
    } else if (part.inlineData) {
      const buffer = Buffer.from(part.inlineData.data, "base64");
      fs.writeFileSync("photosynthesis_spanish.png", buffer);
    }
  }
}

multiTurnEditing();
```

---

## Prompting Best Practices

### General Guidelines

1. **Be Specific**: Provide detailed descriptions of what you want
2. **Include Style References**: Specify artistic style, color schemes, and visual aesthetics
3. **Define Structure**: For diagrams, clearly describe components and relationships
4. **Specify Text Requirements**: If text should appear in the image, specify exactly what it should say
5. **Use Reference Images**: For consistency, provide reference images when possible

### Prompt Templates

#### Infographic Template

```
Create a [style] infographic about [topic] that includes:
- [Main sections/components]
- [Data/statistics to include]
- [Visual elements: charts, icons, illustrations]

Style requirements:
- Color scheme: [colors]
- Font style: [modern/classic/playful]
- Target audience: [audience]
- Layout: [vertical/horizontal/grid]
```

#### Architecture Diagram Template

```
Create a [type] architecture diagram showing:

Components:
- [List each component with brief description]

Connections:
- [Component A] connects to [Component B] via [protocol/method]
- [More connections...]

Visual requirements:
- Use [standard icons/custom shapes]
- Color-code by [category/layer/function]
- Include [labels/annotations/legends]
- Style: [professional/technical/modern]
```

#### Flowchart Template

```
Create a flowchart for [process name]:

Steps:
1. [Step description]
2. [Step with decision point]
   - If [condition]: [action]
   - Else: [alternative action]
3. [Continue...]

Requirements:
- Use standard flowchart symbols
- Include [decision diamonds/process rectangles/connectors]
- Show [error handling/alternative paths]
- Style: [professional/colorful/minimal]
```

#### Image Editing Template

```
Using the provided image of [description], [action] only the
[specific element] to [new description].

Keep everything else in the image exactly the same, preserving:
- Original style and lighting
- Other elements: [list important elements]
- Composition and layout
```

### Tips for Better Results

1. **For Text in Images**: Use Nano Banana Pro for high-fidelity text rendering
2. **For Complex Diagrams**: Break down into multiple generation steps
3. **For Consistency**: Provide style reference images
4. **For Technical Accuracy**: Include specific technical terms and standards
5. **For Iterative Refinement**: Use multi-turn chat for progressive improvements

---

## Error Handling

### Python Error Handling

```python
from google import genai
from google.genai import types
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_image_safely(prompt: str, output_path: str) -> bool:
    """Generate an image with proper error handling."""

    client = genai.Client()

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
            )
        )

        image_saved = False
        for part in response.parts:
            if part.text is not None:
                logger.info(f"Response text: {part.text}")
            elif image := part.as_image():
                image.save(output_path)
                logger.info(f"Image saved to {output_path}")
                image_saved = True

        if not image_saved:
            logger.warning("No image was generated in the response")
            return False

        return True

    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        raise

# Usage
try:
    success = generate_image_safely(
        "A beautiful sunset over mountains",
        "sunset.png"
    )
except Exception as e:
    print(f"Failed to generate image: {e}")
```

### TypeScript Error Handling

```typescript
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

interface GenerationResult {
  success: boolean;
  text?: string;
  imagePath?: string;
  error?: string;
}

async function generateImageSafely(
  prompt: string,
  outputPath: string
): Promise<GenerationResult> {
  const ai = new GoogleGenAI({});

  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash-image",
      contents: prompt,
      config: {
        responseModalities: ["TEXT", "IMAGE"],
      },
    });

    let result: GenerationResult = { success: false };

    for (const part of response.candidates[0].content.parts) {
      if (part.text) {
        result.text = part.text;
        console.log("Response text:", part.text);
      } else if (part.inlineData) {
        const buffer = Buffer.from(part.inlineData.data, "base64");
        fs.writeFileSync(outputPath, buffer);
        result.imagePath = outputPath;
        result.success = true;
        console.log(`Image saved to ${outputPath}`);
      }
    }

    if (!result.success) {
      result.error = "No image was generated in the response";
    }

    return result;
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error(`Error generating image: ${errorMessage}`);
    return {
      success: false,
      error: errorMessage,
    };
  }
}

// Usage
async function main(): Promise<void> {
  const result = await generateImageSafely(
    "A beautiful sunset over mountains",
    "sunset.png"
  );

  if (!result.success) {
    console.error(`Failed to generate image: ${result.error}`);
  }
}

main();
```

---

## Pricing and Limits

### Nano Banana (gemini-2.5-flash-image)

| Metric | Value |
|--------|-------|
| Price per image | ~$0.039 |
| Output tokens per image | 1,290 |
| Price per 1M output tokens | $30.00 |

### Nano Banana Pro (gemini-3-pro-image-preview)

| Metric | Value |
|--------|-------|
| Max reference images | 14 (6 objects + 5 humans) |
| Max resolution | 4K |
| Pricing | Check current Google AI pricing |

### Rate Limits

- Check [Google AI Studio](https://aistudio.google.com/) for current rate limits
- Enterprise users on Vertex AI may have higher limits

### Best Practices for Cost Optimization

1. **Use Nano Banana** for simple, high-volume generation tasks
2. **Use Nano Banana Pro** only when you need:
   - High-resolution output (2K/4K)
   - Complex text rendering
   - Multiple reference images
   - Advanced reasoning capabilities
3. **Cache generated images** to avoid regenerating the same content
4. **Use multi-turn editing** for iterative refinement instead of generating from scratch

---

## Additional Resources

- [Google AI Studio](https://aistudio.google.com/) - API key management and playground
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs/image-generation) - Official documentation
- [Vertex AI](https://cloud.google.com/vertex-ai) - Enterprise deployment options

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-28 | 1.0 | Initial release |

---

*This guide was created to support Claude Code skills development for visual artifact generation using the Nano Banana API.*

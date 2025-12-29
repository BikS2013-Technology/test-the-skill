/**
 * Test: TypeScript Image Editing (Inpainting)
 * From document: 111 - Nano-Banana-API-Guide.md
 * Document lines: 322-366
 */
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";
import * as path from "node:path";

const OUTPUT_DIR = "../output";
const MOCK_DIR = "../mock-images";

async function test() {
  console.log("=".repeat(60));
  console.log("Test: TypeScript Image Editing (lines 322-366)");
  console.log("=".repeat(60));

  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  const ai = new GoogleGenAI({});
  console.log("[OK] Client initialized");

  // Read and encode source image
  const imagePath = path.join(MOCK_DIR, "living_room.png");
  if (!fs.existsSync(imagePath)) {
    throw new Error(`Mock image not found: ${imagePath}`);
  }
  const imageData = fs.readFileSync(imagePath);
  const base64Image = imageData.toString("base64");
  console.log(`[OK] Loaded source image: ${imagePath}`);

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

  console.log("[...] Editing image...");
  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image",
    contents: prompt,
  });
  console.log("[OK] Response received");

  let imageSaved = false;
  const outputPath = path.join(OUTPUT_DIR, "ts_test_03_editing.png");

  for (const part of response.candidates![0].content.parts) {
    if (part.text) {
      console.log(`[INFO] Text: ${part.text.substring(0, 100)}...`);
    } else if (part.inlineData) {
      const buffer = Buffer.from(part.inlineData.data!, "base64");
      fs.writeFileSync(outputPath, buffer);
      console.log(`[OK] Saved: ${outputPath}`);
      imageSaved = true;
    }
  }

  if (!imageSaved) {
    throw new Error("No image generated");
  }

  console.log(`[OK] File size: ${fs.statSync(outputPath).size.toLocaleString()} bytes`);
  console.log("Test: PASSED");
}

test().catch((error) => {
  console.error(`[ERROR] ${error.message}`);
  process.exit(1);
});

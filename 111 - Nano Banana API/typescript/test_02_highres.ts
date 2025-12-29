/**
 * Test: TypeScript High-Resolution Image Generation
 * From document: 111 - Nano-Banana-API-Guide.md
 * Document lines: 287-318
 */
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";
import * as path from "node:path";

const OUTPUT_DIR = "../output";

async function test() {
  console.log("=".repeat(60));
  console.log("Test: TypeScript High-Resolution (lines 287-318)");
  console.log("=".repeat(60));

  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  const ai = new GoogleGenAI({});
  console.log("[OK] Client initialized");

  console.log("[...] Generating high-resolution image...");
  const response = await ai.models.generateContent({
    model: "gemini-3-pro-image-preview",
    contents: "A detailed infographic about the water cycle with labeled diagrams",
    config: {
      responseModalities: ["TEXT", "IMAGE"],
      imageConfig: {
        aspectRatio: "16:9",
        imageSize: "2K",
      },
    },
  });
  console.log("[OK] Response received");

  let imageSaved = false;
  const outputPath = path.join(OUTPUT_DIR, "ts_test_02_highres.png");

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

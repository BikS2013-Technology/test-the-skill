/**
 * Test: TypeScript Basic Text-to-Image Generation
 * From document: 111 - Nano-Banana-API-Guide.md
 * Document lines: 257-283
 */
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";
import * as path from "node:path";

const OUTPUT_DIR = "../output";

async function test() {
  console.log("=".repeat(60));
  console.log("Test: TypeScript Basic Text-to-Image (lines 257-283)");
  console.log("=".repeat(60));

  // Ensure output directory exists
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  // Initialize client (reads GEMINI_API_KEY from environment)
  const ai = new GoogleGenAI({});
  console.log("[OK] Client initialized");

  console.log("[...] Generating image...");
  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image",
    contents: "A watercolor painting of a fox in a snowy forest",
  });
  console.log("[OK] Response received");

  let imageSaved = false;
  const outputPath = path.join(OUTPUT_DIR, "ts_test_01_basic.png");

  for (const part of response.candidates![0].content.parts) {
    if (part.text) {
      console.log(`[INFO] Response text: ${part.text.substring(0, 150)}...`);
    } else if (part.inlineData) {
      const imageData = part.inlineData.data!;
      const buffer = Buffer.from(imageData, "base64");
      fs.writeFileSync(outputPath, buffer);
      console.log(`[OK] Image saved as ${outputPath}`);
      imageSaved = true;
    }
  }

  if (!imageSaved) {
    throw new Error("No image was generated in the response");
  }

  const fileSize = fs.statSync(outputPath).size;
  console.log(`[OK] Output file exists (${fileSize.toLocaleString()} bytes)`);

  console.log("\n" + "=".repeat(60));
  console.log("Test: PASSED");
  console.log("=".repeat(60));
}

test().catch((error) => {
  console.error(`\n[ERROR] Test failed: ${error.message}`);
  process.exit(1);
});

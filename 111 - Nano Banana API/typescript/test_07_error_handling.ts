/**
 * Test: TypeScript Error Handling
 * From document: 111 - Nano-Banana-API-Guide.md
 * Document lines: 1127-1196
 */
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";
import * as path from "node:path";

const OUTPUT_DIR = "../output";

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

    for (const part of response.candidates![0].content.parts) {
      if (part.text) {
        result.text = part.text;
        console.log("Response text:", part.text.substring(0, 100) + "...");
      } else if (part.inlineData) {
        const buffer = Buffer.from(part.inlineData.data!, "base64");
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

async function test() {
  console.log("=".repeat(60));
  console.log("Test: TypeScript Error Handling (lines 1127-1196)");
  console.log("=".repeat(60));

  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  const outputPath = path.join(OUTPUT_DIR, "ts_test_07_error_handling.png");

  console.log("[...] Testing generateImageSafely function...");
  const result = await generateImageSafely(
    "A beautiful sunset over mountains",
    outputPath
  );

  if (result.success) {
    console.log(`[OK] Function returned success`);
    console.log(`[OK] File size: ${fs.statSync(outputPath).size.toLocaleString()} bytes`);
    console.log("Test: PASSED");
  } else {
    console.error(`[ERROR] Failed to generate image: ${result.error}`);
    process.exit(1);
  }
}

test().catch((error) => {
  console.error(`[ERROR] ${error.message}`);
  process.exit(1);
});

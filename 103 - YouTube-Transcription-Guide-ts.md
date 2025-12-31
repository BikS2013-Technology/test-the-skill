# YouTube Video Transcription Guide (TypeScript)

This guide covers different approaches to transcribe YouTube videos using TypeScript/Node.js, from official Google APIs to lightweight scraper libraries.

## Table of Contents

1. [Overview](#overview)
2. [Approach Comparison](#approach-comparison)
3. [Method 1: youtube-caption-extractor (Recommended for Most Use Cases)](#method-1-youtube-caption-extractor)
4. [Method 2: youtube-captions-scraper](#method-2-youtube-captions-scraper)
5. [Method 3: Official YouTube Data API](#method-3-official-youtube-data-api)
6. [Utility Functions](#utility-functions)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Implementation: CLI Transcription Tool](#implementation-cli-transcription-tool)

---

## Overview

YouTube videos often have captions/subtitles available in two forms:
- **User-submitted captions**: Manually created by video owners or contributors
- **Auto-generated captions**: Automatically created by YouTube's speech recognition

There are three main approaches to extract these transcriptions:

| Approach | Auth Required | Quota Limits | Best For |
|----------|---------------|--------------|----------|
| youtube-caption-extractor | No | None | Quick access to public video captions |
| youtube-captions-scraper | No | None | Simple caption extraction |
| YouTube Data API | OAuth 2.0 | Yes (200 units/download) | Your own videos, full control |

---

## Approach Comparison

### When to Use Each Method

**Use youtube-caption-extractor when:**
- You need captions from public videos
- You want TypeScript type definitions out of the box
- You need both captions and video metadata
- You're working in serverless/edge environments

**Use youtube-captions-scraper when:**
- You only need basic caption extraction
- You want the smallest possible dependency
- You prefer a battle-tested, mature library

**Use the Official YouTube Data API when:**
- You need to access captions for your own videos
- You need to upload or modify captions
- You need guaranteed, official API access
- You're building a production application with SLA requirements

---

## Method 1: youtube-caption-extractor

This is the recommended approach for most use cases. It's lightweight, has excellent TypeScript support, and works across all JavaScript environments.

### Project Setup

```bash
# Create project directory
mkdir youtube-transcription
cd youtube-transcription

# Initialize project with uv (for any Python dependencies)
uv init

# Initialize Node.js project
npm init -y

# Install TypeScript and dependencies
npm install typescript ts-node @types/node --save-dev
npm install youtube-caption-extractor

# Initialize TypeScript config
npx tsc --init
```

### TypeScript Configuration

Update your `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### Basic Usage

Create `src/basic-extraction.ts`:

```typescript
import { getSubtitles, getVideoDetails } from 'youtube-caption-extractor';

// TypeScript interfaces (provided by the library)
interface Subtitle {
  start: string;   // Timestamp in seconds
  dur: string;     // Duration in seconds
  text: string;    // Caption content
}

interface VideoDetails {
  title: string;
  description: string;
  subtitles: Subtitle[];
}

async function extractSubtitles(videoId: string, language: string = 'en'): Promise<Subtitle[]> {
  try {
    const subtitles = await getSubtitles({
      videoID: videoId,
      lang: language
    });

    console.log(`Found ${subtitles.length} subtitle segments`);
    return subtitles;
  } catch (error) {
    console.error('Error fetching subtitles:', error);
    throw error;
  }
}

async function extractVideoDetails(videoId: string, language: string = 'en'): Promise<VideoDetails> {
  try {
    const details = await getVideoDetails({
      videoID: videoId,
      lang: language
    });

    console.log(`Video: ${details.title}`);
    console.log(`Subtitles: ${details.subtitles.length} segments`);
    return details;
  } catch (error) {
    console.error('Error fetching video details:', error);
    throw error;
  }
}

// Example usage
async function main() {
  const videoId = 'dQw4w9WgXcQ'; // Example video ID

  // Get just subtitles
  const subtitles = await extractSubtitles(videoId);

  // Get full video details with subtitles
  const details = await extractVideoDetails(videoId);

  // Print first 5 subtitle segments
  console.log('\nFirst 5 subtitle segments:');
  subtitles.slice(0, 5).forEach((sub, index) => {
    console.log(`[${sub.start}s - ${sub.dur}s]: ${sub.text}`);
  });
}

main().catch(console.error);
```

### Full Transcript Extraction

Create `src/full-transcript.ts`:

```typescript
import { getSubtitles, getVideoDetails } from 'youtube-caption-extractor';

interface Subtitle {
  start: string;
  dur: string;
  text: string;
}

interface TranscriptResult {
  videoId: string;
  title?: string;
  language: string;
  fullText: string;
  segments: Subtitle[];
  totalDuration: number;
}

/**
 * Extracts the full transcript from a YouTube video
 * @param videoId - The YouTube video ID
 * @param language - The language code (default: 'en')
 * @param includeTimestamps - Whether to include timestamps in the output
 */
async function extractFullTranscript(
  videoId: string,
  language: string = 'en',
  includeTimestamps: boolean = false
): Promise<TranscriptResult> {
  const details = await getVideoDetails({ videoID: videoId, lang: language });

  let fullText: string;

  if (includeTimestamps) {
    fullText = details.subtitles
      .map(sub => `[${formatTimestamp(parseFloat(sub.start))}] ${sub.text}`)
      .join('\n');
  } else {
    fullText = details.subtitles
      .map(sub => sub.text)
      .join(' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  const totalDuration = details.subtitles.reduce((acc, sub) => {
    return Math.max(acc, parseFloat(sub.start) + parseFloat(sub.dur));
  }, 0);

  return {
    videoId,
    title: details.title,
    language,
    fullText,
    segments: details.subtitles,
    totalDuration
  };
}

/**
 * Formats seconds into HH:MM:SS format
 */
function formatTimestamp(seconds: number): string {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hrs > 0) {
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// Example usage
async function main() {
  const videoId = 'dQw4w9WgXcQ';

  console.log('Extracting transcript without timestamps...');
  const result = await extractFullTranscript(videoId, 'en', false);

  console.log(`\nVideo: ${result.title}`);
  console.log(`Duration: ${formatTimestamp(result.totalDuration)}`);
  console.log(`Segments: ${result.segments.length}`);
  console.log(`\nFull Transcript:\n${result.fullText.substring(0, 500)}...`);

  console.log('\n\nExtracting transcript with timestamps...');
  const resultWithTimestamps = await extractFullTranscript(videoId, 'en', true);
  console.log(`\nFirst 500 characters with timestamps:\n${resultWithTimestamps.fullText.substring(0, 500)}...`);
}

main().catch(console.error);
```

### Multi-Language Support

Create `src/multi-language.ts`:

```typescript
import { getSubtitles } from 'youtube-caption-extractor';

interface Subtitle {
  start: string;
  dur: string;
  text: string;
}

interface LanguageResult {
  language: string;
  available: boolean;
  subtitles?: Subtitle[];
  error?: string;
}

/**
 * Attempts to extract subtitles in multiple languages
 * @param videoId - The YouTube video ID
 * @param languages - Array of language codes to try
 */
async function extractMultipleLanguages(
  videoId: string,
  languages: string[]
): Promise<LanguageResult[]> {
  const results: LanguageResult[] = [];

  for (const lang of languages) {
    try {
      const subtitles = await getSubtitles({ videoID: videoId, lang });
      results.push({
        language: lang,
        available: true,
        subtitles
      });
      console.log(`✓ Found subtitles in ${lang}: ${subtitles.length} segments`);
    } catch (error) {
      results.push({
        language: lang,
        available: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      console.log(`✗ No subtitles available in ${lang}`);
    }
  }

  return results;
}

// Common language codes
const COMMON_LANGUAGES = [
  'en',    // English
  'es',    // Spanish
  'fr',    // French
  'de',    // German
  'pt',    // Portuguese
  'it',    // Italian
  'ja',    // Japanese
  'ko',    // Korean
  'zh-Hans', // Chinese (Simplified)
  'zh-Hant', // Chinese (Traditional)
  'ru',    // Russian
  'ar',    // Arabic
  'hi',    // Hindi
];

async function main() {
  const videoId = 'dQw4w9WgXcQ';

  console.log(`Checking available languages for video: ${videoId}\n`);

  const results = await extractMultipleLanguages(videoId, COMMON_LANGUAGES);

  console.log('\n--- Summary ---');
  const available = results.filter(r => r.available);
  console.log(`Available languages: ${available.map(r => r.language).join(', ')}`);
}

main().catch(console.error);
```

---

## Method 2: youtube-captions-scraper

A simpler, battle-tested library for basic caption extraction.

### Setup

```bash
npm install youtube-captions-scraper
npm install @types/youtube-captions-scraper --save-dev
```

### Basic Usage

Create `src/scraper-example.ts`:

```typescript
import { getSubtitles } from 'youtube-captions-scraper';

// Type definition (from @types/youtube-captions-scraper)
interface Subtitle {
  start: number;  // Note: number type (different from youtube-caption-extractor)
  dur: number;
  text: string;
}

async function getVideoTranscript(videoId: string, language: string = 'en'): Promise<Subtitle[]> {
  try {
    const captions = await getSubtitles({
      videoID: videoId,
      lang: language
    });

    return captions;
  } catch (error) {
    console.error(`Failed to get captions: ${error}`);
    throw error;
  }
}

async function main() {
  const videoId = 'dQw4w9WgXcQ';

  const captions = await getVideoTranscript(videoId, 'en');

  console.log(`Found ${captions.length} caption segments`);

  // Convert to full text
  const fullText = captions.map(c => c.text).join(' ');
  console.log(`\nFull transcript:\n${fullText.substring(0, 500)}...`);
}

main().catch(console.error);
```

---

## Method 3: Official YouTube Data API

Use this method when you need official API access, especially for your own videos or when you need to upload/modify captions.

### Prerequisites

1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable the YouTube Data API v3**
   - Navigate to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"

3. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Desktop app" as the application type
   - Download the JSON file and save as `client_secret.json`

### Setup

```bash
npm install googleapis google-auth-library
npm install @types/node --save-dev
```

### OAuth2 Authentication Setup

Create `src/auth/oauth2-helper.ts`:

```typescript
import { google } from 'googleapis';
import { OAuth2Client, Credentials } from 'google-auth-library';
import * as fs from 'fs';
import * as path from 'path';
import * as readline from 'readline';

// Required scopes for caption operations
const SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl'];

// Path to store the OAuth token
const TOKEN_PATH = path.join(__dirname, '../../.credentials/youtube-token.json');
const CREDENTIALS_PATH = path.join(__dirname, '../../client_secret.json');

interface ClientSecrets {
  installed: {
    client_id: string;
    client_secret: string;
    redirect_uris: string[];
  };
}

/**
 * Creates an OAuth2 client with the given credentials
 */
function createOAuth2Client(credentials: ClientSecrets): OAuth2Client {
  const { client_id, client_secret, redirect_uris } = credentials.installed;
  return new google.auth.OAuth2(client_id, client_secret, redirect_uris[0]);
}

/**
 * Prompts user to authorize the application
 */
async function getNewToken(oauth2Client: OAuth2Client): Promise<Credentials> {
  const authUrl = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
  });

  console.log('Authorize this app by visiting this URL:');
  console.log(authUrl);

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise((resolve, reject) => {
    rl.question('Enter the code from that page here: ', async (code) => {
      rl.close();
      try {
        const { tokens } = await oauth2Client.getToken(code);
        oauth2Client.setCredentials(tokens);

        // Store the token for future use
        const tokenDir = path.dirname(TOKEN_PATH);
        if (!fs.existsSync(tokenDir)) {
          fs.mkdirSync(tokenDir, { recursive: true });
        }
        fs.writeFileSync(TOKEN_PATH, JSON.stringify(tokens));
        console.log('Token stored to:', TOKEN_PATH);

        resolve(tokens);
      } catch (error) {
        reject(error);
      }
    });
  });
}

/**
 * Gets an authorized OAuth2 client
 */
export async function getAuthorizedClient(): Promise<OAuth2Client> {
  // Load client secrets
  if (!fs.existsSync(CREDENTIALS_PATH)) {
    throw new Error(
      `Client secrets file not found at ${CREDENTIALS_PATH}. ` +
      'Download it from Google Cloud Console.'
    );
  }

  const credentials: ClientSecrets = JSON.parse(
    fs.readFileSync(CREDENTIALS_PATH, 'utf-8')
  );

  const oauth2Client = createOAuth2Client(credentials);

  // Check if we have a stored token
  if (fs.existsSync(TOKEN_PATH)) {
    const token: Credentials = JSON.parse(fs.readFileSync(TOKEN_PATH, 'utf-8'));
    oauth2Client.setCredentials(token);
    return oauth2Client;
  }

  // Get new token
  await getNewToken(oauth2Client);
  return oauth2Client;
}
```

### List Captions

Create `src/api/list-captions.ts`:

```typescript
import { google, youtube_v3 } from 'googleapis';
import { getAuthorizedClient } from '../auth/oauth2-helper';

interface CaptionTrack {
  id: string;
  language: string;
  name: string;
  trackKind: string;
  isAutoSynced: boolean;
  isDraft: boolean;
  status: string;
}

/**
 * Lists all caption tracks for a video
 * @param videoId - The YouTube video ID
 */
export async function listCaptions(videoId: string): Promise<CaptionTrack[]> {
  const auth = await getAuthorizedClient();
  const youtube = google.youtube({ version: 'v3', auth });

  try {
    const response = await youtube.captions.list({
      part: ['id', 'snippet'],
      videoId: videoId,
    });

    const tracks: CaptionTrack[] = (response.data.items || []).map(item => ({
      id: item.id || '',
      language: item.snippet?.language || '',
      name: item.snippet?.name || '',
      trackKind: item.snippet?.trackKind || '',
      isAutoSynced: item.snippet?.isAutoSynced || false,
      isDraft: item.snippet?.isDraft || false,
      status: item.snippet?.status || '',
    }));

    return tracks;
  } catch (error) {
    if (error instanceof Error) {
      console.error('Error listing captions:', error.message);
    }
    throw error;
  }
}

// Example usage
async function main() {
  const videoId = 'YOUR_VIDEO_ID'; // Replace with your video ID

  console.log(`Listing captions for video: ${videoId}`);

  const tracks = await listCaptions(videoId);

  console.log(`\nFound ${tracks.length} caption tracks:`);
  tracks.forEach((track, index) => {
    console.log(`\n${index + 1}. ${track.language} (${track.name || 'unnamed'})`);
    console.log(`   ID: ${track.id}`);
    console.log(`   Type: ${track.trackKind}`);
    console.log(`   Auto-synced: ${track.isAutoSynced}`);
    console.log(`   Status: ${track.status}`);
  });
}

main().catch(console.error);
```

### Download Captions

Create `src/api/download-captions.ts`:

```typescript
import { google } from 'googleapis';
import { getAuthorizedClient } from '../auth/oauth2-helper';
import * as fs from 'fs';

// Supported caption formats
type CaptionFormat = 'sbv' | 'scc' | 'srt' | 'ttml' | 'vtt';

interface DownloadOptions {
  captionId: string;
  format?: CaptionFormat;
  translateTo?: string;  // ISO 639-1 language code
  outputPath?: string;
}

/**
 * Downloads a caption track
 * Note: This requires the authenticated user to have edit access to the video
 *
 * @param options - Download configuration
 */
export async function downloadCaption(options: DownloadOptions): Promise<string> {
  const { captionId, format, translateTo, outputPath } = options;

  const auth = await getAuthorizedClient();
  const youtube = google.youtube({ version: 'v3', auth });

  try {
    const response = await youtube.captions.download({
      id: captionId,
      tfmt: format,
      tlang: translateTo,
    }, {
      responseType: 'text'
    });

    const captionContent = response.data as string;

    if (outputPath) {
      fs.writeFileSync(outputPath, captionContent);
      console.log(`Caption saved to: ${outputPath}`);
    }

    return captionContent;
  } catch (error) {
    if (error instanceof Error) {
      console.error('Error downloading caption:', error.message);
    }
    throw error;
  }
}

// Example usage
async function main() {
  // First, list captions to get the caption ID
  const captionId = 'YOUR_CAPTION_ID'; // Get this from listCaptions()

  // Download as SRT format
  const caption = await downloadCaption({
    captionId,
    format: 'srt',
    outputPath: './output/captions.srt'
  });

  console.log('Caption content preview:');
  console.log(caption.substring(0, 500));
}

main().catch(console.error);
```

### Upload Captions

Create `src/api/upload-captions.ts`:

```typescript
import { google } from 'googleapis';
import { getAuthorizedClient } from '../auth/oauth2-helper';
import * as fs from 'fs';
import * as path from 'path';

interface UploadOptions {
  videoId: string;
  language: string;
  name?: string;
  isDraft?: boolean;
  captionFilePath: string;
}

/**
 * Uploads a new caption track to a video
 * Note: The sync parameter was deprecated on March 13, 2024
 *
 * @param options - Upload configuration
 */
export async function uploadCaption(options: UploadOptions): Promise<string> {
  const { videoId, language, name, isDraft, captionFilePath } = options;

  const auth = await getAuthorizedClient();
  const youtube = google.youtube({ version: 'v3', auth });

  // Read the caption file
  const captionContent = fs.readFileSync(captionFilePath);

  try {
    const response = await youtube.captions.insert({
      part: ['snippet'],
      requestBody: {
        snippet: {
          videoId,
          language,
          name: name || '',
          isDraft: isDraft || false,
        },
      },
      media: {
        mimeType: 'application/octet-stream',
        body: captionContent,
      },
    });

    const captionId = response.data.id || '';
    console.log(`Caption uploaded successfully. ID: ${captionId}`);

    return captionId;
  } catch (error) {
    if (error instanceof Error) {
      console.error('Error uploading caption:', error.message);
    }
    throw error;
  }
}

// Example usage
async function main() {
  const result = await uploadCaption({
    videoId: 'YOUR_VIDEO_ID',
    language: 'en',
    name: 'English Subtitles',
    isDraft: false,
    captionFilePath: './captions/my-captions.srt'
  });

  console.log(`Uploaded caption ID: ${result}`);
}

main().catch(console.error);
```

---

## Utility Functions

### Extract Video ID from URL

Create `src/utils/video-id.ts`:

```typescript
/**
 * Extracts YouTube video ID from various URL formats
 *
 * Supported formats:
 * - https://www.youtube.com/watch?v=VIDEO_ID
 * - https://youtu.be/VIDEO_ID
 * - https://www.youtube.com/embed/VIDEO_ID
 * - https://www.youtube.com/v/VIDEO_ID
 * - https://www.youtube.com/shorts/VIDEO_ID
 */
export function extractVideoId(urlOrId: string): string | null {
  // If it's already just an ID (11 characters, alphanumeric with - and _)
  if (/^[a-zA-Z0-9_-]{11}$/.test(urlOrId)) {
    return urlOrId;
  }

  // Regex pattern that handles multiple YouTube URL formats
  const patterns = [
    // Standard watch URL
    /(?:youtube\.com\/watch\?v=|youtube\.com\/watch\?.+&v=)([a-zA-Z0-9_-]{11})/,
    // Short URL
    /youtu\.be\/([a-zA-Z0-9_-]{11})/,
    // Embed URL
    /youtube\.com\/embed\/([a-zA-Z0-9_-]{11})/,
    // Old embed format
    /youtube\.com\/v\/([a-zA-Z0-9_-]{11})/,
    // Shorts URL
    /youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})/,
  ];

  for (const pattern of patterns) {
    const match = urlOrId.match(pattern);
    if (match && match[1]) {
      return match[1];
    }
  }

  return null;
}

/**
 * Validates that a string is a valid YouTube video ID
 */
export function isValidVideoId(id: string): boolean {
  return /^[a-zA-Z0-9_-]{11}$/.test(id);
}

// Example usage
function main() {
  const testUrls = [
    'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    'https://youtu.be/dQw4w9WgXcQ',
    'https://www.youtube.com/embed/dQw4w9WgXcQ',
    'https://www.youtube.com/shorts/dQw4w9WgXcQ',
    'dQw4w9WgXcQ',
    'invalid-url',
  ];

  testUrls.forEach(url => {
    const id = extractVideoId(url);
    console.log(`${url} => ${id || 'NOT FOUND'}`);
  });
}

main();
```

### Save Transcript to File

Create `src/utils/save-transcript.ts`:

```typescript
import * as fs from 'fs';
import * as path from 'path';

interface Subtitle {
  start: string;
  dur: string;
  text: string;
}

interface SaveOptions {
  format: 'txt' | 'srt' | 'vtt' | 'json';
  includeTimestamps?: boolean;
}

/**
 * Saves subtitles to a file in the specified format
 */
export function saveTranscript(
  subtitles: Subtitle[],
  outputPath: string,
  options: SaveOptions = { format: 'txt' }
): void {
  const { format, includeTimestamps } = options;

  let content: string;

  switch (format) {
    case 'txt':
      content = formatAsText(subtitles, includeTimestamps || false);
      break;
    case 'srt':
      content = formatAsSrt(subtitles);
      break;
    case 'vtt':
      content = formatAsVtt(subtitles);
      break;
    case 'json':
      content = JSON.stringify(subtitles, null, 2);
      break;
    default:
      throw new Error(`Unsupported format: ${format}`);
  }

  // Ensure directory exists
  const dir = path.dirname(outputPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  fs.writeFileSync(outputPath, content, 'utf-8');
  console.log(`Transcript saved to: ${outputPath}`);
}

function formatAsText(subtitles: Subtitle[], includeTimestamps: boolean): string {
  if (includeTimestamps) {
    return subtitles
      .map(sub => `[${formatTime(parseFloat(sub.start))}] ${sub.text}`)
      .join('\n');
  }
  return subtitles.map(sub => sub.text).join(' ').replace(/\s+/g, ' ').trim();
}

function formatAsSrt(subtitles: Subtitle[]): string {
  return subtitles.map((sub, index) => {
    const start = parseFloat(sub.start);
    const end = start + parseFloat(sub.dur);
    return `${index + 1}\n${formatSrtTime(start)} --> ${formatSrtTime(end)}\n${sub.text}\n`;
  }).join('\n');
}

function formatAsVtt(subtitles: Subtitle[]): string {
  const header = 'WEBVTT\n\n';
  const body = subtitles.map(sub => {
    const start = parseFloat(sub.start);
    const end = start + parseFloat(sub.dur);
    return `${formatVttTime(start)} --> ${formatVttTime(end)}\n${sub.text}\n`;
  }).join('\n');
  return header + body;
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function formatSrtTime(seconds: number): string {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  const ms = Math.floor((seconds % 1) * 1000);
  return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')},${ms.toString().padStart(3, '0')}`;
}

function formatVttTime(seconds: number): string {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  const ms = Math.floor((seconds % 1) * 1000);
  return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}.${ms.toString().padStart(3, '0')}`;
}
```

### Complete CLI Application

Create `src/cli.ts`:

```typescript
import { getSubtitles, getVideoDetails } from 'youtube-caption-extractor';
import { extractVideoId } from './utils/video-id';
import { saveTranscript } from './utils/save-transcript';
import * as path from 'path';

interface CLIOptions {
  url: string;
  language: string;
  format: 'txt' | 'srt' | 'vtt' | 'json';
  output?: string;
  timestamps: boolean;
}

async function main() {
  // Parse command line arguments
  const args = process.argv.slice(2);

  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    printHelp();
    process.exit(0);
  }

  const options: CLIOptions = {
    url: args[0],
    language: getArgValue(args, '--lang', '-l') || 'en',
    format: (getArgValue(args, '--format', '-f') || 'txt') as CLIOptions['format'],
    output: getArgValue(args, '--output', '-o'),
    timestamps: args.includes('--timestamps') || args.includes('-t'),
  };

  // Extract video ID
  const videoId = extractVideoId(options.url);
  if (!videoId) {
    console.error('Error: Invalid YouTube URL or video ID');
    process.exit(1);
  }

  console.log(`Extracting transcript for video: ${videoId}`);
  console.log(`Language: ${options.language}`);

  try {
    // Get video details with subtitles
    const details = await getVideoDetails({ videoID: videoId, lang: options.language });

    console.log(`Video: ${details.title}`);
    console.log(`Found ${details.subtitles.length} subtitle segments`);

    // Determine output path
    const outputPath = options.output ||
      path.join(process.cwd(), `transcript-${videoId}.${options.format}`);

    // Save transcript
    saveTranscript(details.subtitles, outputPath, {
      format: options.format,
      includeTimestamps: options.timestamps,
    });

    console.log('Done!');
  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : error);
    process.exit(1);
  }
}

function getArgValue(args: string[], longFlag: string, shortFlag: string): string | undefined {
  const longIndex = args.indexOf(longFlag);
  const shortIndex = args.indexOf(shortFlag);
  const index = longIndex !== -1 ? longIndex : shortIndex;

  if (index !== -1 && index + 1 < args.length) {
    return args[index + 1];
  }
  return undefined;
}

function printHelp() {
  console.log(`
YouTube Transcript Extractor

Usage: npx ts-node src/cli.ts <video-url-or-id> [options]

Options:
  -l, --lang <code>      Language code (default: en)
  -f, --format <type>    Output format: txt, srt, vtt, json (default: txt)
  -o, --output <path>    Output file path
  -t, --timestamps       Include timestamps in text output
  -h, --help             Show this help message

Examples:
  npx ts-node src/cli.ts https://www.youtube.com/watch?v=dQw4w9WgXcQ
  npx ts-node src/cli.ts dQw4w9WgXcQ --lang es --format srt
  npx ts-node src/cli.ts dQw4w9WgXcQ -f vtt -o ./output/transcript.vtt
  `);
}

main().catch(console.error);
```

---

## Best Practices

### 1. Error Handling

Always wrap API calls in try-catch blocks and provide meaningful error messages:

```typescript
async function safeExtractSubtitles(videoId: string, language: string = 'en') {
  try {
    const subtitles = await getSubtitles({ videoID: videoId, lang: language });
    return { success: true, data: subtitles };
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';

    // Check for common errors
    if (message.includes('Could not find')) {
      return {
        success: false,
        error: `No ${language} captions available for this video`
      };
    }

    return { success: false, error: message };
  }
}
```

### 2. Rate Limiting

When processing multiple videos, implement rate limiting:

```typescript
async function processVideosWithDelay(
  videoIds: string[],
  delayMs: number = 1000
): Promise<void> {
  for (const videoId of videoIds) {
    await extractSubtitles(videoId);
    await new Promise(resolve => setTimeout(resolve, delayMs));
  }
}
```

### 3. Caching

Cache results to avoid redundant API calls:

```typescript
import * as fs from 'fs';
import * as path from 'path';

const CACHE_DIR = './.cache/transcripts';

async function getCachedOrFetch(videoId: string, language: string) {
  const cachePath = path.join(CACHE_DIR, `${videoId}-${language}.json`);

  // Check cache
  if (fs.existsSync(cachePath)) {
    const cached = JSON.parse(fs.readFileSync(cachePath, 'utf-8'));
    const cacheAge = Date.now() - cached.timestamp;

    // Cache valid for 24 hours
    if (cacheAge < 24 * 60 * 60 * 1000) {
      console.log('Using cached transcript');
      return cached.data;
    }
  }

  // Fetch fresh data
  const subtitles = await getSubtitles({ videoID: videoId, lang: language });

  // Save to cache
  if (!fs.existsSync(CACHE_DIR)) {
    fs.mkdirSync(CACHE_DIR, { recursive: true });
  }

  fs.writeFileSync(cachePath, JSON.stringify({
    timestamp: Date.now(),
    data: subtitles
  }));

  return subtitles;
}
```

### 4. Quota Management (Official API)

The YouTube Data API has quota limits. Track your usage:

| Operation | Quota Cost |
|-----------|------------|
| captions.list | 50 units |
| captions.download | 200 units |
| captions.insert | 400 units |
| captions.update | 450 units |
| captions.delete | 50 units |

Default daily quota: 10,000 units

---

## Troubleshooting

### Common Issues

**1. "Could not find captions" Error**

This occurs when:
- The video doesn't have captions in the requested language
- The video has disabled captions
- The video is private or age-restricted

Solution: Try different language codes or check if captions exist manually.

**2. "403 Forbidden" with Official API**

Causes:
- Invalid or expired OAuth token
- Insufficient permissions
- Trying to download captions for videos you don't own

Solution: Re-authenticate and ensure you have edit access to the video.

**3. Empty or Partial Subtitles**

Some videos have auto-generated captions that may be:
- Only available in certain languages
- Low quality or incomplete

Solution: Check for manually uploaded captions by looking for `trackKind: 'standard'` vs `trackKind: 'ASR'` (auto-generated).

**4. TypeScript Compilation Errors**

Ensure your `tsconfig.json` has:
```json
{
  "compilerOptions": {
    "esModuleInterop": true,
    "moduleResolution": "node"
  }
}
```

---

## Implementation: CLI Transcription Tool

A complete CLI implementation based on this guide is available in the `103 - YouTube Transcription` folder. This tool uses the `youtube-caption-extractor` library to extract transcripts from YouTube videos.

### Project Structure

```
103 - YouTube Transcription/
├── package.json
├── tsconfig.json
├── src/
│   ├── cli.ts                    # Main CLI application
│   └── utils/
│       ├── video-id.ts           # Video ID extraction utility
│       └── save-transcript.ts    # Transcript formatting and saving
└── output/                       # Generated transcripts
```

### Installation

```bash
cd "103 - YouTube Transcription"
npm install
```

### Usage Examples

**Basic usage (outputs to txt file with timestamps):**
```bash
npx ts-node src/cli.ts "https://youtu.be/0hgyHOLIFxw" -t -o ./output/transcript.txt
```

**Export as SRT format:**
```bash
npx ts-node src/cli.ts "https://youtu.be/0hgyHOLIFxw" -f srt -o ./output/transcript.srt
```

**Export as JSON format:**
```bash
npx ts-node src/cli.ts "https://youtu.be/0hgyHOLIFxw" -f json -o ./output/transcript.json
```

**Show help:**
```bash
npx ts-node src/cli.ts --help
```

### CLI Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--lang` | `-l` | Language code for captions | `en` |
| `--format` | `-f` | Output format: txt, srt, vtt, json | `txt` |
| `--output` | `-o` | Output file path | `./transcript-{videoId}.{format}` |
| `--timestamps` | `-t` | Include timestamps in txt output | false |
| `--help` | `-h` | Show help message | - |

### Sample Output

**Text with timestamps:**
```
[00:00] Sub agents are one of the most powerful
[00:02] capabilities inside of Claw Code. And
[00:05] while a lot of people, a lot of creators
[00:07] talk about them or cover them, nobody is
[00:09] showing you how to build sub agents for
[00:12] writing operations or content creation
...
```

**SRT format:**
```
1
00:00:00,000 --> 00:00:02,480
Sub agents are one of the most powerful

2
00:00:02,480 --> 00:00:05,040
capabilities inside of Claw Code. And
...
```

### Supported URL Formats

The tool accepts various YouTube URL formats:
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://youtu.be/VIDEO_ID?si=SHARE_PARAM`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`
- Direct video ID (11 characters)

---

## References

- [YouTube Data API - Captions Overview](https://developers.google.com/youtube/v3/docs/captions)
- [YouTube Data API - Captions Download](https://developers.google.com/youtube/v3/docs/captions/download)
- [YouTube Data API - Captions List](https://developers.google.com/youtube/v3/docs/captions/list)
- [YouTube Data API - Node.js Quickstart](https://developers.google.com/youtube/v3/quickstart/nodejs)
- [OAuth 2.0 for Server-Side Web Apps](https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps)
- [googleapis npm package](https://www.npmjs.com/package/@googleapis/youtube)
- [youtube-caption-extractor GitHub](https://github.com/devhims/youtube-caption-extractor)
- [youtube-captions-scraper GitHub](https://github.com/algolia/youtube-captions-scraper)

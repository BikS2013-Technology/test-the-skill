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

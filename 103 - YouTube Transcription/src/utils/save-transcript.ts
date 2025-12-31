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

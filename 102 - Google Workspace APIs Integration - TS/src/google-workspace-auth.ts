/**
 * Google Workspace APIs Authentication Module for TypeScript.
 *
 * This is the implementation from document lines 2748-2903
 * FIXED:
 * 1. Type compatibility issues - the document's approach using Auth.OAuth2Client
 *    directly doesn't work due to type conflicts between @google-cloud/local-auth
 *    and googleapis. This version uses a more practical approach.
 * 2. Token format - the document assumes a specific token format that doesn't
 *    match what @google-cloud/local-auth actually produces.
 */
import * as fs from 'fs/promises';
import * as path from 'path';
import { authenticate } from '@google-cloud/local-auth';
import { google, drive_v3, docs_v1, sheets_v4, slides_v1 } from 'googleapis';

// Comprehensive scopes for full access
export const SCOPES = [
  'https://www.googleapis.com/auth/drive',
  'https://www.googleapis.com/auth/documents',
  'https://www.googleapis.com/auth/spreadsheets',
  'https://www.googleapis.com/auth/presentations',
];

// Default paths - can be overridden
const DEFAULT_TOKEN_PATH = path.join(process.cwd(), 'token.json');
const DEFAULT_CREDENTIALS_PATH = path.join(process.cwd(), 'credentials.json');

// Document's expected format for saved credentials
interface SavedCredentials {
  type: string;
  client_id: string;
  client_secret: string;
  refresh_token: string;
}

// Actual format produced by @google-cloud/local-auth
interface ActualTokenFormat {
  token?: string;
  refresh_token: string;
  token_uri?: string;
  client_id: string;
  client_secret: string;
  scopes?: string[];
  universe_domain?: string;
  account?: string;
  expiry?: string;
  type?: string;
}

/**
 * Load saved credentials if they exist.
 * FIXED: Handle both the document's expected format and the actual format
 * produced by @google-cloud/local-auth.
 */
async function loadSavedCredentials(tokenPath: string): Promise<ReturnType<typeof google.auth.fromJSON> | null> {
  try {
    const content = await fs.readFile(tokenPath, 'utf-8');
    const rawCredentials: ActualTokenFormat = JSON.parse(content);

    // Convert to the format expected by google.auth.fromJSON
    const credentials: SavedCredentials = {
      type: rawCredentials.type || 'authorized_user',
      client_id: rawCredentials.client_id,
      client_secret: rawCredentials.client_secret,
      refresh_token: rawCredentials.refresh_token,
    };

    return google.auth.fromJSON(credentials);
  } catch {
    return null;
  }
}

/**
 * Save credentials to file.
 */
async function saveCredentials(
  client: Awaited<ReturnType<typeof authenticate>>,
  credentialsPath: string,
  tokenPath: string
): Promise<void> {
  const content = await fs.readFile(credentialsPath, 'utf-8');
  const keys = JSON.parse(content);
  const key = keys.installed || keys.web;
  const payload: SavedCredentials = {
    type: 'authorized_user',
    client_id: key.client_id,
    client_secret: key.client_secret,
    refresh_token: client.credentials.refresh_token!,
  };
  await fs.writeFile(tokenPath, JSON.stringify(payload));
}

// Use a union type that accepts all possible auth client types
type GoogleAuthClient = Awaited<ReturnType<typeof authenticate>> | ReturnType<typeof google.auth.fromJSON>;

/**
 * Get or refresh OAuth credentials.
 *
 * @param credentialsPath - Path to OAuth credentials JSON
 * @param tokenPath - Path to store/retrieve access tokens
 * @param scopes - List of OAuth scopes (defaults to SCOPES)
 * @returns Authenticated credentials object
 */
export async function getCredentials(
  credentialsPath: string = DEFAULT_CREDENTIALS_PATH,
  tokenPath: string = DEFAULT_TOKEN_PATH,
  scopes: string[] = SCOPES
): Promise<GoogleAuthClient> {
  // Try to load saved credentials first
  const savedClient = await loadSavedCredentials(tokenPath);
  if (savedClient) {
    return savedClient;
  }

  // No saved credentials, authenticate
  const client = await authenticate({
    scopes,
    keyfilePath: credentialsPath,
  });

  if (client.credentials) {
    await saveCredentials(client, credentialsPath, tokenPath);
  }

  return client;
}

/**
 * Get Google Drive API service instance.
 */
export async function getDriveService(
  credentialsPath: string = DEFAULT_CREDENTIALS_PATH,
  tokenPath: string = DEFAULT_TOKEN_PATH
): Promise<drive_v3.Drive> {
  const auth = await getCredentials(credentialsPath, tokenPath);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return google.drive({ version: 'v3', auth: auth as any });
}

/**
 * Get Google Docs API service instance.
 */
export async function getDocsService(
  credentialsPath: string = DEFAULT_CREDENTIALS_PATH,
  tokenPath: string = DEFAULT_TOKEN_PATH
): Promise<docs_v1.Docs> {
  const auth = await getCredentials(credentialsPath, tokenPath);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return google.docs({ version: 'v1', auth: auth as any });
}

/**
 * Get Google Sheets API service instance.
 */
export async function getSheetsService(
  credentialsPath: string = DEFAULT_CREDENTIALS_PATH,
  tokenPath: string = DEFAULT_TOKEN_PATH
): Promise<sheets_v4.Sheets> {
  const auth = await getCredentials(credentialsPath, tokenPath);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return google.sheets({ version: 'v4', auth: auth as any });
}

/**
 * Get Google Slides API service instance.
 */
export async function getSlidesService(
  credentialsPath: string = DEFAULT_CREDENTIALS_PATH,
  tokenPath: string = DEFAULT_TOKEN_PATH
): Promise<slides_v1.Slides> {
  const auth = await getCredentials(credentialsPath, tokenPath);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return google.slides({ version: 'v1', auth: auth as any });
}

export interface AllServices {
  drive: drive_v3.Drive;
  docs: docs_v1.Docs;
  sheets: sheets_v4.Sheets;
  slides: slides_v1.Slides;
}

/**
 * Get all Google Workspace API service instances.
 *
 * @returns Object with 'drive', 'docs', 'sheets', 'slides' services
 */
export async function getAllServices(
  credentialsPath: string = DEFAULT_CREDENTIALS_PATH,
  tokenPath: string = DEFAULT_TOKEN_PATH
): Promise<AllServices> {
  const auth = await getCredentials(credentialsPath, tokenPath);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const authClient = auth as any;

  return {
    drive: google.drive({ version: 'v3', auth: authClient }),
    docs: google.docs({ version: 'v1', auth: authClient }),
    sheets: google.sheets({ version: 'v4', auth: authClient }),
    slides: google.slides({ version: 'v1', auth: authClient }),
  };
}

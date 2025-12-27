/**
 * Gmail API Authentication Module for Node.js
 *
 * Test script for: Gmail API Authentication (Node.js)
 * From document: Gmail-API-Integration-Guide.md
 * Document lines: 1727-1811
 */
const fs = require('fs').promises;
const path = require('path');
const { authenticate } = require('@google-cloud/local-auth');
const { google } = require('googleapis');

// Define your scopes - IMPORTANT: Only request scopes configured
// in your OAuth Consent Screen's Data Access section
const SCOPES = [
  'https://www.googleapis.com/auth/gmail.readonly',
];

const TOKEN_PATH = path.join(__dirname, '..', 'gmail_token_nodejs.json');
const CREDENTIALS_PATH = path.join(__dirname, '..', 'GMailSkill-Credentials.json');

/**
 * Reads previously authorized credentials from the save file.
 * @returns {Promise<OAuth2Client|null>}
 */
async function loadSavedCredentialsIfExist() {
  try {
    const content = await fs.readFile(TOKEN_PATH);
    const credentials = JSON.parse(content);
    return google.auth.fromJSON(credentials);
  } catch (err) {
    return null;
  }
}

/**
 * Serializes credentials to a file.
 * @param {OAuth2Client} client
 */
async function saveCredentials(client) {
  const content = await fs.readFile(CREDENTIALS_PATH);
  const keys = JSON.parse(content);
  const key = keys.installed || keys.web;
  const payload = JSON.stringify({
    type: 'authorized_user',
    client_id: key.client_id,
    client_secret: key.client_secret,
    refresh_token: client.credentials.refresh_token,
  });
  await fs.writeFile(TOKEN_PATH, payload);
}

/**
 * Load or request authorization to call APIs.
 * @returns {Promise<OAuth2Client>}
 */
async function authorize() {
  let client = await loadSavedCredentialsIfExist();
  if (client) {
    return client;
  }
  client = await authenticate({
    scopes: SCOPES,
    keyfilePath: CREDENTIALS_PATH,
  });
  if (client.credentials) {
    await saveCredentials(client);
  }
  return client;
}

/**
 * Get Gmail API service instance.
 * @returns {Promise<gmail_v1.Gmail>}
 */
async function getGmailService() {
  const auth = await authorize();
  return google.gmail({ version: 'v1', auth });
}

module.exports = {
  authorize,
  getGmailService,
  SCOPES,
};

// Test execution
if (require.main === module) {
  (async () => {
    console.log('='.repeat(60));
    console.log('Test: Gmail API Authentication Module (Node.js)');
    console.log('='.repeat(60));

    try {
      // Check credentials file exists
      try {
        await fs.access(CREDENTIALS_PATH);
        console.log(`[OK] Credentials file found: ${CREDENTIALS_PATH}`);
      } catch {
        console.log(`[ERROR] Credentials file not found: ${CREDENTIALS_PATH}`);
        process.exit(1);
      }

      console.log('\nAttempting Gmail API authentication...');
      console.log('(This may open a browser window for first-time authentication)');

      const gmail = await getGmailService();

      // Verify by getting profile
      const profile = await gmail.users.getProfile({ userId: 'me' });

      console.log('\n[OK] Authentication successful!');
      console.log(`Email: ${profile.data.emailAddress}`);
      console.log(`Messages Total: ${profile.data.messagesTotal}`);
      console.log(`Threads Total: ${profile.data.threadsTotal}`);

      console.log('\n' + '='.repeat(60));
      console.log('Test: PASSED');
      console.log('='.repeat(60));
    } catch (error) {
      console.log(`\n[ERROR] Authentication failed: ${error.message}`);
      console.error(error);
      process.exit(1);
    }
  })();
}

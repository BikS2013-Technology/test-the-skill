/**
 * Gmail API - Read Messages and Threads Module for Node.js
 *
 * Test script for: Gmail API Read Messages (Node.js)
 * From document: Gmail-API-Integration-Guide.md
 * Document lines: 1934-2088
 */
const { getGmailService } = require('./gmail-auth');

/**
 * Get a specific message by ID.
 * @param {string} messageId - Message ID
 * @param {string} format - 'full', 'metadata', 'minimal', or 'raw'
 * @returns {Promise<Object>} Message object
 */
async function getMessage(messageId, format = 'full') {
  const gmail = await getGmailService();

  try {
    const response = await gmail.users.messages.get({
      userId: 'me',
      id: messageId,
      format,
    });
    return response.data;
  } catch (error) {
    console.error('Error getting message:', error.message);
    throw error;
  }
}

/**
 * Extract body content from a message.
 * @param {Object} message - Full message object
 * @returns {Object} Object with 'plain' and 'html' body content
 */
function getMessageBody(message) {
  const body = { plain: '', html: '' };

  function extractParts(payload) {
    if (payload.body && payload.body.data) {
      const data = Buffer.from(payload.body.data, 'base64').toString('utf-8');
      const mimeType = payload.mimeType || '';

      if (mimeType.includes('text/plain')) {
        body.plain = data;
      } else if (mimeType.includes('text/html')) {
        body.html = data;
      }
    }

    if (payload.parts) {
      payload.parts.forEach((part) => extractParts(part));
    }
  }

  if (message.payload) {
    extractParts(message.payload);
  }

  return body;
}

/**
 * Extract headers from a message.
 * @param {Object} message - Message object
 * @returns {Object} Headers as key-value pairs
 */
function getMessageHeaders(message) {
  const headers = {};
  if (message.payload && message.payload.headers) {
    message.payload.headers.forEach((h) => {
      headers[h.name] = h.value;
    });
  }
  return headers;
}

/**
 * Get a complete thread by ID.
 * @param {string} threadId - Thread ID
 * @param {string} format - 'full', 'metadata', or 'minimal'
 * @returns {Promise<Object>} Thread object with all messages
 */
async function getThread(threadId, format = 'full') {
  const gmail = await getGmailService();

  try {
    const response = await gmail.users.threads.get({
      userId: 'me',
      id: threadId,
      format,
    });
    return response.data;
  } catch (error) {
    console.error('Error getting thread:', error.message);
    throw error;
  }
}

/**
 * Get all messages in a thread with parsed content.
 * @param {string} threadId - Thread ID
 * @returns {Promise<Array>} Array of parsed message objects
 */
async function getThreadMessages(threadId) {
  const thread = await getThread(threadId, 'full');
  const parsedMessages = [];

  for (const message of thread.messages || []) {
    const headers = getMessageHeaders(message);
    const body = getMessageBody(message);

    parsedMessages.push({
      id: message.id,
      threadId: message.threadId,
      subject: headers.Subject || '',
      from: headers.From || '',
      to: headers.To || '',
      date: headers.Date || '',
      bodyPlain: body.plain,
      bodyHtml: body.html,
      snippet: message.snippet || '',
      labelIds: message.labelIds || [],
    });
  }

  return parsedMessages;
}

module.exports = {
  getMessage,
  getMessageBody,
  getMessageHeaders,
  getThread,
  getThreadMessages,
};

// Test execution
if (require.main === module) {
  const { listMessages } = require('./gmail-list');

  (async () => {
    console.log('='.repeat(60));
    console.log('Test: Gmail API Read Messages Module (Node.js)');
    console.log('='.repeat(60));

    try {
      // Get a message to test with
      console.log('\n[Setup] Getting a message to read...');
      const messages = await listMessages({ maxResults: 1 });
      if (messages.length === 0) {
        console.log('[ERROR] No messages found in mailbox');
        process.exit(1);
      }

      const msgId = messages[0].id;
      const threadId = messages[0].threadId;
      console.log(`[OK] Using message ID: ${msgId}`);
      console.log(`     Thread ID: ${threadId}`);

      // Test 1: Get message
      console.log('\n[Test 1] Getting full message...');
      const message = await getMessage(msgId);
      console.log('[OK] Retrieved message');
      console.log(`     Snippet: ${message.snippet.substring(0, 80)}...`);

      // Test 2: Extract headers
      console.log('\n[Test 2] Extracting headers...');
      const headers = getMessageHeaders(message);
      console.log('[OK] Headers extracted');
      console.log(`     Subject: ${(headers.Subject || '(none)').substring(0, 50)}`);
      console.log(`     From: ${(headers.From || '(none)').substring(0, 50)}`);
      console.log(`     Date: ${headers.Date || '(none)'}`);

      // Test 3: Extract body
      console.log('\n[Test 3] Extracting message body...');
      const body = getMessageBody(message);
      console.log('[OK] Body extracted');
      console.log(`     Plain text length: ${body.plain.length} chars`);
      console.log(`     HTML length: ${body.html.length} chars`);
      if (body.plain) {
        console.log(`     Preview: ${body.plain.substring(0, 100)}...`);
      }

      // Test 4: Get thread
      console.log('\n[Test 4] Getting thread...');
      const thread = await getThread(threadId);
      const msgCount = (thread.messages || []).length;
      console.log('[OK] Thread retrieved');
      console.log(`     Messages in thread: ${msgCount}`);

      // Test 5: Get thread messages with details
      console.log('\n[Test 5] Getting thread messages with parsed content...');
      const threadMessages = await getThreadMessages(threadId);
      console.log(`[OK] Retrieved ${threadMessages.length} messages`);

      for (let i = 0; i < threadMessages.length; i++) {
        const msg = threadMessages[i];
        console.log(`\n  [Message ${i + 1}]`);
        console.log(`    Subject: ${(msg.subject || '(none)').substring(0, 40)}...`);
        console.log(`    From: ${(msg.from || '(none)').substring(0, 40)}...`);
        console.log(`    Has plain text: ${msg.bodyPlain ? 'Yes' : 'No'}`);
        console.log(`    Has HTML: ${msg.bodyHtml ? 'Yes' : 'No'}`);
      }

      console.log('\n' + '='.repeat(60));
      console.log('Test: PASSED');
      console.log('='.repeat(60));
    } catch (error) {
      console.log(`\n[ERROR] Test failed: ${error.message}`);
      console.error(error);
      process.exit(1);
    }
  })();
}

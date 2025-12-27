/**
 * Gmail API - List Messages Module for Node.js
 *
 * Test script for: Gmail API List Messages (Node.js)
 * From document: Gmail-API-Integration-Guide.md
 * Document lines: 1817-1927
 */
const { getGmailService } = require('./gmail-auth');

/**
 * List messages matching the specified criteria.
 * @param {Object} options - Search options
 * @param {string} options.query - Gmail search query
 * @param {string[]} options.labelIds - Label IDs to filter by
 * @param {number} options.maxResults - Maximum messages to return
 * @param {boolean} options.includeSpamTrash - Include spam/trash
 * @returns {Promise<Array>} Array of message objects
 */
async function listMessages(options = {}) {
  const {
    query = '',
    labelIds = null,
    maxResults = 100,
    includeSpamTrash = false,
  } = options;

  const gmail = await getGmailService();
  const messages = [];
  let pageToken = null;

  try {
    do {
      const params = {
        userId: 'me',
        maxResults: Math.min(maxResults - messages.length, 500),
        includeSpamTrash,
      };

      if (query) params.q = query;
      if (labelIds) params.labelIds = labelIds;
      if (pageToken) params.pageToken = pageToken;

      const response = await gmail.users.messages.list(params);

      if (response.data.messages) {
        messages.push(...response.data.messages);
      }

      pageToken = response.data.nextPageToken;
    } while (pageToken && messages.length < maxResults);

    return messages.slice(0, maxResults);
  } catch (error) {
    console.error('Error listing messages:', error.message);
    throw error;
  }
}

/**
 * List messages with full details.
 * @param {string} query - Gmail search query
 * @param {number} maxResults - Maximum messages to return
 * @returns {Promise<Array>} Array of detailed message objects
 */
async function listMessagesWithDetails(query = '', maxResults = 10) {
  const gmail = await getGmailService();
  const messages = await listMessages({ query, maxResults });
  const detailedMessages = [];

  for (const msg of messages) {
    const fullMsg = await gmail.users.messages.get({
      userId: 'me',
      id: msg.id,
      format: 'metadata',
      metadataHeaders: ['Subject', 'From', 'To', 'Date'],
    });

    const headers = {};
    fullMsg.data.payload.headers.forEach((h) => {
      headers[h.name] = h.value;
    });

    detailedMessages.push({
      id: fullMsg.data.id,
      threadId: fullMsg.data.threadId,
      subject: headers.Subject || '(No Subject)',
      from: headers.From || '',
      to: headers.To || '',
      date: headers.Date || '',
      snippet: fullMsg.data.snippet || '',
      labelIds: fullMsg.data.labelIds || [],
    });
  }

  return detailedMessages;
}

module.exports = {
  listMessages,
  listMessagesWithDetails,
};

// Test execution
if (require.main === module) {
  (async () => {
    console.log('='.repeat(60));
    console.log('Test: Gmail API List Messages Module (Node.js)');
    console.log('='.repeat(60));

    try {
      // Test 1: List basic messages
      console.log('\n[Test 1] Listing messages (max 5)...');
      const messages = await listMessages({ maxResults: 5 });
      console.log(`[OK] Found ${messages.length} messages`);
      if (messages.length > 0) {
        console.log(`     First message ID: ${messages[0].id}`);
        console.log(`     Thread ID: ${messages[0].threadId}`);
      }

      // Test 2: List with query
      console.log('\n[Test 2] Listing unread messages from last 7 days...');
      const unreadMessages = await listMessages({ query: 'is:unread newer_than:7d', maxResults: 5 });
      console.log(`[OK] Found ${unreadMessages.length} unread messages`);

      // Test 3: List with details
      console.log('\n[Test 3] Listing messages with details...');
      const detailed = await listMessagesWithDetails('newer_than:7d', 3);
      console.log(`[OK] Retrieved ${detailed.length} messages with details`);

      for (let i = 0; i < detailed.length; i++) {
        const msg = detailed[i];
        console.log(`\n  [${i + 1}] Subject: ${msg.subject.substring(0, 50)}...`);
        console.log(`      From: ${msg.from.substring(0, 50)}...`);
        console.log(`      Date: ${msg.date}`);
      }

      // Test 4: List by label
      console.log('\n[Test 4] Listing INBOX messages...');
      const inboxMessages = await listMessages({ labelIds: ['INBOX'], maxResults: 3 });
      console.log(`[OK] Found ${inboxMessages.length} INBOX messages`);

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

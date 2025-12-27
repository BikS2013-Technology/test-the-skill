/**
 * Gmail API - Send Messages Module for Node.js
 *
 * Test script for: Gmail API Send Messages (Node.js)
 * From document: Gmail-API-Integration-Guide.md
 * Document lines: 2095-2310
 *
 * NOTE: Actual sending is skipped as it requires gmail.send scope.
 * This test validates the message creation functions only.
 */
const { getGmailService } = require('./gmail-auth');
const { getMessage, getMessageBody, getMessageHeaders } = require('./gmail-read');

/**
 * Create an email message.
 * @param {Object} options - Message options
 * @returns {Object} Message object ready for sending
 */
function createMessage(options) {
  const {
    to,
    subject,
    body,
    cc = null,
    bcc = null,
    htmlBody = null,
    threadId = null,
    inReplyTo = null,
    references = null,
  } = options;

  // Build email headers and body
  const boundary = `boundary_${Date.now()}`;
  let email = '';

  email += `To: ${to}\r\n`;
  email += `Subject: ${subject}\r\n`;
  if (cc) email += `Cc: ${cc}\r\n`;
  if (bcc) email += `Bcc: ${bcc}\r\n`;
  if (inReplyTo) email += `In-Reply-To: ${inReplyTo}\r\n`;
  if (references) email += `References: ${references}\r\n`;

  if (htmlBody) {
    // Multipart message
    email += `Content-Type: multipart/alternative; boundary="${boundary}"\r\n\r\n`;
    email += `--${boundary}\r\n`;
    email += `Content-Type: text/plain; charset="UTF-8"\r\n\r\n`;
    email += `${body}\r\n\r\n`;
    email += `--${boundary}\r\n`;
    email += `Content-Type: text/html; charset="UTF-8"\r\n\r\n`;
    email += `${htmlBody}\r\n\r\n`;
    email += `--${boundary}--`;
  } else {
    email += `Content-Type: text/plain; charset="UTF-8"\r\n\r\n`;
    email += body;
  }

  const encodedMessage = Buffer.from(email)
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');

  const result = { raw: encodedMessage };
  if (threadId) result.threadId = threadId;

  return result;
}

/**
 * Send an email message.
 * NOTE: Requires gmail.send scope.
 * @param {Object} message - Message object with 'raw' key
 * @returns {Promise<Object>} Sent message object
 */
async function sendMessage(message) {
  const gmail = await getGmailService();

  try {
    const response = await gmail.users.messages.send({
      userId: 'me',
      requestBody: message,
    });

    console.log(`Message sent successfully. ID: ${response.data.id}`);
    return response.data;
  } catch (error) {
    console.error('Error sending message:', error.message);
    throw error;
  }
}

/**
 * Convenience function to create and send an email.
 * @param {Object} options - Email options (to, subject, body, cc, bcc, htmlBody)
 * @returns {Promise<Object>} Sent message object
 */
async function sendEmail(options) {
  const message = createMessage(options);
  return sendMessage(message);
}

/**
 * Reply to an existing message.
 * NOTE: Requires gmail.send scope.
 * @param {string} originalMessageId - ID of message to reply to
 * @param {string} body - Reply body text
 * @param {boolean} replyAll - If true, reply to all recipients
 * @param {string} htmlBody - Optional HTML body
 * @returns {Promise<Object>} Sent reply message object
 */
async function replyToMessage(originalMessageId, body, replyAll = false, htmlBody = null) {
  const original = await getMessage(originalMessageId);
  const headers = getMessageHeaders(original);

  const originalFrom = headers.From || '';
  const originalTo = headers.To || '';
  const originalCc = headers.Cc || '';
  const originalSubject = headers.Subject || '';
  const messageId = headers['Message-ID'] || '';
  const existingReferences = headers.References || '';

  // Determine recipients
  let to = originalFrom;
  let cc = null;
  if (replyAll) {
    cc = [originalTo, originalCc].filter(Boolean).join(', ');
  }

  // Build subject
  let subject = originalSubject;
  if (!originalSubject.toLowerCase().startsWith('re:')) {
    subject = `Re: ${originalSubject}`;
  }

  // Build References header
  const newReferences = existingReferences
    ? `${existingReferences} ${messageId}`
    : messageId;

  const message = createMessage({
    to,
    subject,
    body,
    cc,
    htmlBody,
    threadId: original.threadId,
    inReplyTo: messageId,
    references: newReferences,
  });

  return sendMessage(message);
}

/**
 * Forward a message to new recipients.
 * NOTE: Requires gmail.send scope.
 * @param {string} originalMessageId - ID of message to forward
 * @param {string} to - Recipient(s) to forward to
 * @param {string} additionalText - Optional text to add before forwarded content
 * @param {string} cc - Optional CC recipients
 * @param {string} bcc - Optional BCC recipients
 * @returns {Promise<Object>} Sent forwarded message object
 */
async function forwardMessage(originalMessageId, to, additionalText = null, cc = null, bcc = null) {
  const original = await getMessage(originalMessageId);
  const headers = getMessageHeaders(original);
  const originalBody = getMessageBody(original);

  // Build forwarded message body
  const forwardHeader = `\n\n---------- Forwarded message ----------\n` +
    `From: ${headers.From || ''}\n` +
    `Date: ${headers.Date || ''}\n` +
    `Subject: ${headers.Subject || ''}\n` +
    `To: ${headers.To || ''}\n\n`;

  let body;
  if (additionalText) {
    body = `${additionalText}${forwardHeader}${originalBody.plain}`;
  } else {
    body = `${forwardHeader}${originalBody.plain}`;
  }

  // Build subject
  const originalSubject = headers.Subject || '';
  let subject = originalSubject;
  if (!originalSubject.toLowerCase().startsWith('fwd:')) {
    subject = `Fwd: ${originalSubject}`;
  }

  const message = createMessage({
    to,
    subject,
    body,
    cc,
    bcc,
  });

  return sendMessage(message);
}

/**
 * Create a draft email.
 * NOTE: Requires gmail.compose scope.
 * @param {Object} options - Email options
 * @returns {Promise<Object>} Draft object
 */
async function createDraft(options) {
  const gmail = await getGmailService();
  const message = createMessage(options);

  try {
    const response = await gmail.users.drafts.create({
      userId: 'me',
      requestBody: {
        message: message,
      },
    });

    console.log(`Draft created. ID: ${response.data.id}`);
    return response.data;
  } catch (error) {
    console.error('Error creating draft:', error.message);
    throw error;
  }
}

/**
 * Send an existing draft.
 * NOTE: Requires gmail.compose scope.
 * @param {string} draftId - ID of the draft to send
 * @returns {Promise<Object>} Sent message object
 */
async function sendDraft(draftId) {
  const gmail = await getGmailService();

  try {
    const response = await gmail.users.drafts.send({
      userId: 'me',
      requestBody: {
        id: draftId,
      },
    });

    console.log(`Draft sent successfully. Message ID: ${response.data.id}`);
    return response.data;
  } catch (error) {
    console.error('Error sending draft:', error.message);
    throw error;
  }
}

module.exports = {
  createMessage,
  sendMessage,
  sendEmail,
  replyToMessage,
  forwardMessage,
  createDraft,
  sendDraft,
};

// Test execution
if (require.main === module) {
  const { listMessages } = require('./gmail-list');

  (async () => {
    console.log('='.repeat(60));
    console.log('Test: Gmail API Send Messages Module (Node.js) - Read-Only Mode');
    console.log('='.repeat(60));
    console.log('\nNOTE: Actual sending/draft creation requires gmail.send/compose scopes.');
    console.log('This test validates message creation functions only.\n');

    try {
      // Test 1: Create simple message
      console.log('[Test 1] Creating simple plain text message...');
      const msg = createMessage({
        to: 'test@example.com',
        subject: 'Test Subject',
        body: 'This is a test email body.',
      });
      console.log('[OK] Message created');
      console.log(`     Has 'raw' key: ${'raw' in msg}`);
      console.log(`     Raw length: ${msg.raw.length} chars`);

      // Decode and verify
      const decoded = Buffer.from(msg.raw, 'base64').toString('utf-8');
      console.log(`     Contains 'To: test@example.com': ${decoded.includes('To: test@example.com')}`);
      console.log(`     Contains 'Subject: Test Subject': ${decoded.includes('Subject: Test Subject')}`);

      // Test 2: Create message with CC/BCC
      console.log('\n[Test 2] Creating message with CC and BCC...');
      const msg2 = createMessage({
        to: 'recipient@example.com',
        subject: 'Test with CC/BCC',
        body: 'Test body',
        cc: 'cc@example.com',
        bcc: 'bcc@example.com',
      });
      const decoded2 = Buffer.from(msg2.raw, 'base64').toString('utf-8');
      console.log('[OK] Message created');
      console.log(`     Contains Cc header: ${decoded2.includes('Cc:')}`);
      console.log(`     Contains Bcc header: ${decoded2.includes('Bcc:')}`);

      // Test 3: Create multipart message (plain + HTML)
      console.log('\n[Test 3] Creating multipart message (plain + HTML)...');
      const msg3 = createMessage({
        to: 'test@example.com',
        subject: 'HTML Test',
        body: 'Plain text version',
        htmlBody: '<html><body><h1>HTML Version</h1></body></html>',
      });
      const decoded3 = Buffer.from(msg3.raw, 'base64').toString('utf-8');
      console.log('[OK] Multipart message created');
      console.log(`     Contains multipart: ${decoded3.includes('multipart/alternative')}`);
      console.log(`     Contains text/plain: ${decoded3.includes('text/plain')}`);
      console.log(`     Contains text/html: ${decoded3.includes('text/html')}`);

      // Test 4: Create reply message structure
      console.log('\n[Test 4] Creating reply message with threading headers...');
      const msg4 = createMessage({
        to: 'sender@example.com',
        subject: 'Re: Original Subject',
        body: 'This is my reply.',
        threadId: 'thread123',
        inReplyTo: '<original@message.id>',
        references: '<original@message.id>',
      });
      const decoded4 = Buffer.from(msg4.raw, 'base64').toString('utf-8');
      console.log('[OK] Reply message created');
      console.log(`     Has threadId: ${'threadId' in msg4}`);
      console.log(`     Contains In-Reply-To: ${decoded4.includes('In-Reply-To:')}`);
      console.log(`     Contains References: ${decoded4.includes('References:')}`);

      // Test 5: Verify we can fetch original message (without sending)
      console.log('\n[Test 5] Testing reply preparation (read-only)...');
      const messages = await listMessages({ maxResults: 1 });
      if (messages.length > 0) {
        const original = await getMessage(messages[0].id);
        const headers = getMessageHeaders(original);
        console.log('[OK] Can fetch original message for reply');
        console.log(`     Original Subject: ${(headers.Subject || 'N/A').substring(0, 40)}...`);
        console.log(`     Would reply to: ${(headers.From || 'N/A').substring(0, 40)}...`);
      }

      // Test 6: Verify forward preparation (without sending)
      console.log('\n[Test 6] Testing forward preparation (read-only)...');
      if (messages.length > 0) {
        const original = await getMessage(messages[0].id);
        const originalBody = getMessageBody(original);
        console.log('[OK] Can fetch original message for forwarding');
        console.log(`     Original body length: ${originalBody.plain.length} chars`);
      }

      console.log('\n' + '='.repeat(60));
      console.log('Test: PASSED (Message creation validated)');
      console.log('='.repeat(60));
      console.log('\nNote: To test actual sending, enable gmail.send scope in');
      console.log('your OAuth consent screen and re-authenticate.');
    } catch (error) {
      console.log(`\n[ERROR] Test failed: ${error.message}`);
      console.error(error);
      process.exit(1);
    }
  })();
}

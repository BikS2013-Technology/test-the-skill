# Gmail API Integration Guide - Part 1: OAuth Setup

This guide provides detailed instructions for setting up OAuth 2.0 authentication to access Gmail programmatically using Python. It covers creating a Google Cloud project, configuring the OAuth consent screen, creating credentials, and understanding scopes.

> **Note:** This is Part 1 of the Gmail API Integration Guide, focusing on OAuth setup and the `credentials.json` file. API operations (listing messages, sending emails, etc.) are covered in Part 2.

---

## Table of Contents

1. [Prerequisites and Setup](#1-prerequisites-and-setup)
   - [1.1 Create a Google Cloud Project](#11-create-a-google-cloud-project)
   - [1.2 Configure OAuth Consent Screen](#12-configure-oauth-consent-screen)
   - [1.3 Create OAuth 2.0 Credentials](#13-create-oauth-20-credentials)
   - [1.4 Authentication Methods: OAuth 2.0 vs Service Accounts](#14-authentication-methods-oauth-20-vs-service-accounts)
   - [1.5 Enable APIs Using gcloud CLI](#15-enable-apis-using-gcloud-cli)
   - [1.6 OAuth Consent Screen Configuration (CLI Limitations)](#16-oauth-consent-screen-configuration-cli-limitations)
2. [OAuth 2.0 Scopes](#2-oauth-20-scopes)
   - [2.1 Where to Configure Scopes](#21-where-to-configure-scopes-summary)
   - [2.2 Available Gmail API Scopes](#22-available-gmail-api-scopes)
   - [2.3 Scope Selection Guide](#23-scope-selection-guide)
   - [2.4 Scope Combinations for Common Use Cases](#24-scope-combinations-for-common-use-cases)
   - [2.5 Important Notes About Scopes](#25-important-notes-about-scopes)
   - [2.6 CASA Security Assessment Requirements](#26-casa-security-assessment-requirements)

---

## 1. Prerequisites and Setup

### 1.1 Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Navigate to **APIs & Services > Library**
   - Search for "Gmail API"
   - Click **Enable**

### 1.2 Configure OAuth Consent Screen

The OAuth consent screen is what users see when your application requests access to their Gmail data. This is also where you **declare the scopes** your application will use.

#### 1.2.1 Understanding Where Scopes Are Configured

> **Common Confusion:** Many developers wonder whether scopes are configured in the OAuth Consent Screen, the OAuth Client, or the application code. Here's the answer:

| Location | What You Configure | Purpose |
|----------|-------------------|---------|
| **OAuth Consent Screen → Data Access** | DECLARE scopes | Register scopes for Google's review and user transparency |
| **OAuth Client** | Client ID, secret, redirect URIs | Identify your application (NO scope configuration here) |
| **Application Code** | REQUEST scopes | Actually request specific scopes during authentication |

> **Note:** Scopes are configured in the **Data Access** section of the OAuth Consent Screen, NOT in the OAuth Client settings.

**Key Rule:** For **External apps** (personal Gmail, public apps), the scopes in your code **MUST match** what you've declared in the OAuth Consent Screen. Mismatches cause "unverified app" warnings.

#### 1.2.2 Internal vs External Apps

| App Type | Who Can Use It | Scope Requirements | Google Verification |
|----------|---------------|-------------------|---------------------|
| **Internal** | Only users in your Google Workspace organization | Scopes NOT required in consent screen | NOT required |
| **External** | Anyone (including personal @gmail.com) | Scopes MUST be declared in consent screen | Required for sensitive/restricted scopes |

**If you're accessing a personal Gmail account (@gmail.com), you MUST use External.**

#### 1.2.3 Step-by-Step: Configure OAuth Consent Screen

**Step 1: Navigate to OAuth Consent Screen**
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Select your project
- Navigate to **APIs & Services > OAuth consent screen**
- Or go to: **Google Auth platform > Branding** (newer console)

**Step 2: Select User Type**
- **Internal**: For Google Workspace organizations only
- **External**: For personal Gmail and public apps (most common)

**Step 3: Fill in App Information**
- **App name**: Name shown to users on consent screen
- **User support email**: Contact email for users
- **App logo** (optional): Your application's logo
- **Application home page** (optional): Your app's website
- **Application privacy policy link** (optional but recommended)
- **Application terms of service link** (optional)

**Step 4: Add Developer Contact Information**
- Enter email addresses for Google to contact you about your project

**Step 5: Add Scopes in Data Access (IMPORTANT for External Apps)**

1. Navigate to the **Data Access** section (or click **Add or Remove Scopes** if prompted)
2. Click **Add or Remove Scopes**
3. Find the Gmail API scopes you need:
   - Search for "Gmail" in the filter
   - Or manually enter the scope URL
4. Select the scopes your application requires
5. Click **Update** to save

> **Location:** In the newer Google Cloud Console, this is under **Google Auth platform > Data Access**. In the older console, it's under **APIs & Services > OAuth consent screen**, then scroll to the "Scopes" section.

**Step 6: Add Test Users (External Apps Only)**
- While your app is in "Testing" status, only test users can access it
- Add email addresses of users who will test your app
- Maximum 100 test users

**Step 7: Review and Create**
- Review your settings
- Click **Save and Continue** or **Create**

#### 1.2.4 How to Add Scopes in the Data Access Section

**Detailed Steps:**

1. In the Google Cloud Console, go to your OAuth consent screen settings
2. Navigate to the **Data Access** section:
   - **Newer console:** Google Auth platform > **Data Access**
   - **Older console:** APIs & Services > OAuth consent screen > scroll to **Scopes**
3. Click **Add or Remove Scopes**
4. A panel opens showing available scopes:

```
┌─────────────────────────────────────────────────────────────────┐
│  Add or Remove Scopes                                           │
├─────────────────────────────────────────────────────────────────┤
│  Filter: [Gmail_____________________]                           │
│                                                                 │
│  ☑ .../auth/gmail.readonly     - Read all Gmail messages       │
│  ☑ .../auth/gmail.send         - Send email on your behalf     │
│  ☐ .../auth/gmail.compose      - Manage drafts and send        │
│  ☐ .../auth/gmail.modify       - Read, compose, send, delete   │
│  ☐ https://mail.google.com/    - Full access to Gmail          │
│                                                                 │
│  [Update]  [Cancel]                                             │
└─────────────────────────────────────────────────────────────────┘
```

4. Check the scopes your application needs
5. Click **Update**
6. The scopes are now declared for your app

**Alternatively, manually enter scope URLs:**
- Click **Add Scopes** and enter the full URL:
  - `https://www.googleapis.com/auth/gmail.readonly`
  - `https://www.googleapis.com/auth/gmail.send`

> **Scope Selection:** For a complete list of available Gmail API scopes and guidance on choosing the right ones, see [Section 2: OAuth 2.0 Scopes](#2-oauth-20-scopes).

#### 1.2.5 Scope Categories and Verification Requirements

| Category | Examples | User Impact | Verification Required |
|----------|----------|-------------|----------------------|
| **Non-sensitive** | `userinfo.email`, `gmail.labels` | Basic info, labels only | Basic verification only |
| **Sensitive** | `gmail.send` | Send emails | Additional verification |
| **Restricted** | `gmail.readonly`, `gmail.modify`, `mail.google.com/` | Read/write access | Security assessment required |

**Gmail API Scope Classifications:**

| Scope | Category | Notes |
|-------|----------|-------|
| `gmail.labels` | **Non-sensitive** | Labels management only |
| `gmail.send` | Sensitive | Send emails only |
| `gmail.readonly` | **Restricted** | Read-only access |
| `gmail.compose` | **Restricted** | Drafts and sending |
| `gmail.insert` | **Restricted** | Insert messages |
| `gmail.modify` | **Restricted** | Most operations |
| `gmail.metadata` | **Restricted** | Headers and labels only |
| `gmail.settings.basic` | **Restricted** | Basic mail settings |
| `gmail.settings.sharing` | **Restricted** | Sensitive mail settings |
| `mail.google.com/` | **Restricted** | Full access - requires security assessment |

> **Important:** Restricted scopes require annual CASA (Cloud Application Security Assessment) by a Google-approved assessor. See Section 2.6 for details.

#### 1.2.6 What Happens If Scopes Don't Match?

If your code requests scopes that aren't declared in the OAuth Consent Screen:

| Scenario | Result |
|----------|--------|
| Internal app | Usually works (scopes not enforced) |
| External app (Testing) | May work for test users with warning |
| External app (Production) | "Unverified app" screen shown to users |
| External app (Verified) | Error - scope not approved |

**Symptoms of scope mismatch:**
- Users see "This app isn't verified" warning
- "Access blocked" errors
- App limited to 100 users
- Error: "Scope has not been approved for this project"

**Solution:** Always ensure your code requests the SAME scopes declared in your OAuth Consent Screen.

#### 1.2.7 App Publishing Status

| Status | Description | User Limit |
|--------|-------------|-----------|
| **Testing** | Only test users can access | 100 test users |
| **In production** | Published but unverified | 100 users (with warning) |
| **Verified** | Google-verified app | Unlimited users |

To publish your app:
1. Complete all required consent screen fields
2. Add all scopes your app uses
3. Click **Publish App**
4. Submit for verification if using sensitive/restricted scopes

### 1.3 Create OAuth 2.0 Credentials

OAuth 2.0 Client IDs are required to authenticate users and access their Gmail data. This section explains when you need OAuth credentials, how to create them, and how to use them.

#### 1.3.1 Do You Need OAuth 2.0 Credentials?

| Your Scenario | What You Need |
|--------------|---------------|
| Personal Gmail account (@gmail.com) | ✅ **OAuth 2.0 Client ID** (this section) |
| Desktop/CLI application | ✅ **OAuth 2.0 Client ID** (Desktop app type) |
| Web application with user login | ✅ **OAuth 2.0 Client ID** (Web app type) |
| Google Workspace server-to-server | Service Account (covered in separate guide) |
| API key only (no user data) | API Key (not applicable for Gmail) |

**For Gmail API access, you will almost always need an OAuth 2.0 Client ID** because the Gmail API requires user authorization to access mailbox data.

#### 1.3.2 OAuth 2.0 Client Types

| Client Type | Use Case | Example |
|------------|----------|---------|
| **Desktop app** | Standalone applications, CLI tools, scripts | Python/Node.js scripts on your computer |
| **Web application** | Server-side apps, websites with user login | Web app where users sign in with Google |
| **Android** | Native Android applications | Mobile Gmail client |
| **iOS** | Native iOS applications | iPhone/iPad Gmail app |
| **Chrome Extension** | Browser extensions | Gmail productivity extension |
| **TVs & Limited Input** | Smart TVs, IoT devices | TV email client |

**For this guide, we focus on Desktop app** as it's the most common for programmatic Gmail access.

#### 1.3.3 Create OAuth 2.0 Client ID (Console Method)

> **Note:** As of December 2025, there is **no gcloud CLI command** to create standard OAuth 2.0 Client IDs. This must be done through the Google Cloud Console.

**Step-by-Step Instructions:**

1. **Navigate to Credentials Page**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Select your project
   - Navigate to **APIs & Services > Credentials**
   - Or go directly to: `https://console.cloud.google.com/apis/credentials?project=YOUR_PROJECT_ID`

2. **Create OAuth Client ID**
   - Click **+ CREATE CREDENTIALS** at the top
   - Select **OAuth client ID**

3. **Configure the Client**
   - **Application type**: Select **Desktop app**
   - **Name**: Enter a descriptive name (e.g., "Gmail API Desktop Client")
   - This name is only shown in the Google Cloud Console

4. **Create and Download**
   - Click **CREATE**
   - A dialog will show your **Client ID** and **Client Secret**
   - Click **DOWNLOAD JSON** to download the credentials file

5. **Save the Credentials File**
   - Save the downloaded file as `credentials.json` in your project directory
   - The file will be named something like `client_secret_XXXXX.apps.googleusercontent.com.json`
   - Rename it to `credentials.json` for consistency with the code examples

> **Best Practice:** Download the JSON file immediately after creation and store it securely. Client secrets should be treated as sensitive credentials—if lost, you may need to create a new OAuth client.

#### 1.3.4 Understanding the credentials.json File

The `credentials.json` file contains your OAuth 2.0 client configuration:

```json
{
  "installed": {
    "client_id": "XXXXX.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "GOCSPX-XXXXXXXXXXXXX",
    "redirect_uris": ["http://localhost"]
  }
}
```

| Field | Description |
|-------|-------------|
| `client_id` | Unique identifier for your application |
| `project_id` | Your Google Cloud project ID |
| `auth_uri` | Google's authorization endpoint |
| `token_uri` | Endpoint to exchange auth code for tokens |
| `client_secret` | Secret key (keep confidential!) |
| `redirect_uris` | Where Google redirects after authorization |

#### 1.3.5 The Authentication Flow

When you run your application for the first time:

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Your App       │      │  Google OAuth   │      │  User's Browser │
│  (credentials.  │ ───► │  Server         │ ───► │  Login & Consent│
│   json)         │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
        │                                                  │
        │                                                  │
        ▼                                                  ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  token.json     │ ◄─── │  Access Token   │ ◄─── │  Authorization  │
│  (saved for     │      │  + Refresh Token│      │  Code           │
│   future use)   │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

1. **First run**: App opens browser → User logs in → User grants permission → App receives tokens
2. **Subsequent runs**: App uses saved `token.json` → Automatically refreshes if expired

#### 1.3.6 Using Credentials with gcloud CLI

While you cannot CREATE OAuth clients via CLI, you CAN use existing credentials:

```bash
# Use your OAuth credentials for application-default login
gcloud auth application-default login \
    --client-id-file=credentials.json \
    --scopes='https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.send'
```

This stores tokens in a well-known location that Google client libraries can access automatically.

#### 1.3.7 Security Best Practices

| Practice | Reason |
|----------|--------|
| **Never commit `credentials.json` to git** | Contains your client secret |
| **Add to `.gitignore`** | Prevents accidental commits |
| **Never commit `token.json` to git** | Contains access/refresh tokens |
| **Store secrets in environment variables** | For production deployments |
| **Download credentials immediately** | Secrets only visible at creation (2025+) |
| **Use separate credentials per environment** | Dev, staging, production |

Add to your `.gitignore`:

```gitignore
# OAuth credentials - NEVER commit these
credentials.json
client_secret*.json
token.json

# Python token files
*.pickle
```

#### 1.3.8 Creating Credentials for Web Applications

If you're building a web application instead of a desktop app:

1. Select **Web application** as the application type
2. Add **Authorized JavaScript origins** (e.g., `http://localhost:3000` for development)
3. Add **Authorized redirect URIs** (e.g., `http://localhost:3000/oauth2callback`)

Web applications use the same `credentials.json` format but with `"web"` instead of `"installed"`:

```json
{
  "web": {
    "client_id": "XXXXX.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_secret": "GOCSPX-XXXXXXXXXXXXX",
    "redirect_uris": ["http://localhost:3000/oauth2callback"],
    "javascript_origins": ["http://localhost:3000"]
  }
}
```

#### 1.3.9 Troubleshooting OAuth Client Issues

| Error | Cause | Solution |
|-------|-------|----------|
| `redirect_uri_mismatch` | Redirect URI doesn't match configured URIs | Add the exact URI to your OAuth client settings |
| `invalid_client` | Wrong client ID or secret | Re-download credentials.json |
| `access_denied` | User denied permission | User must click "Allow" on consent screen |
| `invalid_grant` | Token expired or revoked | Delete token.json and re-authenticate |
| File not found | credentials.json missing | Download from Cloud Console |

**Important:** Never commit `credentials.json` or `token.json` to source control!

### 1.4 Authentication Methods: OAuth 2.0 vs Service Accounts

The Gmail API supports two authentication methods, but their availability depends on your account type:

| Account Type | OAuth 2.0 Client ID | Service Account |
|-------------|---------------------|-----------------|
| Personal Gmail (@gmail.com) | ✅ Supported | ❌ **NOT Supported** |
| Google Workspace | ✅ Supported | ✅ Supported (with domain-wide delegation) |

#### Why Service Accounts Don't Work with Personal Gmail

Service accounts are designed for server-to-server interactions where no user is directly involved. According to Google's documentation:

> "By themselves, service accounts cannot be used to access user data; data customarily accessed using Workspace APIs. However, a service account can access user data by implementing domain-wide delegation of authority."

**Domain-wide delegation** is an administrative feature exclusive to Google Workspace organizations that allows a service account to impersonate users within that organization. Since personal Gmail accounts don't belong to a Google Workspace domain, there is no administrator who can grant this delegation authority.

#### When to Use Each Authentication Method

| Scenario | Recommended Method |
|----------|-------------------|
| Personal Gmail access | OAuth 2.0 Client ID (user consent required) |
| Desktop/CLI application | OAuth 2.0 Client ID (Desktop app type) |
| Web application with user login | OAuth 2.0 Client ID (Web app type) |
| Google Workspace automation (server-to-server) | Service Account with domain-wide delegation |
| Background processing for Workspace users | Service Account with domain-wide delegation |

**For personal Gmail accounts**, you must use the OAuth 2.0 flow described in Section 1.3 of this guide, which requires user consent through a browser-based authentication.

**For Google Workspace accounts**, you have the option to use Service Accounts with domain-wide delegation. Service Account implementation is covered in a separate guide.

### 1.5 Enable APIs Using gcloud CLI

As an alternative to the Google Cloud Console UI, you can use the **gcloud CLI** to enable APIs programmatically. This is especially useful for:

- Automating project setup in scripts
- CI/CD pipelines
- Infrastructure as Code (IaC) workflows
- Batch operations across multiple projects

#### 1.5.1 Prerequisites

1. **Install the Google Cloud CLI**: Download and install from [cloud.google.com/sdk](https://cloud.google.com/sdk/docs/install)

2. **Initialize and authenticate**:
   ```bash
   # Initialize gcloud (first time setup)
   gcloud init

   # Or authenticate separately
   gcloud auth login
   ```

3. **Set your project** (or specify with `--project` flag):
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

#### 1.5.2 Enable the Gmail API

```bash
# Enable Gmail API for the current project
gcloud services enable gmail.googleapis.com

# Or specify a project explicitly
gcloud services enable gmail.googleapis.com --project=YOUR_PROJECT_ID
```

#### 1.5.3 Enable Multiple APIs

You can enable multiple APIs in sequence:

```bash
# Enable Gmail and related APIs
gcloud services enable gmail.googleapis.com
gcloud services enable drive.googleapis.com
gcloud services enable calendar-json.googleapis.com
```

Or create a shell script for batch operations:

```bash
#!/bin/bash
# enable-workspace-apis.sh
# Script to enable Google Workspace APIs for a project

PROJECT_ID="${1:-$(gcloud config get-value project)}"

if [ -z "$PROJECT_ID" ]; then
    echo "Error: No project ID specified and no default project set."
    echo "Usage: $0 <PROJECT_ID>"
    exit 1
fi

echo "Enabling APIs for project: $PROJECT_ID"

# List of APIs to enable
APIS=(
    "gmail.googleapis.com"
    "drive.googleapis.com"
    "calendar-json.googleapis.com"
    "sheets.googleapis.com"
    "docs.googleapis.com"
)

for api in "${APIS[@]}"; do
    echo "Enabling $api..."
    gcloud services enable "$api" --project="$PROJECT_ID"
    if [ $? -eq 0 ]; then
        echo "  ✓ $api enabled successfully"
    else
        echo "  ✗ Failed to enable $api"
    fi
done

echo "Done!"
```

Make the script executable and run it:

```bash
chmod +x enable-workspace-apis.sh
./enable-workspace-apis.sh YOUR_PROJECT_ID
```

#### 1.5.4 Common Google Workspace API Service Names

| Service | API Service Name |
|---------|-----------------|
| Gmail | `gmail.googleapis.com` |
| Google Drive | `drive.googleapis.com` |
| Google Calendar | `calendar-json.googleapis.com` |
| Google Sheets | `sheets.googleapis.com` |
| Google Docs | `docs.googleapis.com` |
| Google Slides | `slides.googleapis.com` |
| Google Chat | `chat.googleapis.com` |
| Google Meet | `meet.googleapis.com` |
| Admin SDK | `admin.googleapis.com` |
| People API | `people.googleapis.com` |

#### 1.5.5 List Enabled APIs

To verify which APIs are enabled in your project:

```bash
# List all enabled services
gcloud services list --enabled

# Filter for specific APIs
gcloud services list --enabled --filter="name:gmail"
```

#### 1.5.6 Disable an API

To disable an API (use with caution):

```bash
gcloud services disable gmail.googleapis.com
```

> **Warning:** Disabling an API may break applications that depend on it. Data storage charges may continue even after disabling API access.

#### 1.5.7 Check API Status

To check if a specific API is enabled:

```bash
# List available services matching a pattern
gcloud services list --available --filter="name:gmail"

# Describe a specific service
gcloud services describe gmail.googleapis.com
```

#### 1.5.8 Required Permissions

To enable/disable APIs, your account needs the **Service Usage Admin** role (`roles/serviceusage.serviceUsageAdmin`) or equivalent permissions on the project.

```bash
# Grant Service Usage Admin role to a user
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="user:email@example.com" \
    --role="roles/serviceusage.serviceUsageAdmin"
```

#### 1.5.9 Rate Limits

API enablement operations use the `serviceusage.googleapis.com/mutate_requests` quota with a default limit of **2 queries per second (QPS)**. For batch operations, consider adding delays between requests.

### 1.6 OAuth Consent Screen Configuration (CLI Limitations)

Unlike enabling APIs (Section 1.5), configuring the OAuth consent screen for general OAuth 2.0 clients **cannot be fully automated via gcloud CLI**. This section explains what is and isn't possible.

#### 1.6.1 Current Limitations

> **Important:** As of December 2025, there is **no gcloud CLI command** to configure the OAuth consent screen for standard OAuth 2.0 clients used with Gmail API or other Google Workspace APIs. This is a [known feature request](https://issuetracker.google.com/issues/35907249) in Google's Issue Tracker.

| Configuration Task | gcloud CLI Support | Notes |
|-------------------|-------------------|-------|
| Enable APIs | ✅ Supported | `gcloud services enable` |
| Create OAuth 2.0 Client ID | ❌ **Not Supported** | Must use Console |
| Configure OAuth Consent Screen | ❌ **Not Supported** | Must use Console |
| Set Scopes | ❌ **Not Supported** | Must use Console |
| Add Test Users | ❌ **Not Supported** | Must use Console |
| IAP OAuth Brands (internal only) | ✅ Limited Support | For IAP use cases only |

#### 1.6.2 Understanding Identity-Aware Proxy (IAP)

Before discussing IAP OAuth Brands, it's important to understand what IAP is and its intended use cases—this clarifies why IAP-based OAuth is not suitable for Gmail API integration.

**What is Identity-Aware Proxy (IAP)?**

Identity-Aware Proxy (IAP) is a Google Cloud security service that provides application-level access control based on user identity rather than network location. It implements Google's **BeyondCorp** zero-trust security model, allowing organizations to secure applications without relying on traditional VPNs.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TRADITIONAL VPN vs IAP ACCESS MODEL                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Traditional VPN:                    Identity-Aware Proxy:                  │
│  ─────────────────                   ─────────────────────                  │
│  User → VPN → Corporate Network →    User → Browser → IAP → Application    │
│       → Application                        (identity verified at app level) │
│                                                                             │
│  • Network-based trust               • Identity-based trust                 │
│  • VPN client required               • No client software needed            │
│  • Access to entire network          • Access to specific applications      │
│  • Complex to manage                 • Centralized policy management        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Recommended IAP Use Cases:**

| Use Case | Description | Example |
|----------|-------------|---------|
| **Secure Internal Web Apps** | Protect internal applications without VPN | Corporate intranet, admin dashboards |
| **Remote Workforce Access** | Enable secure remote access to corporate apps | Employees accessing internal tools from home |
| **VM Administration** | Secure SSH/RDP access to VMs without public IPs | DevOps accessing production servers via IAP TCP forwarding |
| **Zero-Trust Implementation** | Enforce BeyondCorp security model | Context-aware access based on user, device, and location |
| **Microservices Protection** | Secure backend services in Kubernetes/Cloud Run | Protecting APIs between internal services |
| **Multi-Tenant Applications** | Manage access across multiple organizations | SaaS platforms with enterprise customers |

**IAP Key Features:**

| Feature | Benefit |
|---------|---------|
| **Context-Aware Access** | Grant access based on user identity, device security status, IP address, and location |
| **No Client Software** | Users access applications directly through their browser |
| **Centralized Policies** | Define access policies once, apply across all protected applications |
| **Audit Logging** | Detailed logs of all access attempts for compliance |
| **Integration** | Works with Cloud IAM, Cloud Logging, and Security Command Center |

**When to Use IAP:**

✅ **Use IAP when you need to:**
- Protect web applications hosted on Google Cloud (App Engine, Compute Engine, GKE, Cloud Run)
- Secure access to on-premises applications via Cloud Load Balancing
- Replace or reduce VPN dependency
- Implement zero-trust access controls
- Provide secure administrative access to VMs (SSH/RDP tunneling)

❌ **Do NOT use IAP for:**
- Gmail API integration (IAP OAuth clients cannot request Gmail scopes)
- Accessing Google Workspace user data
- Public-facing applications that need external user OAuth
- Standard OAuth 2.0 flows for desktop/mobile applications

> **Key Distinction:** IAP is for protecting **your applications** from unauthorized access. Gmail API OAuth is for **your application accessing user data** in Gmail. These are fundamentally different use cases requiring different OAuth configurations.

For more information about IAP, see the [Identity-Aware Proxy documentation](https://cloud.google.com/iap/docs/concepts-overview).

#### 1.6.3 What IS Available: IAP OAuth Brands (Limited Use Case)

For **Identity-Aware Proxy (IAP)** use cases only, you can create OAuth brands and clients programmatically. However, these have significant limitations that make them **unsuitable for Gmail API integration**:

```bash
# List existing OAuth brands (IAP only)
gcloud iap oauth-brands list

# Create an OAuth brand for IAP (internal users only)
gcloud iap oauth-brands create \
    --application_title="My Application" \
    --support_email="support@example.com"

# Create an OAuth client for IAP
gcloud iap oauth-clients create projects/PROJECT_NUMBER/brands/BRAND_ID \
    --display_name="My IAP Client"
```

**Why IAP OAuth brands are NOT suitable for Gmail API:**

| Limitation | Impact |
|-----------|--------|
| Internal users only | Cannot be used for external/public apps |
| IAP-locked | Clients can only be used with Identity-Aware Proxy |
| No scope configuration | Cannot specify Gmail API scopes |
| Unreviewed status | Requires manual console steps to publish |
| 500 client limit | API-created clients count against this limit |

#### 1.6.4 Required Manual Steps

For Gmail API integration, you **must** configure the OAuth consent screen manually:

1. **Navigate to Google Cloud Console**
   - Go to [console.cloud.google.com](https://console.cloud.google.com)
   - Select your project

2. **Configure OAuth Consent Screen**
   - Navigate to **APIs & Services > OAuth consent screen** (or **Google Auth platform > Branding** in newer console)
   - Select User Type:
     - **Internal**: For Google Workspace organizations only (no review required)
     - **External**: For personal Gmail accounts (may require verification for sensitive scopes)

3. **Enter Required Information**
   - App name
   - User support email
   - Developer contact information

4. **Configure Scopes**
   - Add the Gmail API scopes your app requires (see Section 2)
   - Sensitive/restricted scopes may require Google verification

5. **Add Test Users** (External apps only)
   - Add email addresses of users who can test before verification

6. **Create OAuth 2.0 Credentials**
   - Go to **APIs & Services > Credentials**
   - Click **Create Credentials > OAuth client ID**
   - Download the `credentials.json` file

#### 1.6.5 Terraform Partial Support

If you use Terraform for infrastructure management, there is **partial support** for IAP OAuth configuration:

```hcl
# Note: This is for IAP use cases only, NOT suitable for Gmail API

resource "google_iap_brand" "project_brand" {
  support_email     = "support@example.com"
  application_title = "My Application"
  project           = google_project.my_project.project_id
}

resource "google_iap_client" "project_client" {
  display_name = "My IAP Client"
  brand        = google_iap_brand.project_brand.name
}
```

**Limitations:**
- Only creates internal brands
- No support for OAuth consent screen scopes
- Cannot create standard OAuth 2.0 client credentials
- [Feature request for scope configuration](https://github.com/hashicorp/terraform-provider-google/issues/17649) is open

#### 1.6.6 Automation Workaround: Semi-Automated Setup Script

While you cannot fully automate OAuth consent screen configuration, you can automate the preparatory steps and provide clear instructions for the manual portions:

```bash
#!/bin/bash
# setup-gmail-api-project.sh
# Semi-automated Gmail API project setup

PROJECT_ID="${1:?Error: PROJECT_ID required}"
SUPPORT_EMAIL="${2:?Error: SUPPORT_EMAIL required}"

echo "=============================================="
echo "Gmail API Project Setup"
echo "=============================================="

# Step 1: Set the project
echo "[1/4] Setting active project..."
gcloud config set project "$PROJECT_ID"

# Step 2: Enable required APIs
echo "[2/4] Enabling Gmail API..."
gcloud services enable gmail.googleapis.com

# Step 3: Open the OAuth consent screen configuration page
echo "[3/4] Opening OAuth consent screen configuration..."
echo ""
echo "=============================================="
echo "MANUAL STEPS REQUIRED"
echo "=============================================="
echo ""
echo "The OAuth consent screen cannot be configured via CLI."
echo "Please complete these steps in your browser:"
echo ""
echo "1. Open: https://console.cloud.google.com/apis/credentials/consent?project=$PROJECT_ID"
echo ""
echo "2. Configure the OAuth consent screen:"
echo "   - User Type: Select 'External' for personal Gmail or 'Internal' for Workspace"
echo "   - App name: Enter your application name"
echo "   - User support email: $SUPPORT_EMAIL"
echo "   - Developer contact: $SUPPORT_EMAIL"
echo ""
echo "3. Add scopes (click 'Add or Remove Scopes'):"
echo "   - https://www.googleapis.com/auth/gmail.readonly"
echo "   - https://www.googleapis.com/auth/gmail.send"
echo "   - https://www.googleapis.com/auth/gmail.modify"
echo "   (Select based on your needs)"
echo ""
echo "4. Add test users (if External user type)"
echo ""
echo "5. Save and continue"
echo ""
echo "=============================================="
echo ""

# Step 4: Provide link to create credentials
echo "[4/4] After configuring consent screen, create credentials:"
echo ""
echo "1. Open: https://console.cloud.google.com/apis/credentials?project=$PROJECT_ID"
echo "2. Click 'Create Credentials' > 'OAuth client ID'"
echo "3. Select 'Desktop app' as application type"
echo "4. Download the JSON file as 'credentials.json'"
echo ""
echo "Setup preparation complete!"
```

Make executable and run:

```bash
chmod +x setup-gmail-api-project.sh
./setup-gmail-api-project.sh my-project-id support@example.com
```

#### 1.6.7 Future Improvements

This limitation is tracked in:
- [Google Issue Tracker #35907249](https://issuetracker.google.com/issues/35907249) - Request for gcloud CLI support
- [Terraform Provider Issue #17649](https://github.com/hashicorp/terraform-provider-google/issues/17649) - Request for scope configuration support

Monitor these issues for updates on programmatic OAuth consent screen configuration.

---

## 2. OAuth 2.0 Scopes

Scopes define what permissions your application requests from users. This section explains the available Gmail API scopes and how to use them.

### 2.1 Where to Configure Scopes (Summary)

As explained in Section 1.2, scopes are configured in **two places**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SCOPE CONFIGURATION FLOW                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. OAuth Consent Screen              2. Application Code                   │
│     (Data Access section)                                                   │
│  ───────────────────────────          ─────────────────────                 │
│  DECLARE scopes here             ──►  REQUEST same scopes here              │
│  (for Google's review)                (during authentication)               │
│                                                                             │
│  Google Cloud Console:                Python example:                       │
│  Google Auth platform >               SCOPES = [                            │
│  Data Access >                          'https://.../gmail.readonly',       │
│  Add or Remove Scopes                   'https://.../gmail.send',           │
│                                       ]                                     │
│                                                                             │
│  ⚠️ These MUST match for External apps!                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Available Gmail API Scopes

Choose the **minimum scopes** required for your use case (principle of least privilege):

| Scope | Description | Category |
|-------|-------------|----------|
| `https://www.googleapis.com/auth/gmail.labels` | Manage labels only | **Non-sensitive** |
| `https://www.googleapis.com/auth/gmail.send` | Send emails only | Sensitive |
| `https://www.googleapis.com/auth/gmail.readonly` | Read-only access to messages and settings | **Restricted** |
| `https://www.googleapis.com/auth/gmail.compose` | Create, read, update, and delete drafts; send emails | **Restricted** |
| `https://www.googleapis.com/auth/gmail.insert` | Insert and import messages only | **Restricted** |
| `https://www.googleapis.com/auth/gmail.modify` | All read/write operations except permanent deletion | **Restricted** |
| `https://www.googleapis.com/auth/gmail.metadata` | Read headers and labels (no message bodies) | **Restricted** |
| `https://www.googleapis.com/auth/gmail.settings.basic` | Manage basic mail settings | **Restricted** |
| `https://www.googleapis.com/auth/gmail.settings.sharing` | Manage sensitive mail settings (forwarding, aliases) | **Restricted** |
| `https://mail.google.com/` | **Full access** to Gmail (use sparingly) | **Restricted** |

> **Note:** Most Gmail scopes are classified as **Restricted**, which requires annual CASA security assessments for public apps. See Section 2.6 for verification requirements and costs.

### 2.3 Scope Selection Guide

| What You Want to Do | Minimum Scope Required |
|--------------------|----------------------|
| Read emails | `gmail.readonly` |
| Send emails | `gmail.send` |
| Read AND send emails | `gmail.readonly` + `gmail.send` |
| Manage drafts | `gmail.compose` |
| Delete emails | `gmail.modify` |
| Manage labels | `gmail.labels` or `gmail.modify` |
| Full mailbox control | `mail.google.com/` (avoid if possible) |

### 2.4 Scope Combinations for Common Use Cases

**Read-only access (safest):**
```python
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
```

**Send emails only:**
```python
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
```

**Read and send (most common):**
```python
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
]
```

**Full read/write (excluding permanent delete):**
```python
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
```

**Complete access (use only if absolutely necessary):**
```python
SCOPES = ['https://mail.google.com/']
```

### 2.5 Important Notes About Scopes

1. **Most Gmail scopes are restricted**: Unlike other Google APIs, most Gmail scopes require security assessments. See Section 2.6 for details.

2. **More scopes = more friction**: Users are more likely to deny access if your app requests too many permissions.

3. **Scopes cannot be reduced without re-authentication**: If you later need fewer scopes, users must re-authenticate.

4. **Scopes can be incrementally added**: You can request additional scopes later if needed (users will see a new consent screen).

5. **Test user limitation**: During testing status, only added test users can authenticate (max 100 users).

### 2.6 CASA Security Assessment Requirements

Apps that use **restricted scopes** (which includes most Gmail scopes) and are intended for public use must complete Google's Cloud Application Security Assessment (CASA).

#### 2.6.1 What is CASA?

CASA is Google's security audit framework for cloud applications that handle sensitive user data. It's built on the OWASP ASVS (Application Security Verification Standard) and uses risk-based, multi-tier testing.

#### 2.6.2 When is CASA Required?

| Scenario | CASA Required? |
|----------|---------------|
| Personal use only | No |
| Development/testing/staging | No |
| Internal use within organization | No |
| Domain-wide installation (Workspace) | No |
| Public app with restricted scopes | **Yes** |
| Public app with only sensitive scopes | No (verification only) |
| Public app with only non-sensitive scopes | No (basic verification) |

#### 2.6.3 CASA Assessment Tiers and Costs

| Tier | Description | Typical Cost |
|------|-------------|--------------|
| Tier 1 | Self-assessment questionnaire | Free |
| Tier 2 | Light security audit | $500 - $1,000/year |
| Tier 3 | Comprehensive security assessment | $4,500+/year |

> **Note:** Costs are estimates and vary by assessor. CASA assessments must be renewed annually.

#### 2.6.4 CASA Assessment Process

1. **Submit for verification**: Complete OAuth app verification in Google Cloud Console
2. **Receive tier assignment**: Google assigns a tier based on your app's scope and risk profile
3. **Select an assessor**: Choose from Google's list of approved security assessors
4. **Complete assessment**: Work with the assessor to complete the required testing
5. **Submit results**: Assessor submits results to Google
6. **Approval**: Google reviews and approves (or requests remediation)
7. **Annual renewal**: Repeat assessment annually

#### 2.6.5 Avoiding CASA Requirements

If you want to avoid the CASA process, consider these alternatives:

| Alternative | Trade-off |
|-------------|-----------|
| Use `gmail.send` only | Limited to sending; cannot read emails |
| Use `gmail.labels` only | Can only manage labels |
| Keep app internal | Only available to your organization |
| Use for personal testing only | Limited to 100 test users |

For more information, see [Restricted Scope Verification](https://developers.google.com/identity/protocols/oauth2/production-readiness/restricted-scope-verification) and [CASA Security Assessment](https://support.google.com/cloud/answer/13464325).

---

## Sources

### Gmail API Documentation
- [Gmail API Documentation](https://developers.google.com/workspace/gmail/api)
- [Gmail API Reference](https://developers.google.com/workspace/gmail/api/reference/rest)
- [Gmail API Authentication Overview](https://developers.google.com/workspace/gmail/api/auth/about-auth)
- [Choose Gmail API Scopes](https://developers.google.com/workspace/gmail/api/auth/scopes)

### OAuth 2.0 and Authentication
- [Using OAuth 2.0 to Access Google APIs](https://developers.google.com/identity/protocols/oauth2)
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
- [Configure OAuth Consent Screen](https://developers.google.com/workspace/guides/configure-oauth-consent)
- [OAuth Branding Management](https://support.google.com/cloud/answer/15549049)
- [Create Access Credentials](https://developers.google.com/workspace/guides/create-credentials)
- [Setting up OAuth 2.0](https://support.google.com/cloud/answer/6158849)

### Verification and Security Assessment
- [OAuth App Verification](https://support.google.com/cloud/answer/13463073)
- [Sensitive Scope Verification](https://developers.google.com/identity/protocols/oauth2/production-readiness/sensitive-scope-verification)
- [Restricted Scope Verification](https://developers.google.com/identity/protocols/oauth2/production-readiness/restricted-scope-verification)
- [CASA Security Assessment](https://support.google.com/cloud/answer/13464325)
- [Unverified Apps](https://support.google.com/cloud/answer/7454865)

### Service Accounts (for Google Workspace)
- [Understanding Service Accounts](https://cloud.google.com/iam/docs/service-accounts)
- [Domain-Wide Delegation](https://developers.google.com/workspace/guides/create-credentials#service-account)

### Google Cloud CLI and APIs
- [Google Cloud SDK Installation](https://cloud.google.com/sdk/docs/install)
- [gcloud services enable Reference](https://cloud.google.com/sdk/gcloud/reference/services/enable)
- [Enable and Disable Services](https://cloud.google.com/service-usage/docs/enable-disable)
- [Enable Google Workspace APIs](https://developers.google.com/workspace/guides/enable-apis)

### Identity-Aware Proxy (IAP)
- [Identity-Aware Proxy Overview](https://cloud.google.com/iap/docs/concepts-overview)
- [IAP Product Page](https://cloud.google.com/security/products/iap)
- [IAP TCP Forwarding](https://cloud.google.com/iap/docs/using-tcp-forwarding)
- [Programmatic OAuth Clients for IAP](https://cloud.google.com/iap/docs/programmatic-oauth-clients)

### CLI Limitations and Automation
- [Google Issue Tracker #35907249 - OAuth CLI Support](https://issuetracker.google.com/issues/35907249)
- [Terraform google_iap_brand Resource](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/iap_brand)

### Client Libraries
- [Google API Python Client](https://github.com/googleapis/google-api-python-client)

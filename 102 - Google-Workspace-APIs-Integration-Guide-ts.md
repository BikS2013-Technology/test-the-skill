# Google Workspace APIs Integration Guide (TypeScript)

This guide provides comprehensive instructions for programmatically accessing Google Drive, Docs, Sheets, and Slides using TypeScript/Node.js. It covers file management, document operations, permissions management, and organization workflows.

> **Prerequisites:** Before using this guide, complete the OAuth setup in [Part 1: OAuth Setup](./101%20-%20Gmail-API-Integration-Guide-OAuth%20part.md), which covers creating a Google Cloud project, configuring the OAuth consent screen, and creating credentials.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Google Drive API](#2-google-drive-api)
   - [File Operations (List, Create, Update, Delete)](#21-file-operations)
   - [Search and Query](#22-search-and-query)
   - [Folder Management](#23-folder-management)
   - [Move and Organize Files](#24-move-and-organize-files)
   - [Permissions Management](#25-permissions-management)
3. [Google Docs API](#3-google-docs-api)
   - [Create Documents](#31-create-documents)
   - [Read Document Content](#32-read-document-content)
   - [Update Documents](#33-update-documents)
   - [Search Within Documents](#34-search-within-documents)
4. [Google Sheets API](#4-google-sheets-api)
   - [Create Spreadsheets](#41-create-spreadsheets)
   - [Read Data](#42-read-data)
   - [Update Data](#43-update-data)
   - [Search and Query Data](#44-search-and-query-data)
5. [Google Slides API](#5-google-slides-api)
   - [Create Presentations](#51-create-presentations)
   - [Read Presentations](#52-read-presentations)
   - [Update Presentations](#53-update-presentations)
6. [TypeScript Implementation](#6-typescript-implementation)
7. [Error Handling and Best Practices](#7-error-handling-and-best-practices)
8. [Quick Reference](#8-quick-reference)
9. [Sources](#sources)

---

## 1. Prerequisites

### 1.1 Enable Required APIs

Enable the following APIs in your Google Cloud Console:

| API | Purpose |
|-----|---------|
| Google Drive API | File management, permissions, organization |
| Google Docs API | Document creation and manipulation |
| Google Sheets API | Spreadsheet operations |
| Google Slides API | Presentation management |

```bash
# Using gcloud CLI (if available)
gcloud services enable drive.googleapis.com
gcloud services enable docs.googleapis.com
gcloud services enable sheets.googleapis.com
gcloud services enable slides.googleapis.com
```

### 1.2 Required Scopes

Select scopes based on your needs:

| Scope | Access Level | Use Case |
|-------|--------------|----------|
| `https://www.googleapis.com/auth/drive` | Full Drive access | Complete file management |
| `https://www.googleapis.com/auth/drive.file` | Files created/opened by app | Limited, app-specific access |
| `https://www.googleapis.com/auth/drive.readonly` | Read-only Drive access | Viewing and listing only |
| `https://www.googleapis.com/auth/drive.metadata.readonly` | Metadata only | File info without content |
| `https://www.googleapis.com/auth/documents` | Full Docs access | Create/edit documents |
| `https://www.googleapis.com/auth/documents.readonly` | Read-only Docs | View documents |
| `https://www.googleapis.com/auth/spreadsheets` | Full Sheets access | Create/edit spreadsheets |
| `https://www.googleapis.com/auth/spreadsheets.readonly` | Read-only Sheets | View spreadsheets |
| `https://www.googleapis.com/auth/presentations` | Full Slides access | Create/edit presentations |
| `https://www.googleapis.com/auth/presentations.readonly` | Read-only Slides | View presentations |

### 1.3 MIME Types Reference

| File Type | MIME Type |
|-----------|-----------|
| Google Doc | `application/vnd.google-apps.document` |
| Google Sheet | `application/vnd.google-apps.spreadsheet` |
| Google Slides | `application/vnd.google-apps.presentation` |
| Folder | `application/vnd.google-apps.folder` |
| PDF | `application/pdf` |
| Plain Text | `text/plain` |
| Microsoft Word | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| Microsoft Excel | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |
| Microsoft PowerPoint | `application/vnd.openxmlformats-officedocument.presentationml.presentation` |

---

## 2. Google Drive API

The Google Drive API v3 provides comprehensive file management capabilities.

### 2.1 File Operations

#### List Files

```typescript
// TypeScript - List files
import { drive_v3 } from 'googleapis';

/**
 * List files in Google Drive.
 *
 * @param service - Drive API service instance
 * @param pageSize - Maximum files per page (max 1000)
 * @param query - Optional search query string
 * @param maxResults - Maximum total results to return (default 100, 0 for unlimited)
 * @returns List of file metadata objects
 */
export async function listFiles(
  service: drive_v3.Drive,
  pageSize: number = 100,
  query?: string,
  maxResults: number = 100
): Promise<drive_v3.Schema$File[]> {
  const files: drive_v3.Schema$File[] = [];
  let pageToken: string | undefined;
  // Optimize page size based on maxResults to avoid fetching more than needed
  const effectivePageSize = maxResults > 0 ? Math.min(pageSize, maxResults) : pageSize;

  while (true) {
    const params: drive_v3.Params$Resource$Files$List = {
      pageSize: effectivePageSize,
      fields: 'nextPageToken, files(id, name, mimeType, parents, createdTime, modifiedTime, owners, permissions)',
      supportsAllDrives: true,
    };

    if (query) {
      params.q = query;
    }
    if (pageToken) {
      params.pageToken = pageToken;
    }

    const response = await service.files.list(params);
    files.push(...(response.data.files || []));

    // Check if we've reached maxResults limit
    if (maxResults > 0 && files.length >= maxResults) {
      return files.slice(0, maxResults);
    }

    pageToken = response.data.nextPageToken ?? undefined;
    if (!pageToken) {
      break;
    }
  }

  return files;
}
```

#### Create File/Folder

```typescript
// TypeScript - Create a folder
import { drive_v3 } from 'googleapis';

/**
 * Create a folder in Google Drive.
 *
 * @param service - Drive API service instance
 * @param name - Folder name
 * @param parentId - Optional parent folder ID
 * @returns Created folder metadata
 */
export async function createFolder(
  service: drive_v3.Drive,
  name: string,
  parentId?: string
): Promise<drive_v3.Schema$File> {
  const fileMetadata: drive_v3.Schema$File = {
    name,
    mimeType: 'application/vnd.google-apps.folder',
  };

  if (parentId) {
    fileMetadata.parents = [parentId];
  }

  const response = await service.files.create({
    requestBody: fileMetadata,
    fields: 'id, name, webViewLink',
  });

  return response.data;
}


// TypeScript - Upload a file
import * as fs from 'fs';
import * as path from 'path';

/**
 * Upload a file to Google Drive.
 *
 * @param service - Drive API service instance
 * @param filePath - Local path to the file
 * @param name - Optional name (defaults to filename)
 * @param parentId - Optional parent folder ID
 * @param mimeType - Optional MIME type
 * @returns Uploaded file metadata
 */
export async function uploadFile(
  service: drive_v3.Drive,
  filePath: string,
  name?: string,
  parentId?: string,
  mimeType?: string
): Promise<drive_v3.Schema$File> {
  const fileName = name ?? path.basename(filePath);

  const fileMetadata: drive_v3.Schema$File = { name: fileName };

  if (parentId) {
    fileMetadata.parents = [parentId];
  }

  const media = {
    mimeType: mimeType,
    body: fs.createReadStream(filePath),
  };

  const response = await service.files.create({
    requestBody: fileMetadata,
    media,
    fields: 'id, name, webViewLink',
  });

  return response.data;
}
```

#### Update File Metadata

```typescript
// TypeScript - Update file metadata
import { drive_v3 } from 'googleapis';

/**
 * Update a file's metadata.
 *
 * @param service - Drive API service instance
 * @param fileId - ID of the file to update
 * @param newName - Optional new name
 * @param description - Optional description
 * @returns Updated file metadata
 */
export async function updateFileMetadata(
  service: drive_v3.Drive,
  fileId: string,
  newName?: string,
  description?: string
): Promise<drive_v3.Schema$File> {
  const fileMetadata: drive_v3.Schema$File = {};

  if (newName) {
    fileMetadata.name = newName;
  }
  if (description) {
    fileMetadata.description = description;
  }

  const response = await service.files.update({
    fileId,
    requestBody: fileMetadata,
    fields: 'id, name, description',
  });

  return response.data;
}
```

#### Delete File

```typescript
// TypeScript - Delete a file (move to trash or permanently delete)
import { drive_v3 } from 'googleapis';

/**
 * Delete a file from Google Drive.
 *
 * @param service - Drive API service instance
 * @param fileId - ID of the file to delete
 * @param permanent - If true, permanently delete; otherwise move to trash
 */
export async function deleteFile(
  service: drive_v3.Drive,
  fileId: string,
  permanent: boolean = false
): Promise<void> {
  if (permanent) {
    await service.files.delete({ fileId });
  } else {
    // Move to trash
    await service.files.update({
      fileId,
      requestBody: { trashed: true },
    });
  }
}

/**
 * Restore a file from trash.
 */
export async function restoreFromTrash(
  service: drive_v3.Drive,
  fileId: string
): Promise<void> {
  await service.files.update({
    fileId,
    requestBody: { trashed: false },
  });
}
```

### 2.2 Search and Query

The Drive API supports powerful search queries using the `q` parameter.

#### Query Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equals | `name = 'Report.pdf'` |
| `!=` | Not equals | `mimeType != 'application/vnd.google-apps.folder'` |
| `contains` | Contains (prefix match for name) | `name contains 'Budget'` |
| `in` | Value in collection | `'user@example.com' in owners` |
| `and` | Logical AND | `name contains 'Q1' and mimeType = 'application/pdf'` |
| `or` | Logical OR | `name contains 'report' or name contains 'summary'` |
| `not` | Logical NOT | `not name contains 'draft'` |

#### Common Query Fields

| Field | Description | Example |
|-------|-------------|---------|
| `name` | File name | `name = 'MyDocument'` |
| `fullText` | Full text content search | `fullText contains 'quarterly sales'` |
| `mimeType` | File MIME type | `mimeType = 'application/vnd.google-apps.document'` |
| `trashed` | In trash | `trashed = false` |
| `starred` | Starred files | `starred = true` |
| `parents` | Parent folder ID | `'folder_id' in parents` |
| `owners` | File owner | `'user@example.com' in owners` |
| `writers` | Users with write access | `'user@example.com' in writers` |
| `readers` | Users with read access | `'user@example.com' in readers` |
| `sharedWithMe` | Shared with current user | `sharedWithMe = true` |
| `createdTime` | Creation timestamp | `createdTime > '2024-01-01T00:00:00'` |
| `modifiedTime` | Last modified timestamp | `modifiedTime > '2024-06-01T00:00:00'` |
| `viewedByMeTime` | Last viewed by user | `viewedByMeTime > '2024-01-01T00:00:00'` |

#### Search Examples

```typescript
// TypeScript - Search functions
import { drive_v3 } from 'googleapis';

/**
 * Search for files using a query string.
 *
 * @param service - Drive API service instance
 * @param query - Search query string
 * @param maxResults - Maximum total results to return (default: 100)
 * @returns List of matching files
 */
export async function searchFiles(
  service: drive_v3.Drive,
  query: string,
  maxResults: number = 100
): Promise<drive_v3.Schema$File[]> {
  return listFiles(service, maxResults, query, maxResults);
}


/**
 * Find Google Docs containing a specific name.
 */
export async function findDocsByName(
  service: drive_v3.Drive,
  nameContains: string
): Promise<drive_v3.Schema$File[]> {
  const query = `name contains '${nameContains}' and mimeType = 'application/vnd.google-apps.document' and trashed = false`;
  return searchFiles(service, query);
}


/**
 * Find Google Sheets containing a specific name.
 */
export async function findSheetsByName(
  service: drive_v3.Drive,
  nameContains: string
): Promise<drive_v3.Schema$File[]> {
  const query = `name contains '${nameContains}' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false`;
  return searchFiles(service, query);
}


/**
 * Find Google Slides containing a specific name.
 */
export async function findSlidesByName(
  service: drive_v3.Drive,
  nameContains: string
): Promise<drive_v3.Schema$File[]> {
  const query = `name contains '${nameContains}' and mimeType = 'application/vnd.google-apps.presentation' and trashed = false`;
  return searchFiles(service, query);
}


/**
 * Find all files in a specific folder.
 */
export async function findFilesInFolder(
  service: drive_v3.Drive,
  folderId: string
): Promise<drive_v3.Schema$File[]> {
  const query = `'${folderId}' in parents and trashed = false`;
  return searchFiles(service, query);
}


/**
 * Find files owned by a specific user.
 */
export async function findFilesByOwner(
  service: drive_v3.Drive,
  ownerEmail: string
): Promise<drive_v3.Schema$File[]> {
  const query = `'${ownerEmail}' in owners and trashed = false`;
  return searchFiles(service, query);
}


/**
 * Find files shared with the current user.
 */
export async function findSharedWithMe(
  service: drive_v3.Drive
): Promise<drive_v3.Schema$File[]> {
  const query = "sharedWithMe = true and trashed = false";
  return searchFiles(service, query);
}


/**
 * Find files modified in the last N days.
 */
export async function findRecentFiles(
  service: drive_v3.Drive,
  days: number = 7
): Promise<drive_v3.Schema$File[]> {
  const cutoff = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();
  const query = `modifiedTime > '${cutoff}' and trashed = false`;
  return searchFiles(service, query);
}


/**
 * Search file contents for specific text.
 */
export async function fullTextSearch(
  service: drive_v3.Drive,
  searchText: string
): Promise<drive_v3.Schema$File[]> {
  const query = `fullText contains '${searchText}' and trashed = false`;
  return searchFiles(service, query);
}


/**
 * Find all folders.
 */
export async function findAllFolders(
  service: drive_v3.Drive
): Promise<drive_v3.Schema$File[]> {
  const query = "mimeType = 'application/vnd.google-apps.folder' and trashed = false";
  return searchFiles(service, query);
}
```

### 2.3 Folder Management

```typescript
// TypeScript - Folder management functions
import { drive_v3 } from 'googleapis';

/**
 * Get all contents of a folder.
 *
 * @param service - Drive API service instance
 * @param folderId - ID of the folder
 * @param includeSubfolders - If true, recursively get subfolder contents
 * @returns List of files and folders
 */
export async function getFolderContents(
  service: drive_v3.Drive,
  folderId: string,
  includeSubfolders: boolean = false
): Promise<drive_v3.Schema$File[]> {
  const query = `'${folderId}' in parents and trashed = false`;
  const contents = await searchFiles(service, query);

  if (includeSubfolders) {
    const folders = contents.filter(
      f => f.mimeType === 'application/vnd.google-apps.folder'
    );
    for (const folder of folders) {
      if (folder.id) {
        const subfolderContents = await getFolderContents(service, folder.id, true);
        contents.push(...subfolderContents);
      }
    }
  }

  return contents;
}


export interface FolderTreeNode {
  id: string;
  name: string;
  type: 'folder' | 'file';
  mimeType?: string;
  children?: FolderTreeNode[];
}

/**
 * Get a hierarchical view of folder structure.
 *
 * @param service - Drive API service instance
 * @param folderId - ID of the root folder
 * @param depth - Current depth (for recursion)
 * @param maxDepth - Maximum recursion depth
 * @returns Dictionary with folder tree structure
 */
export async function getFolderTree(
  service: drive_v3.Drive,
  folderId: string,
  depth: number = 0,
  maxDepth: number = 10
): Promise<FolderTreeNode | null> {
  if (depth > maxDepth) {
    return null;
  }

  const folderInfo = await service.files.get({
    fileId: folderId,
    fields: 'id, name',
  });

  const query = `'${folderId}' in parents and trashed = false`;
  const contents = await searchFiles(service, query);

  const tree: FolderTreeNode = {
    id: folderInfo.data.id!,
    name: folderInfo.data.name!,
    type: 'folder',
    children: [],
  };

  for (const item of contents) {
    if (item.mimeType === 'application/vnd.google-apps.folder' && item.id) {
      const subtree = await getFolderTree(service, item.id, depth + 1, maxDepth);
      if (subtree) {
        tree.children!.push(subtree);
      }
    } else {
      tree.children!.push({
        id: item.id!,
        name: item.name!,
        type: 'file',
        mimeType: item.mimeType ?? undefined,
      });
    }
  }

  return tree;
}


/**
 * Create a folder path, creating intermediate folders as needed.
 *
 * @param service - Drive API service instance
 * @param folderPath - Folder path like 'Projects/2024/Q1'
 * @param rootId - Optional root folder ID
 * @returns ID of the final folder in the path
 */
export async function createFolderPath(
  service: drive_v3.Drive,
  folderPath: string,
  rootId?: string
): Promise<string> {
  const folders = folderPath.replace(/^\/|\/$/g, '').split('/');
  let parentId = rootId;

  for (const folderName of folders) {
    // Check if folder exists
    let query = `name = '${folderName}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false`;
    if (parentId) {
      query += ` and '${parentId}' in parents`;
    }

    const results = await searchFiles(service, query, 1);

    if (results.length > 0) {
      parentId = results[0].id!;
    } else {
      // Create the folder
      const newFolder = await createFolder(service, folderName, parentId);
      parentId = newFolder.id!;
    }
  }

  return parentId!;
}
```

### 2.4 Move and Organize Files

```typescript
// TypeScript - Move and organize functions
import { drive_v3 } from 'googleapis';

/**
 * Move a file to a different folder.
 *
 * @param service - Drive API service instance
 * @param fileId - ID of the file to move
 * @param newParentId - ID of the destination folder
 * @param removeFromCurrent - If true, remove from current parent(s)
 * @returns Updated file metadata
 */
export async function moveFile(
  service: drive_v3.Drive,
  fileId: string,
  newParentId: string,
  removeFromCurrent: boolean = true
): Promise<drive_v3.Schema$File> {
  // Get current parents
  const file = await service.files.get({
    fileId,
    fields: 'parents',
  });

  const previousParents = (file.data.parents || []).join(',');

  // Move the file
  const response = await service.files.update({
    fileId,
    addParents: newParentId,
    removeParents: removeFromCurrent ? previousParents : undefined,
    fields: 'id, name, parents',
  });

  return response.data;
}


/**
 * Copy a file.
 *
 * @param service - Drive API service instance
 * @param fileId - ID of the file to copy
 * @param newName - Optional new name for the copy
 * @param destinationFolderId - Optional destination folder
 * @returns Copied file metadata
 */
export async function copyFile(
  service: drive_v3.Drive,
  fileId: string,
  newName?: string,
  destinationFolderId?: string
): Promise<drive_v3.Schema$File> {
  const copyMetadata: drive_v3.Schema$File = {};

  if (newName) {
    copyMetadata.name = newName;
  }
  if (destinationFolderId) {
    copyMetadata.parents = [destinationFolderId];
  }

  const response = await service.files.copy({
    fileId,
    requestBody: copyMetadata,
    fields: 'id, name, webViewLink',
  });

  return response.data;
}


/**
 * Add a file to an additional folder (create shortcut).
 *
 * @param service - Drive API service instance
 * @param fileId - ID of the file
 * @param folderId - ID of the folder to add to
 * @returns Updated file metadata
 */
export async function addToFolder(
  service: drive_v3.Drive,
  fileId: string,
  folderId: string
): Promise<drive_v3.Schema$File> {
  const response = await service.files.update({
    fileId,
    addParents: folderId,
    fields: 'id, name, parents',
  });

  return response.data;
}


/**
 * Organize files in a folder by type into subfolders.
 *
 * @param service - Drive API service instance
 * @param sourceFolderId - ID of the source folder
 * @returns Dictionary mapping types to created folder IDs
 */
export async function organizeFilesByType(
  service: drive_v3.Drive,
  sourceFolderId: string
): Promise<Record<string, string>> {
  const typeFolders: Record<string, string> = {
    'application/vnd.google-apps.document': 'Documents',
    'application/vnd.google-apps.spreadsheet': 'Spreadsheets',
    'application/vnd.google-apps.presentation': 'Presentations',
    'application/pdf': 'PDFs',
    'image/': 'Images',
  };

  const createdFolders: Record<string, string> = {};
  const contents = await findFilesInFolder(service, sourceFolderId);

  for (const file of contents) {
    if (file.mimeType === 'application/vnd.google-apps.folder') {
      continue;
    }

    // Determine target folder
    let targetFolderName = 'Other';
    for (const [mimePrefix, folderName] of Object.entries(typeFolders)) {
      if (file.mimeType?.startsWith(mimePrefix)) {
        targetFolderName = folderName;
        break;
      }
    }

    // Create or get target folder
    if (!(targetFolderName in createdFolders)) {
      const folder = await createFolder(service, targetFolderName, sourceFolderId);
      createdFolders[targetFolderName] = folder.id!;
    }

    // Move file to target folder
    await moveFile(service, file.id!, createdFolders[targetFolderName]);
  }

  return createdFolders;
}
```

### 2.5 Permissions Management

#### Permission Roles

| Role | Description |
|------|-------------|
| `owner` | Full ownership (can delete, transfer ownership) |
| `organizer` | Shared drive organizer (manage members, content) |
| `fileOrganizer` | Can organize files in shared drive |
| `writer` | Can edit and share |
| `commenter` | Can view and comment |
| `reader` | View only |

#### Permission Types

| Type | Description |
|------|-------------|
| `user` | Specific user (requires emailAddress) |
| `group` | Google Group (requires emailAddress) |
| `domain` | Entire domain (requires domain) |
| `anyone` | Anyone with the link |

```typescript
// TypeScript - Permissions management functions
import { drive_v3 } from 'googleapis';

/**
 * List all permissions for a file.
 *
 * @param service - Drive API service instance
 * @param fileId - ID of the file
 * @returns List of permission objects
 */
export async function listPermissions(
  service: drive_v3.Drive,
  fileId: string
): Promise<drive_v3.Schema$Permission[]> {
  const response = await service.permissions.list({
    fileId,
    fields: 'permissions(id, type, role, emailAddress, domain, displayName, expirationTime, deleted)',
  });

  return response.data.permissions || [];
}


/**
 * Get detailed information about a specific permission.
 *
 * @param service - Drive API service instance
 * @param fileId - ID of the file
 * @param permissionId - ID of the permission
 * @returns Permission details
 */
export async function getPermissionDetails(
  service: drive_v3.Drive,
  fileId: string,
  permissionId: string
): Promise<drive_v3.Schema$Permission> {
  const response = await service.permissions.get({
    fileId,
    permissionId,
    fields: '*',
  });

  return response.data;
}


/**
 * Share a file with a specific user.
 *
 * @param service - Drive API service instance
 * @param fileId - ID of the file to share
 * @param email - Email address of the user
 * @param role - Permission role ('reader', 'commenter', 'writer')
 * @param sendNotification - Send email notification
 * @param message - Optional message in notification
 * @returns Created permission
 */
export async function shareWithUser(
  service: drive_v3.Drive,
  fileId: string,
  email: string,
  role: 'reader' | 'commenter' | 'writer' = 'reader',
  sendNotification: boolean = true,
  message?: string
): Promise<drive_v3.Schema$Permission> {
  const permission: drive_v3.Schema$Permission = {
    type: 'user',
    role,
    emailAddress: email,
  };

  const response = await service.permissions.create({
    fileId,
    requestBody: permission,
    sendNotificationEmail: sendNotification,
    emailMessage: message,
    fields: 'id, type, role, emailAddress',
  });

  return response.data;
}


/**
 * Share a file with a Google Group.
 *
 * @param service - Drive API service instance
 * @param fileId - ID of the file
 * @param groupEmail - Email address of the Google Group
 * @param role - Permission role
 * @returns Created permission
 */
export async function shareWithGroup(
  service: drive_v3.Drive,
  fileId: string,
  groupEmail: string,
  role: 'reader' | 'commenter' | 'writer' = 'reader'
): Promise<drive_v3.Schema$Permission> {
  const permission: drive_v3.Schema$Permission = {
    type: 'group',
    role,
    emailAddress: groupEmail,
  };

  const response = await service.permissions.create({
    fileId,
    requestBody: permission,
    fields: 'id, type, role, emailAddress',
  });

  return response.data;
}


/**
 * Share a file with an entire domain.
 *
 * @param service - Drive API service instance
 * @param fileId - ID of the file
 * @param domain - Domain name (e.g., 'example.com')
 * @param role - Permission role
 * @returns Created permission
 */
export async function shareWithDomain(
  service: drive_v3.Drive,
  fileId: string,
  domain: string,
  role: 'reader' | 'commenter' | 'writer' = 'reader'
): Promise<drive_v3.Schema$Permission> {
  const permission: drive_v3.Schema$Permission = {
    type: 'domain',
    role,
    domain,
  };

  const response = await service.permissions.create({
    fileId,
    requestBody: permission,
    fields: 'id, type, role, domain',
  });

  return response.data;
}


/**
 * Share a file with anyone who has the link.
 *
 * @param service - Drive API service instance
 * @param fileId - ID of the file
 * @param role - Permission role ('reader' or 'commenter')
 * @returns Created permission
 */
export async function shareWithAnyone(
  service: drive_v3.Drive,
  fileId: string,
  role: 'reader' | 'commenter' = 'reader'
): Promise<drive_v3.Schema$Permission> {
  const permission: drive_v3.Schema$Permission = {
    type: 'anyone',
    role,
  };

  const response = await service.permissions.create({
    fileId,
    requestBody: permission,
    fields: 'id, type, role',
  });

  return response.data;
}


/**
 * Update an existing permission's role.
 *
 * @param service - Drive API service instance
 * @param fileId - ID of the file
 * @param permissionId - ID of the permission to update
 * @param newRole - New role ('reader', 'commenter', 'writer')
 * @returns Updated permission
 */
export async function updatePermission(
  service: drive_v3.Drive,
  fileId: string,
  permissionId: string,
  newRole: 'reader' | 'commenter' | 'writer'
): Promise<drive_v3.Schema$Permission> {
  const response = await service.permissions.update({
    fileId,
    permissionId,
    requestBody: { role: newRole },
    fields: 'id, type, role, emailAddress',
  });

  return response.data;
}


/**
 * Revoke a permission (remove access).
 *
 * @param service - Drive API service instance
 * @param fileId - ID of the file
 * @param permissionId - ID of the permission to revoke
 */
export async function revokePermission(
  service: drive_v3.Drive,
  fileId: string,
  permissionId: string
): Promise<void> {
  await service.permissions.delete({
    fileId,
    permissionId,
  });
}


/**
 * Revoke access for a specific user by email.
 *
 * @param service - Drive API service instance
 * @param fileId - ID of the file
 * @param email - Email address of the user
 * @returns True if access was revoked, false if user had no access
 */
export async function revokeAccessByEmail(
  service: drive_v3.Drive,
  fileId: string,
  email: string
): Promise<boolean> {
  const permissions = await listPermissions(service, fileId);

  for (const perm of permissions) {
    if (perm.emailAddress?.toLowerCase() === email.toLowerCase()) {
      await revokePermission(service, fileId, perm.id!);
      return true;
    }
  }

  return false;
}


/**
 * Transfer ownership of a file to another user.
 *
 * @param service - Drive API service instance
 * @param fileId - ID of the file
 * @param newOwnerEmail - Email of the new owner
 * @returns Updated permission
 *
 * Note:
 *   - The new owner must be in the same domain for Google Workspace
 *   - For personal accounts, ownership transfer may be restricted
 */
export async function transferOwnership(
  service: drive_v3.Drive,
  fileId: string,
  newOwnerEmail: string
): Promise<drive_v3.Schema$Permission> {
  const permission: drive_v3.Schema$Permission = {
    type: 'user',
    role: 'owner',
    emailAddress: newOwnerEmail,
  };

  const response = await service.permissions.create({
    fileId,
    requestBody: permission,
    transferOwnership: true,
    fields: 'id, type, role, emailAddress',
  });

  return response.data;
}


/**
 * SharingSummary interface for standalone functions.
 * Note: The DriveManager class (Section 6.3) uses a different SharingSummary
 * interface with 'editors'/'viewers' (user-friendly terms) instead of
 * 'writers'/'readers' (API terms), and includes additional details like
 * domain access roles.
 */
export interface SharingSummary {
  owner: string | null;
  writers: string[];
  commenters: string[];
  readers: string[];
  anyoneWithLink: boolean;
  domainShared: string[];
}

/**
 * Get a summary of who has access to a file.
 *
 * @param service - Drive API service instance
 * @param fileId - ID of the file
 * @returns Dictionary with sharing summary
 */
export async function getSharingSummary(
  service: drive_v3.Drive,
  fileId: string
): Promise<SharingSummary> {
  const permissions = await listPermissions(service, fileId);

  const summary: SharingSummary = {
    owner: null,
    writers: [],
    commenters: [],
    readers: [],
    anyoneWithLink: false,
    domainShared: [],
  };

  for (const perm of permissions) {
    const role = perm.role;
    const permType = perm.type;

    if (role === 'owner') {
      summary.owner = perm.emailAddress || null;
    } else if (role === 'writer') {
      if (permType === 'user') {
        summary.writers.push(perm.emailAddress || '');
      } else if (permType === 'group') {
        summary.writers.push(`group:${perm.emailAddress}`);
      }
    } else if (role === 'commenter') {
      summary.commenters.push(perm.emailAddress || '');
    } else if (role === 'reader') {
      if (permType === 'anyone') {
        summary.anyoneWithLink = true;
      } else if (permType === 'domain') {
        summary.domainShared.push(perm.domain || '');
      } else if (permType === 'user') {
        summary.readers.push(perm.emailAddress || '');
      }
    }
  }

  return summary;
}
```

---

## 3. Google Docs API

The Google Docs API allows you to create and manipulate documents programmatically.

### 3.1 Create Documents

```typescript
// TypeScript - Create documents
import { docs_v1 } from 'googleapis';

/**
 * Create a new Google Document.
 *
 * @param docsService - Docs API service instance
 * @param title - Document title
 * @returns Created document metadata
 */
export async function createDocument(
  docsService: docs_v1.Docs,
  title: string
): Promise<docs_v1.Schema$Document> {
  const response = await docsService.documents.create({
    requestBody: { title },
  });

  return response.data;
}


/**
 * Create a new Google Document with initial content.
 *
 * @param docsService - Docs API service instance
 * @param title - Document title
 * @param content - Initial text content
 * @returns Created document metadata
 */
export async function createDocumentWithContent(
  docsService: docs_v1.Docs,
  title: string,
  content: string
): Promise<docs_v1.Schema$Document> {
  // Create the document
  const document = await createDocument(docsService, title);
  const documentId = document.documentId!;

  // Insert content
  const requests: docs_v1.Schema$Request[] = [
    {
      insertText: {
        location: { index: 1 },
        text: content,
      },
    },
  ];

  await docsService.documents.batchUpdate({
    documentId,
    requestBody: { requests },
  });

  return document;
}


/**
 * Create a document in a specific folder.
 *
 * @param driveService - Drive API service instance
 * @param docsService - Docs API service instance
 * @param title - Document title
 * @param folderId - Parent folder ID
 * @returns Created document metadata
 */
export async function createDocumentInFolder(
  driveService: drive_v3.Drive,
  docsService: docs_v1.Docs,
  title: string,
  folderId: string
): Promise<docs_v1.Schema$Document> {
  // Create the document
  const document = await createDocument(docsService, title);
  const documentId = document.documentId!;

  // Move to folder
  await moveFile(driveService, documentId, folderId);

  return document;
}
```

### 3.2 Read Document Content

```typescript
// TypeScript - Read document content
import { docs_v1 } from 'googleapis';

/**
 * Get a document's full content.
 *
 * @param docsService - Docs API service instance
 * @param documentId - ID of the document
 * @returns Document object with content
 */
export async function getDocument(
  docsService: docs_v1.Docs,
  documentId: string
): Promise<docs_v1.Schema$Document> {
  const response = await docsService.documents.get({
    documentId,
  });

  return response.data;
}


/**
 * Extract plain text from a document.
 *
 * @param docsService - Docs API service instance
 * @param documentId - ID of the document
 * @returns Plain text content of the document
 */
export async function getDocumentText(
  docsService: docs_v1.Docs,
  documentId: string
): Promise<string> {
  const document = await getDocument(docsService, documentId);
  const textContent: string[] = [];

  function extractText(elements: docs_v1.Schema$StructuralElement[]): void {
    for (const element of elements) {
      if (element.paragraph) {
        for (const paraElement of element.paragraph.elements || []) {
          if (paraElement.textRun) {
            textContent.push(paraElement.textRun.content || '');
          }
        }
      } else if (element.table) {
        for (const row of element.table.tableRows || []) {
          for (const cell of row.tableCells || []) {
            extractText(cell.content || []);
          }
        }
      }
    }
  }

  const body = document.body;
  if (body?.content) {
    extractText(body.content);
  }

  return textContent.join('');
}


export interface DocumentSummary {
  title: string | null | undefined;
  documentId: string;
  summary: string;
  totalLength: number;
}

/**
 * Get a summary of document content (first N characters).
 *
 * @param docsService - Docs API service instance
 * @param documentId - ID of the document
 * @param maxChars - Maximum characters to return
 * @returns Dictionary with title and summary
 */
export async function getDocumentSummary(
  docsService: docs_v1.Docs,
  documentId: string,
  maxChars: number = 500
): Promise<DocumentSummary> {
  const document = await getDocument(docsService, documentId);
  const text = await getDocumentText(docsService, documentId);

  let summary = text.slice(0, maxChars).trim();
  if (text.length > maxChars) {
    summary += '...';
  }

  return {
    title: document.title,
    documentId,
    summary,
    totalLength: text.length,
  };
}


export interface HeadingInfo {
  level: string;
  text: string;
}

export interface DocumentStructure {
  title: string | null | undefined;
  headings: HeadingInfo[];
  lists: number;
  tables: number;
  images: number;
}

/**
 * Get the structural elements of a document (headings, lists, tables).
 *
 * @param docsService - Docs API service instance
 * @param documentId - ID of the document
 * @returns Dictionary with document structure
 */
export async function getDocumentStructure(
  docsService: docs_v1.Docs,
  documentId: string
): Promise<DocumentStructure> {
  const document = await getDocument(docsService, documentId);

  const structure: DocumentStructure = {
    title: document.title,
    headings: [],
    lists: 0,
    tables: 0,
    images: 0,
  };

  const body = document.body;

  for (const element of body?.content || []) {
    if (element.paragraph) {
      const paragraph = element.paragraph;
      const style = paragraph.paragraphStyle?.namedStyleType || '';

      if (style.startsWith('HEADING')) {
        let text = '';
        for (const paraElement of paragraph.elements || []) {
          if (paraElement.textRun) {
            text += paraElement.textRun.content || '';
          }
        }

        structure.headings.push({
          level: style,
          text: text.trim(),
        });
      }

      // Check for inline objects (images)
      for (const paraElement of paragraph.elements || []) {
        if (paraElement.inlineObjectElement) {
          structure.images += 1;
        }
      }
    } else if (element.table) {
      structure.tables += 1;
    }
  }

  return structure;
}
```

### 3.3 Update Documents

```typescript
// TypeScript - Update documents
import { docs_v1 } from 'googleapis';

/**
 * Append text to the end of a document.
 *
 * @param docsService - Docs API service instance
 * @param documentId - ID of the document
 * @param text - Text to append
 */
export async function appendText(
  docsService: docs_v1.Docs,
  documentId: string,
  text: string
): Promise<void> {
  // Get the document to find the end index
  const document = await getDocument(docsService, documentId);
  const content = document.body?.content || [];
  const endIndex = content[content.length - 1]?.endIndex || 1;
  const insertIndex = endIndex - 1;

  const requests: docs_v1.Schema$Request[] = [
    {
      insertText: {
        location: { index: insertIndex },
        text,
      },
    },
  ];

  await docsService.documents.batchUpdate({
    documentId,
    requestBody: { requests },
  });
}


/**
 * Insert text at a specific position in the document.
 *
 * @param docsService - Docs API service instance
 * @param documentId - ID of the document
 * @param text - Text to insert
 * @param index - Position to insert at (1-based)
 */
export async function insertTextAtPosition(
  docsService: docs_v1.Docs,
  documentId: string,
  text: string,
  index: number
): Promise<void> {
  const requests: docs_v1.Schema$Request[] = [
    {
      insertText: {
        location: { index },
        text,
      },
    },
  ];

  await docsService.documents.batchUpdate({
    documentId,
    requestBody: { requests },
  });
}


/**
 * Replace all occurrences of text in a document.
 *
 * @param docsService - Docs API service instance
 * @param documentId - ID of the document
 * @param oldText - Text to find
 * @param newText - Replacement text
 * @returns Number of replacements made
 */
export async function replaceText(
  docsService: docs_v1.Docs,
  documentId: string,
  oldText: string,
  newText: string
): Promise<number> {
  const requests: docs_v1.Schema$Request[] = [
    {
      replaceAllText: {
        containsText: {
          text: oldText,
          matchCase: true,
        },
        replaceText: newText,
      },
    },
  ];

  const response = await docsService.documents.batchUpdate({
    documentId,
    requestBody: { requests },
  });

  const replies = response.data.replies || [];
  if (replies.length > 0) {
    return replies[0].replaceAllText?.occurrencesChanged || 0;
  }
  return 0;
}


/**
 * Delete content in a specific range.
 *
 * @param docsService - Docs API service instance
 * @param documentId - ID of the document
 * @param startIndex - Start index (1-based)
 * @param endIndex - End index
 */
export async function deleteContentRange(
  docsService: docs_v1.Docs,
  documentId: string,
  startIndex: number,
  endIndex: number
): Promise<void> {
  const requests: docs_v1.Schema$Request[] = [
    {
      deleteContentRange: {
        range: {
          startIndex,
          endIndex,
        },
      },
    },
  ];

  await docsService.documents.batchUpdate({
    documentId,
    requestBody: { requests },
  });
}


/**
 * Add a heading to the end of the document.
 *
 * @param docsService - Docs API service instance
 * @param documentId - ID of the document
 * @param text - Heading text
 * @param headingLevel - Heading level (1-6)
 */
export async function addHeading(
  docsService: docs_v1.Docs,
  documentId: string,
  text: string,
  headingLevel: 1 | 2 | 3 | 4 | 5 | 6 = 1
): Promise<void> {
  // Get the document to find the end index
  const document = await getDocument(docsService, documentId);
  const content = document.body?.content || [];
  const endIndex = content[content.length - 1]?.endIndex || 1;
  const insertIndex = endIndex - 1;

  const headingStyles: Record<number, string> = {
    1: 'HEADING_1',
    2: 'HEADING_2',
    3: 'HEADING_3',
    4: 'HEADING_4',
    5: 'HEADING_5',
    6: 'HEADING_6',
  };

  const requests: docs_v1.Schema$Request[] = [
    {
      insertText: {
        location: { index: insertIndex },
        text: text + '\n',
      },
    },
    {
      updateParagraphStyle: {
        range: {
          startIndex: insertIndex,
          endIndex: insertIndex + text.length + 1,
        },
        paragraphStyle: {
          namedStyleType: headingStyles[headingLevel],
        },
        fields: 'namedStyleType',
      },
    },
  ];

  await docsService.documents.batchUpdate({
    documentId,
    requestBody: { requests },
  });
}
```

### 3.4 Search Within Documents

```typescript
// TypeScript - Search within documents
import { docs_v1, drive_v3 } from 'googleapis';

export interface TextMatch {
  position: number;
  context: string;
  match: string;
}

/**
 * Search for text within a document.
 *
 * @param docsService - Docs API service instance
 * @param documentId - ID of the document
 * @param searchText - Text to search for
 * @returns List of matches with context
 */
export async function searchInDocument(
  docsService: docs_v1.Docs,
  documentId: string,
  searchText: string
): Promise<TextMatch[]> {
  const text = await getDocumentText(docsService, documentId);

  const matches: TextMatch[] = [];
  const searchLower = searchText.toLowerCase();
  const textLower = text.toLowerCase();

  let start = 0;
  while (true) {
    const index = textLower.indexOf(searchLower, start);
    if (index === -1) {
      break;
    }

    // Get context (50 chars before and after)
    const contextStart = Math.max(0, index - 50);
    const contextEnd = Math.min(text.length, index + searchText.length + 50);

    matches.push({
      position: index,
      context: text.slice(contextStart, contextEnd),
      match: text.slice(index, index + searchText.length),
    });

    start = index + 1;
  }

  return matches;
}


export interface DocumentSearchResult {
  documentId: string;
  name: string;
  matchCount: number;
  matches: TextMatch[];
}

/**
 * Search across multiple documents for specific text.
 *
 * @param driveService - Drive API service instance
 * @param docsService - Docs API service instance
 * @param searchText - Text to search for
 * @param folderId - Optional folder to limit search
 * @returns List of documents containing the text
 */
export async function searchDocumentsForText(
  driveService: drive_v3.Drive,
  docsService: docs_v1.Docs,
  searchText: string,
  folderId?: string
): Promise<DocumentSearchResult[]> {
  // First, use Drive's fullText search for efficiency
  let query = `fullText contains '${searchText}' and mimeType = 'application/vnd.google-apps.document' and trashed = false`;

  if (folderId) {
    query += ` and '${folderId}' in parents`;
  }

  const files = await searchFiles(driveService, query);

  const results: DocumentSearchResult[] = [];
  for (const file of files) {
    try {
      const matches = await searchInDocument(docsService, file.id!, searchText);
      if (matches.length > 0) {
        results.push({
          documentId: file.id!,
          name: file.name!,
          matchCount: matches.length,
          matches: matches.slice(0, 5), // First 5 matches
        });
      }
    } catch (e) {
      console.error(`Error searching ${file.name}: ${e}`);
    }
  }

  return results;
}
```

---

## 4. Google Sheets API

The Google Sheets API v4 provides comprehensive spreadsheet operations.

### 4.1 Create Spreadsheets

```typescript
// TypeScript - Create spreadsheets
import { sheets_v4 } from 'googleapis';

/**
 * Create a new Google Spreadsheet.
 *
 * @param sheetsService - Sheets API service instance
 * @param title - Spreadsheet title
 * @returns Created spreadsheet metadata
 */
export async function createSpreadsheet(
  sheetsService: sheets_v4.Sheets,
  title: string
): Promise<sheets_v4.Schema$Spreadsheet> {
  const spreadsheet: sheets_v4.Schema$Spreadsheet = {
    properties: {
      title,
    },
  };

  const response = await sheetsService.spreadsheets.create({
    requestBody: spreadsheet,
    fields: 'spreadsheetId,spreadsheetUrl',
  });

  return response.data;
}


/**
 * Create a spreadsheet with multiple named sheets.
 *
 * @param sheetsService - Sheets API service instance
 * @param title - Spreadsheet title
 * @param sheetNames - List of sheet names
 * @returns Created spreadsheet metadata
 */
export async function createSpreadsheetWithSheets(
  sheetsService: sheets_v4.Sheets,
  title: string,
  sheetNames: string[]
): Promise<sheets_v4.Schema$Spreadsheet> {
  const sheets: sheets_v4.Schema$Sheet[] = sheetNames.map(name => ({
    properties: { title: name },
  }));

  const spreadsheet: sheets_v4.Schema$Spreadsheet = {
    properties: { title },
    sheets,
  };

  const response = await sheetsService.spreadsheets.create({
    requestBody: spreadsheet,
    fields: 'spreadsheetId,spreadsheetUrl,sheets.properties',
  });

  return response.data;
}


/**
 * Create a spreadsheet and populate it with data.
 *
 * @param sheetsService - Sheets API service instance
 * @param title - Spreadsheet title
 * @param data - 2D array of values
 * @param sheetName - Name of the sheet
 * @returns Created spreadsheet metadata
 */
export async function createSpreadsheetWithData(
  sheetsService: sheets_v4.Sheets,
  title: string,
  data: any[][],
  sheetName: string = 'Sheet1'
): Promise<sheets_v4.Schema$Spreadsheet> {
  // Create the spreadsheet
  const spreadsheet = await createSpreadsheet(sheetsService, title);
  const spreadsheetId = spreadsheet.spreadsheetId!;

  // Write the data
  await writeValues(sheetsService, spreadsheetId, `${sheetName}!A1`, data);

  return spreadsheet;
}
```

### 4.2 Read Data

```typescript
// TypeScript - Read spreadsheet data
import { sheets_v4 } from 'googleapis';

/**
 * Get spreadsheet metadata.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @returns Spreadsheet metadata
 */
export async function getSpreadsheet(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string
): Promise<sheets_v4.Schema$Spreadsheet> {
  const response = await sheetsService.spreadsheets.get({
    spreadsheetId,
  });

  return response.data;
}


/**
 * Read values from a spreadsheet range.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param rangeName - A1 notation range (e.g., 'Sheet1!A1:D10')
 * @returns 2D array of values
 */
export async function readValues(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  rangeName: string
): Promise<any[][]> {
  const response = await sheetsService.spreadsheets.values.get({
    spreadsheetId,
    range: rangeName,
  });

  return response.data.values || [];
}


/**
 * Read all values from a sheet.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param sheetName - Name of the sheet
 * @returns 2D array of all values
 */
export async function readAllValues(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  sheetName: string = 'Sheet1'
): Promise<any[][]> {
  return readValues(sheetsService, spreadsheetId, sheetName);
}


/**
 * Read multiple ranges at once.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param ranges - List of A1 notation ranges
 * @returns Dictionary mapping ranges to values
 */
export async function readMultipleRanges(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  ranges: string[]
): Promise<Record<string, any[][]>> {
  const response = await sheetsService.spreadsheets.values.batchGet({
    spreadsheetId,
    ranges,
  });

  const result: Record<string, any[][]> = {};
  for (const vr of response.data.valueRanges || []) {
    if (vr.range) {
      result[vr.range] = vr.values || [];
    }
  }

  return result;
}


export interface SheetSummary {
  sheetId: number;
  title: string;
  rowCount: number;
  columnCount: number;
}

export interface SpreadsheetSummary {
  title: string | null | undefined;
  spreadsheetId: string;
  url: string | null | undefined;
  sheets: SheetSummary[];
}

/**
 * Get a summary of the spreadsheet.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @returns Dictionary with spreadsheet summary
 */
export async function getSheetSummary(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string
): Promise<SpreadsheetSummary> {
  const spreadsheet = await getSpreadsheet(sheetsService, spreadsheetId);

  const summary: SpreadsheetSummary = {
    title: spreadsheet.properties?.title,
    spreadsheetId,
    url: spreadsheet.spreadsheetUrl,
    sheets: [],
  };

  for (const sheet of spreadsheet.sheets || []) {
    const props = sheet.properties;
    const gridProps = props?.gridProperties;

    summary.sheets.push({
      sheetId: props?.sheetId || 0,
      title: props?.title || '',
      rowCount: gridProps?.rowCount || 0,
      columnCount: gridProps?.columnCount || 0,
    });
  }

  return summary;
}
```

### 4.3 Update Data

```typescript
// TypeScript - Update spreadsheet data
import { sheets_v4 } from 'googleapis';

/**
 * Write values to a spreadsheet range.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param rangeName - A1 notation range
 * @param values - 2D array of values
 * @returns Update result
 */
export async function writeValues(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  rangeName: string,
  values: any[][]
): Promise<sheets_v4.Schema$UpdateValuesResponse> {
  const response = await sheetsService.spreadsheets.values.update({
    spreadsheetId,
    range: rangeName,
    valueInputOption: 'USER_ENTERED',
    requestBody: { values },
  });

  return response.data;
}


/**
 * Append values after the last row of data.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param rangeName - A1 notation range (determines columns)
 * @param values - 2D array of values to append
 * @returns Append result
 */
export async function appendValues(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  rangeName: string,
  values: any[][]
): Promise<sheets_v4.Schema$AppendValuesResponse> {
  const response = await sheetsService.spreadsheets.values.append({
    spreadsheetId,
    range: rangeName,
    valueInputOption: 'USER_ENTERED',
    insertDataOption: 'INSERT_ROWS',
    requestBody: { values },
  });

  return response.data;
}


/**
 * Clear values from a range.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param rangeName - A1 notation range
 */
export async function clearValues(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  rangeName: string
): Promise<void> {
  await sheetsService.spreadsheets.values.clear({
    spreadsheetId,
    range: rangeName,
  });
}


/**
 * Update multiple ranges at once.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param data - Dictionary mapping ranges to values
 * @returns Update result
 */
export async function updateMultipleRanges(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  data: Record<string, any[][]>
): Promise<sheets_v4.Schema$BatchUpdateValuesResponse> {
  const valueRanges: sheets_v4.Schema$ValueRange[] = Object.entries(data).map(
    ([range, values]) => ({ range, values })
  );

  const response = await sheetsService.spreadsheets.values.batchUpdate({
    spreadsheetId,
    requestBody: {
      valueInputOption: 'USER_ENTERED',
      data: valueRanges,
    },
  });

  return response.data;
}


/**
 * Add a new sheet to a spreadsheet.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param sheetName - Name for the new sheet
 * @returns New sheet properties
 */
export async function addSheet(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  sheetName: string
): Promise<sheets_v4.Schema$SheetProperties> {
  const requests: sheets_v4.Schema$Request[] = [
    {
      addSheet: {
        properties: {
          title: sheetName,
        },
      },
    },
  ];

  const response = await sheetsService.spreadsheets.batchUpdate({
    spreadsheetId,
    requestBody: { requests },
  });

  return response.data.replies![0].addSheet!.properties!;
}


/**
 * Delete a sheet from a spreadsheet.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param sheetId - ID of the sheet to delete
 */
export async function deleteSheet(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  sheetId: number
): Promise<void> {
  const requests: sheets_v4.Schema$Request[] = [
    {
      deleteSheet: {
        sheetId,
      },
    },
  ];

  await sheetsService.spreadsheets.batchUpdate({
    spreadsheetId,
    requestBody: { requests },
  });
}
```

### 4.4 Search and Query Data

```typescript
// TypeScript - Search and query spreadsheet data
import { sheets_v4 } from 'googleapis';

export interface CellMatch {
  cell: string;
  row: number;
  column: number;
  value: any;
}

/**
 * Find cells containing specific text.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param searchText - Text to search for
 * @param sheetName - Sheet to search
 * @returns List of matches with cell references
 */
export async function findInSheet(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  searchText: string,
  sheetName: string = 'Sheet1'
): Promise<CellMatch[]> {
  const values = await readAllValues(sheetsService, spreadsheetId, sheetName);

  const matches: CellMatch[] = [];
  const searchLower = searchText.toLowerCase();

  for (let rowIdx = 0; rowIdx < values.length; rowIdx++) {
    const row = values[rowIdx];
    for (let colIdx = 0; colIdx < row.length; colIdx++) {
      const cell = row[colIdx];
      if (String(cell).toLowerCase().includes(searchLower)) {
        const colLetter = colIdx < 26
          ? String.fromCharCode('A'.charCodeAt(0) + colIdx)
          : String.fromCharCode('A'.charCodeAt(0) + Math.floor(colIdx / 26) - 1) +
            String.fromCharCode('A'.charCodeAt(0) + (colIdx % 26));

        matches.push({
          cell: `${colLetter}${rowIdx + 1}`,
          row: rowIdx + 1,
          column: colIdx + 1,
          value: cell,
        });
      }
    }
  }

  return matches;
}


/**
 * Query sheet data with column filters.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param columnFilters - Dict of {column_index: filter_value}
 * @param sheetName - Sheet to query
 * @returns Filtered rows
 */
export async function querySheet(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  columnFilters: Record<number, string>,
  sheetName: string = 'Sheet1'
): Promise<Record<string, any>[]> {
  const values = await readAllValues(sheetsService, spreadsheetId, sheetName);

  if (values.length === 0) {
    return [];
  }

  const headers = values[0] || [];
  const results: Record<string, any>[] = [];

  for (const row of values.slice(1)) {  // Skip header row
    let match = true;
    for (const [colIdx, filterValue] of Object.entries(columnFilters)) {
      const idx = parseInt(colIdx);
      if (idx >= row.length) {
        match = false;
        break;
      }
      if (!String(row[idx]).toLowerCase().includes(filterValue.toLowerCase())) {
        match = false;
        break;
      }
    }

    if (match) {
      const rowObj: Record<string, any> = {};
      headers.forEach((header, i) => {
        rowObj[header] = row[i];
      });
      results.push(rowObj);
    }
  }

  return results;
}


/**
 * Get all values from a specific column.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param column - Column letter (e.g., 'A') or index (0-based)
 * @param sheetName - Sheet name
 * @returns List of column values
 */
export async function getColumnValues(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  column: string | number,
  sheetName: string = 'Sheet1'
): Promise<any[]> {
  let colLetter: string;
  if (typeof column === 'number') {
    colLetter = String.fromCharCode('A'.charCodeAt(0) + column);
  } else {
    colLetter = column;
  }

  const rangeName = `${sheetName}!${colLetter}:${colLetter}`;
  const values = await readValues(sheetsService, spreadsheetId, rangeName);

  return values.map(row => row[0] || '');
}


/**
 * Find a row by a value in a specific column.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param column - Column to search
 * @param value - Value to find
 * @param sheetName - Sheet name
 * @returns Row data as dictionary (with headers) or null
 */
export async function findRowByValue(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  column: string | number,
  value: any,
  sheetName: string = 'Sheet1'
): Promise<Record<string, any> | null> {
  const values = await readAllValues(sheetsService, spreadsheetId, sheetName);

  if (values.length < 2) {
    return null;
  }

  const headers = values[0];

  let colIdx: number;
  if (typeof column === 'string') {
    colIdx = column.toUpperCase().charCodeAt(0) - 'A'.charCodeAt(0);
  } else {
    colIdx = column;
  }

  for (const row of values.slice(1)) {
    if (colIdx < row.length && String(row[colIdx]) === String(value)) {
      const rowObj: Record<string, any> = {};
      headers.forEach((header, i) => {
        rowObj[header] = row[i];
      });
      return rowObj;
    }
  }

  return null;
}
```

---

## 5. Google Slides API

The Google Slides API allows you to create and modify presentations.

### 5.1 Create Presentations

```typescript
// TypeScript - Create presentations
import { slides_v1 } from 'googleapis';

/**
 * Create a new Google Slides presentation.
 *
 * @param slidesService - Slides API service instance
 * @param title - Presentation title
 * @returns Created presentation metadata
 */
export async function createPresentation(
  slidesService: slides_v1.Slides,
  title: string
): Promise<slides_v1.Schema$Presentation> {
  const presentation: slides_v1.Schema$Presentation = {
    title,
  };

  const response = await slidesService.presentations.create({
    requestBody: presentation,
  });

  return response.data;
}


/**
 * Create a presentation with multiple blank slides.
 *
 * @param slidesService - Slides API service instance
 * @param title - Presentation title
 * @param slideCount - Number of slides to create
 * @returns Created presentation
 */
export async function createPresentationWithSlides(
  slidesService: slides_v1.Slides,
  title: string,
  slideCount: number = 5
): Promise<slides_v1.Schema$Presentation> {
  const presentation = await createPresentation(slidesService, title);
  const presentationId = presentation.presentationId!;

  // Add additional slides (first slide is created automatically)
  const requests: slides_v1.Schema$Request[] = [];
  for (let i = 0; i < slideCount - 1; i++) {
    requests.push({
      createSlide: {
        insertionIndex: i + 1,
        slideLayoutReference: {
          predefinedLayout: 'BLANK',
        },
      },
    });
  }

  if (requests.length > 0) {
    await slidesService.presentations.batchUpdate({
      presentationId,
      requestBody: { requests },
    });
  }

  return presentation;
}
```

### 5.2 Read Presentations

```typescript
// TypeScript - Read presentations
import { slides_v1 } from 'googleapis';

/**
 * Get presentation metadata and content.
 *
 * @param slidesService - Slides API service instance
 * @param presentationId - ID of the presentation
 * @returns Presentation object
 */
export async function getPresentation(
  slidesService: slides_v1.Slides,
  presentationId: string
): Promise<slides_v1.Schema$Presentation> {
  const response = await slidesService.presentations.get({
    presentationId,
  });

  return response.data;
}


export interface SlideInfo {
  slideNumber: number;
  objectId: string;
  textContent: string[];
}

export interface PresentationSummary {
  title: string | null | undefined;
  presentationId: string;
  slideCount: number;
  slides: SlideInfo[];
}

/**
 * Get a summary of the presentation.
 *
 * @param slidesService - Slides API service instance
 * @param presentationId - ID of the presentation
 * @returns Dictionary with presentation summary
 */
export async function getPresentationSummary(
  slidesService: slides_v1.Slides,
  presentationId: string
): Promise<PresentationSummary> {
  const presentation = await getPresentation(slidesService, presentationId);

  const summary: PresentationSummary = {
    title: presentation.title,
    presentationId,
    slideCount: presentation.slides?.length || 0,
    slides: [],
  };

  for (let idx = 0; idx < (presentation.slides || []).length; idx++) {
    const slide = presentation.slides![idx];
    const slideInfo: SlideInfo = {
      slideNumber: idx + 1,
      objectId: slide.objectId!,
      textContent: [],
    };

    // Extract text from slide elements
    for (const element of slide.pageElements || []) {
      if (element.shape?.text) {
        const textElements = element.shape.text.textElements || [];
        for (const textEl of textElements) {
          if (textEl.textRun) {
            const content = (textEl.textRun.content || '').trim();
            if (content) {
              slideInfo.textContent.push(content);
            }
          }
        }
      }
    }

    summary.slides.push(slideInfo);
  }

  return summary;
}


/**
 * Get all text content from a specific slide.
 *
 * @param slidesService - Slides API service instance
 * @param presentationId - ID of the presentation
 * @param slideIndex - Index of the slide (0-based)
 * @returns List of text strings from the slide
 */
export async function getSlideText(
  slidesService: slides_v1.Slides,
  presentationId: string,
  slideIndex: number = 0
): Promise<string[]> {
  const presentation = await getPresentation(slidesService, presentationId);
  const slides = presentation.slides || [];

  if (slideIndex >= slides.length) {
    return [];
  }

  const slide = slides[slideIndex];
  const textContent: string[] = [];

  for (const element of slide.pageElements || []) {
    if (element.shape?.text) {
      const textElements = element.shape.text.textElements || [];
      for (const textEl of textElements) {
        if (textEl.textRun) {
          const content = (textEl.textRun.content || '').trim();
          if (content) {
            textContent.push(content);
          }
        }
      }
    }
  }

  return textContent;
}


/**
 * Get all text content from the entire presentation.
 *
 * @param slidesService - Slides API service instance
 * @param presentationId - ID of the presentation
 * @returns Dictionary mapping slide numbers to text content
 */
export async function getAllPresentationText(
  slidesService: slides_v1.Slides,
  presentationId: string
): Promise<Record<number, string[]>> {
  const presentation = await getPresentation(slidesService, presentationId);
  const allText: Record<number, string[]> = {};

  for (let idx = 0; idx < (presentation.slides || []).length; idx++) {
    const slide = presentation.slides![idx];
    const slideText: string[] = [];

    for (const element of slide.pageElements || []) {
      if (element.shape?.text) {
        const textElements = element.shape.text.textElements || [];
        for (const textEl of textElements) {
          if (textEl.textRun) {
            const content = (textEl.textRun.content || '').trim();
            if (content) {
              slideText.push(content);
            }
          }
        }
      }
    }

    allText[idx + 1] = slideText;
  }

  return allText;
}
```

### 5.3 Update Presentations

```typescript
// TypeScript - Update presentations
import { slides_v1 } from 'googleapis';
import { v4 as uuidv4 } from 'uuid';

export type PredefinedLayout = 'BLANK' | 'TITLE' | 'TITLE_AND_BODY' | 'TITLE_AND_TWO_COLUMNS' | 'TITLE_ONLY' | 'SECTION_HEADER' | 'SECTION_TITLE_AND_DESCRIPTION' | 'ONE_COLUMN_TEXT' | 'MAIN_POINT' | 'BIG_NUMBER';

/**
 * Add a new slide to the presentation.
 *
 * @param slidesService - Slides API service instance
 * @param presentationId - ID of the presentation
 * @param layout - Slide layout (BLANK, TITLE, TITLE_AND_BODY, etc.)
 * @param insertionIndex - Position to insert (undefined = end)
 * @returns Created slide info
 */
export async function addSlide(
  slidesService: slides_v1.Slides,
  presentationId: string,
  layout: PredefinedLayout = 'BLANK',
  insertionIndex?: number
): Promise<slides_v1.Schema$CreateSlideResponse> {
  const request: slides_v1.Schema$Request = {
    createSlide: {
      slideLayoutReference: {
        predefinedLayout: layout,
      },
    },
  };

  if (insertionIndex !== undefined) {
    request.createSlide!.insertionIndex = insertionIndex;
  }

  const response = await slidesService.presentations.batchUpdate({
    presentationId,
    requestBody: { requests: [request] },
  });

  return response.data.replies![0].createSlide!;
}


/**
 * Delete a slide from the presentation.
 *
 * @param slidesService - Slides API service instance
 * @param presentationId - ID of the presentation
 * @param slideObjectId - Object ID of the slide to delete
 */
export async function deleteSlide(
  slidesService: slides_v1.Slides,
  presentationId: string,
  slideObjectId: string
): Promise<void> {
  const requests: slides_v1.Schema$Request[] = [
    {
      deleteObject: {
        objectId: slideObjectId,
      },
    },
  ];

  await slidesService.presentations.batchUpdate({
    presentationId,
    requestBody: { requests },
  });
}


/**
 * Add a text box to a slide.
 *
 * @param slidesService - Slides API service instance
 * @param presentationId - ID of the presentation
 * @param slideObjectId - Object ID of the slide
 * @param text - Text content
 * @param x - X position in points
 * @param y - Y position in points
 * @param width - Width in points
 * @param height - Height in points
 * @returns Created element info
 */
export async function addTextBox(
  slidesService: slides_v1.Slides,
  presentationId: string,
  slideObjectId: string,
  text: string,
  x: number = 100,
  y: number = 100,
  width: number = 300,
  height: number = 50
): Promise<slides_v1.Schema$BatchUpdatePresentationResponse> {
  const elementId = `textbox_${uuidv4().slice(0, 8)}`;

  const requests: slides_v1.Schema$Request[] = [
    {
      createShape: {
        objectId: elementId,
        shapeType: 'TEXT_BOX',
        elementProperties: {
          pageObjectId: slideObjectId,
          size: {
            width: { magnitude: width, unit: 'PT' },
            height: { magnitude: height, unit: 'PT' },
          },
          transform: {
            scaleX: 1,
            scaleY: 1,
            translateX: x,
            translateY: y,
            unit: 'PT',
          },
        },
      },
    },
    {
      insertText: {
        objectId: elementId,
        text,
      },
    },
  ];

  const response = await slidesService.presentations.batchUpdate({
    presentationId,
    requestBody: { requests },
  });

  return response.data;
}


/**
 * Replace all occurrences of text in the presentation.
 *
 * @param slidesService - Slides API service instance
 * @param presentationId - ID of the presentation
 * @param oldText - Text to find
 * @param newText - Replacement text
 * @returns Number of replacements
 */
export async function replaceTextInPresentation(
  slidesService: slides_v1.Slides,
  presentationId: string,
  oldText: string,
  newText: string
): Promise<number> {
  const requests: slides_v1.Schema$Request[] = [
    {
      replaceAllText: {
        containsText: {
          text: oldText,
          matchCase: true,
        },
        replaceText: newText,
      },
    },
  ];

  const response = await slidesService.presentations.batchUpdate({
    presentationId,
    requestBody: { requests },
  });

  const replies = response.data.replies || [];
  if (replies.length > 0) {
    return replies[0].replaceAllText?.occurrencesChanged || 0;
  }
  return 0;
}
```

---

## 6. TypeScript Implementation

### 6.1 Environment Setup

```bash
# Initialize project
npm init -y

# Install required packages
npm install googleapis @google-cloud/local-auth

# Install TypeScript and type definitions
npm install -D typescript @types/node

# Initialize TypeScript configuration
npx tsc --init
```

Create `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### 6.2 Complete Authentication Module

Create `src/google-workspace-auth.ts`:

```typescript
/**
 * Google Workspace APIs Authentication Module for TypeScript.
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

// Type for the auth client - uses ReturnType to handle type compatibility
// between @google-cloud/local-auth and googleapis
type GoogleAuthClient = Awaited<ReturnType<typeof authenticate>> | ReturnType<typeof google.auth.fromJSON>;

// Format expected by google.auth.fromJSON
interface SavedCredentials {
  type: string;
  client_id: string;
  client_secret: string;
  refresh_token: string;
}

// Actual format from @google-cloud/local-auth token file
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
 * Handles the token format from @google-cloud/local-auth and converts
 * it to the format expected by google.auth.fromJSON.
 */
async function loadSavedCredentials(
  tokenPath: string
): Promise<ReturnType<typeof google.auth.fromJSON> | null> {
  try {
    const content = await fs.readFile(tokenPath, 'utf-8');
    const rawCredentials: ActualTokenFormat = JSON.parse(content);

    // Convert to format expected by google.auth.fromJSON
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
 * Note: Uses the specific authenticate return type rather than GoogleAuthClient
 * because we need access to the credentials property which is only guaranteed
 * to exist on the authenticate result, not on fromJSON results.
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
    refresh_token: (client as any).credentials.refresh_token!,
  };
  await fs.writeFile(tokenPath, JSON.stringify(payload));
}

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
  const savedClient = await loadSavedCredentials(tokenPath);
  if (savedClient) {
    return savedClient;
  }

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

  return {
    drive: google.drive({ version: 'v3', auth: auth as any }),
    docs: google.docs({ version: 'v1', auth: auth as any }),
    sheets: google.sheets({ version: 'v4', auth: auth as any }),
    slides: google.slides({ version: 'v1', auth: auth as any }),
  };
}
```

### 6.3 Complete Drive Manager Module

Create `src/drive-manager.ts`:

```typescript
/**
 * Google Drive Management Module - Complete TypeScript Implementation.
 */
import * as fs from 'fs';
import * as path from 'path';
import { drive_v3 } from 'googleapis';
import { getDriveService } from './google-workspace-auth';

/**
 * SharingSummary interface for DriveManager class.
 * Note: This interface uses user-friendly terms ('editors'/'viewers') and provides
 * more detail than the standalone functions' SharingSummary in Section 2.5, which
 * uses API terms ('writers'/'readers'). The 'anyoneWithLink' field here can be
 * 'edit', 'view', or false for more precise access indication.
 */
export interface SharingSummary {
  owner: string | null;
  editors: string[];
  commenters: string[];
  viewers: string[];
  anyoneWithLink: boolean | string;
  domainAccess: Array<{ domain: string; role: string }>;
}

export class DriveManager {
  private service: drive_v3.Drive | null = null;

  /**
   * Initialize with credentials.
   */
  async init(
    credentialsPath: string = 'credentials.json',
    tokenPath: string = 'token.json'
  ): Promise<this> {
    this.service = await getDriveService(credentialsPath, tokenPath);
    return this;
  }

  private getService(): drive_v3.Drive {
    if (!this.service) {
      throw new Error('DriveManager not initialized. Call init() first.');
    }
    return this.service;
  }

  // ==================== FILE OPERATIONS ====================

  /**
   * List files with optional query filter.
   */
  async listFiles(
    query?: string,
    pageSize: number = 100,
    orderBy: string = 'modifiedTime desc'
  ): Promise<drive_v3.Schema$File[]> {
    const service = this.getService();
    const files: drive_v3.Schema$File[] = [];
    let pageToken: string | undefined;

    while (true) {
      const params: drive_v3.Params$Resource$Files$List = {
        pageSize: Math.min(pageSize, 1000),
        fields: 'nextPageToken, files(id, name, mimeType, parents, createdTime, modifiedTime, owners, size, webViewLink)',
        orderBy,
        supportsAllDrives: true,
      };

      if (query) params.q = query;
      if (pageToken) params.pageToken = pageToken;

      const response = await service.files.list(params);
      files.push(...(response.data.files || []));

      pageToken = response.data.nextPageToken ?? undefined;
      if (!pageToken || files.length >= pageSize) {
        break;
      }
    }

    return files.slice(0, pageSize);
  }

  /**
   * Get file metadata.
   */
  async getFile(fileId: string): Promise<drive_v3.Schema$File> {
    const service = this.getService();
    const response = await service.files.get({
      fileId,
      fields: '*',
      supportsAllDrives: true,
    });
    return response.data;
  }

  /**
   * Create a folder.
   */
  async createFolder(
    name: string,
    parentId?: string
  ): Promise<drive_v3.Schema$File> {
    const service = this.getService();
    const metadata: drive_v3.Schema$File = {
      name,
      mimeType: 'application/vnd.google-apps.folder',
    };
    if (parentId) {
      metadata.parents = [parentId];
    }

    const response = await service.files.create({
      requestBody: metadata,
      fields: 'id, name, webViewLink',
    });
    return response.data;
  }

  /**
   * Upload a file.
   */
  async uploadFile(
    filePath: string,
    name?: string,
    parentId?: string,
    mimeType?: string
  ): Promise<drive_v3.Schema$File> {
    const service = this.getService();
    const fileName = name ?? path.basename(filePath);

    const metadata: drive_v3.Schema$File = { name: fileName };
    if (parentId) {
      metadata.parents = [parentId];
    }

    const media = {
      mimeType,
      body: fs.createReadStream(filePath),
    };

    const response = await service.files.create({
      requestBody: metadata,
      media,
      fields: 'id, name, webViewLink',
    });
    return response.data;
  }

  /**
   * Download a file.
   */
  async downloadFile(fileId: string, outputPath: string): Promise<string> {
    const service = this.getService();
    const response = await service.files.get(
      { fileId, alt: 'media' },
      { responseType: 'stream' }
    );

    return new Promise((resolve, reject) => {
      const dest = fs.createWriteStream(outputPath);
      (response.data as NodeJS.ReadableStream)
        .pipe(dest)
        .on('finish', () => resolve(outputPath))
        .on('error', reject);
    });
  }

  /**
   * Export a Google Docs/Sheets/Slides file.
   */
  async exportGoogleFile(
    fileId: string,
    mimeType: string,
    outputPath: string
  ): Promise<string> {
    const service = this.getService();
    const response = await service.files.export(
      { fileId, mimeType },
      { responseType: 'stream' }
    );

    return new Promise((resolve, reject) => {
      const dest = fs.createWriteStream(outputPath);
      (response.data as NodeJS.ReadableStream)
        .pipe(dest)
        .on('finish', () => resolve(outputPath))
        .on('error', reject);
    });
  }

  /**
   * Update file metadata.
   */
  async updateFile(
    fileId: string,
    name?: string,
    description?: string
  ): Promise<drive_v3.Schema$File> {
    const service = this.getService();
    const metadata: drive_v3.Schema$File = {};
    if (name) metadata.name = name;
    if (description) metadata.description = description;

    const response = await service.files.update({
      fileId,
      requestBody: metadata,
      fields: 'id, name, description',
    });
    return response.data;
  }

  /**
   * Delete or trash a file.
   */
  async deleteFile(fileId: string, permanent: boolean = false): Promise<void> {
    const service = this.getService();
    if (permanent) {
      await service.files.delete({ fileId });
    } else {
      await service.files.update({
        fileId,
        requestBody: { trashed: true },
      });
    }
  }

  /**
   * Restore a file from trash.
   */
  async restoreFile(fileId: string): Promise<void> {
    const service = this.getService();
    await service.files.update({
      fileId,
      requestBody: { trashed: false },
    });
  }

  // ==================== SEARCH OPERATIONS ====================

  /**
   * Search with custom query.
   */
  async search(query: string): Promise<drive_v3.Schema$File[]> {
    return this.listFiles(query);
  }

  /**
   * Find files by name.
   */
  async findByName(
    name: string,
    exact: boolean = false
  ): Promise<drive_v3.Schema$File[]> {
    const query = exact
      ? `name = '${name}' and trashed = false`
      : `name contains '${name}' and trashed = false`;
    return this.search(query);
  }

  /**
   * Find Google Docs.
   */
  async findDocs(nameContains?: string): Promise<drive_v3.Schema$File[]> {
    let query = "mimeType = 'application/vnd.google-apps.document' and trashed = false";
    if (nameContains) {
      query = `name contains '${nameContains}' and ${query}`;
    }
    return this.search(query);
  }

  /**
   * Find Google Sheets.
   */
  async findSheets(nameContains?: string): Promise<drive_v3.Schema$File[]> {
    let query = "mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false";
    if (nameContains) {
      query = `name contains '${nameContains}' and ${query}`;
    }
    return this.search(query);
  }

  /**
   * Find Google Slides.
   */
  async findSlides(nameContains?: string): Promise<drive_v3.Schema$File[]> {
    let query = "mimeType = 'application/vnd.google-apps.presentation' and trashed = false";
    if (nameContains) {
      query = `name contains '${nameContains}' and ${query}`;
    }
    return this.search(query);
  }

  /**
   * Find folders.
   */
  async findFolders(nameContains?: string): Promise<drive_v3.Schema$File[]> {
    let query = "mimeType = 'application/vnd.google-apps.folder' and trashed = false";
    if (nameContains) {
      query = `name contains '${nameContains}' and ${query}`;
    }
    return this.search(query);
  }

  /**
   * Find files in a specific folder.
   */
  async findInFolder(folderId: string): Promise<drive_v3.Schema$File[]> {
    const query = `'${folderId}' in parents and trashed = false`;
    return this.search(query);
  }

  /**
   * Find files shared with me.
   */
  async findSharedWithMe(): Promise<drive_v3.Schema$File[]> {
    return this.search("sharedWithMe = true and trashed = false");
  }

  /**
   * Find recently modified files.
   */
  async findRecent(days: number = 7): Promise<drive_v3.Schema$File[]> {
    const cutoff = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();
    return this.search(`modifiedTime > '${cutoff}' and trashed = false`);
  }

  /**
   * Search file contents.
   */
  async fullTextSearch(text: string): Promise<drive_v3.Schema$File[]> {
    return this.search(`fullText contains '${text}' and trashed = false`);
  }

  // ==================== ORGANIZATION OPERATIONS ====================

  /**
   * Move a file to a different folder.
   */
  async moveFile(
    fileId: string,
    newParentId: string
  ): Promise<drive_v3.Schema$File> {
    const service = this.getService();
    const file = await service.files.get({
      fileId,
      fields: 'parents',
    });

    const previousParents = (file.data.parents || []).join(',');

    const response = await service.files.update({
      fileId,
      addParents: newParentId,
      removeParents: previousParents,
      fields: 'id, name, parents',
    });
    return response.data;
  }

  /**
   * Copy a file.
   */
  async copyFile(
    fileId: string,
    newName?: string,
    destinationFolderId?: string
  ): Promise<drive_v3.Schema$File> {
    const service = this.getService();
    const metadata: drive_v3.Schema$File = {};
    if (newName) metadata.name = newName;
    if (destinationFolderId) metadata.parents = [destinationFolderId];

    const response = await service.files.copy({
      fileId,
      requestBody: metadata,
      fields: 'id, name, webViewLink',
    });
    return response.data;
  }

  /**
   * Create folder path, creating intermediates as needed.
   */
  async createFolderPath(folderPath: string, rootId?: string): Promise<string> {
    const folders = folderPath.replace(/^\/|\/$/g, '').split('/');
    let parentId = rootId;

    for (const folderName of folders) {
      let query = `name = '${folderName}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false`;
      if (parentId) {
        query += ` and '${parentId}' in parents`;
      }

      const results = await this.search(query);

      if (results.length > 0) {
        parentId = results[0].id!;
      } else {
        const newFolder = await this.createFolder(folderName, parentId);
        parentId = newFolder.id!;
      }
    }

    return parentId!;
  }

  // ==================== PERMISSIONS OPERATIONS ====================

  /**
   * List all permissions for a file.
   */
  async listPermissions(fileId: string): Promise<drive_v3.Schema$Permission[]> {
    const service = this.getService();
    const response = await service.permissions.list({
      fileId,
      fields: 'permissions(id, type, role, emailAddress, domain, displayName, deleted)',
    });
    return response.data.permissions || [];
  }

  /**
   * Share with a specific user.
   */
  async shareWithUser(
    fileId: string,
    email: string,
    role: 'reader' | 'commenter' | 'writer' = 'reader',
    notify: boolean = true,
    message?: string
  ): Promise<drive_v3.Schema$Permission> {
    const service = this.getService();
    const permission: drive_v3.Schema$Permission = {
      type: 'user',
      role,
      emailAddress: email,
    };

    const response = await service.permissions.create({
      fileId,
      requestBody: permission,
      sendNotificationEmail: notify,
      emailMessage: message,
      fields: 'id, type, role, emailAddress',
    });
    return response.data;
  }

  /**
   * Share with a Google Group.
   */
  async shareWithGroup(
    fileId: string,
    groupEmail: string,
    role: 'reader' | 'commenter' | 'writer' = 'reader'
  ): Promise<drive_v3.Schema$Permission> {
    const service = this.getService();
    const permission: drive_v3.Schema$Permission = {
      type: 'group',
      role,
      emailAddress: groupEmail,
    };

    const response = await service.permissions.create({
      fileId,
      requestBody: permission,
      fields: 'id, type, role, emailAddress',
    });
    return response.data;
  }

  /**
   * Share with entire domain.
   */
  async shareWithDomain(
    fileId: string,
    domain: string,
    role: 'reader' | 'commenter' | 'writer' = 'reader'
  ): Promise<drive_v3.Schema$Permission> {
    const service = this.getService();
    const permission: drive_v3.Schema$Permission = {
      type: 'domain',
      role,
      domain,
    };

    const response = await service.permissions.create({
      fileId,
      requestBody: permission,
      fields: 'id, type, role, domain',
    });
    return response.data;
  }

  /**
   * Share with anyone (public link).
   */
  async shareWithAnyone(
    fileId: string,
    role: 'reader' | 'commenter' = 'reader'
  ): Promise<drive_v3.Schema$Permission> {
    const service = this.getService();
    const permission: drive_v3.Schema$Permission = {
      type: 'anyone',
      role,
    };

    const response = await service.permissions.create({
      fileId,
      requestBody: permission,
      fields: 'id, type, role',
    });
    return response.data;
  }

  /**
   * Update a permission's role.
   */
  async updatePermission(
    fileId: string,
    permissionId: string,
    newRole: 'reader' | 'commenter' | 'writer'
  ): Promise<drive_v3.Schema$Permission> {
    const service = this.getService();
    const response = await service.permissions.update({
      fileId,
      permissionId,
      requestBody: { role: newRole },
      fields: 'id, type, role, emailAddress',
    });
    return response.data;
  }

  /**
   * Revoke a permission.
   */
  async revokePermission(fileId: string, permissionId: string): Promise<void> {
    const service = this.getService();
    await service.permissions.delete({
      fileId,
      permissionId,
    });
  }

  /**
   * Revoke access for a user by email.
   */
  async revokeAccessByEmail(fileId: string, email: string): Promise<boolean> {
    const permissions = await this.listPermissions(fileId);

    for (const perm of permissions) {
      if ((perm.emailAddress || '').toLowerCase() === email.toLowerCase()) {
        await this.revokePermission(fileId, perm.id!);
        return true;
      }
    }
    return false;
  }

  /**
   * Get a summary of who has access.
   */
  async getSharingSummary(fileId: string): Promise<SharingSummary> {
    const permissions = await this.listPermissions(fileId);

    const summary: SharingSummary = {
      owner: null,
      editors: [],
      commenters: [],
      viewers: [],
      anyoneWithLink: false,
      domainAccess: [],
    };

    for (const perm of permissions) {
      const role = perm.role;
      const permType = perm.type;
      const email = perm.emailAddress || '';

      if (role === 'owner') {
        summary.owner = email;
      } else if (role === 'writer') {
        if (permType === 'anyone') {
          summary.anyoneWithLink = 'edit';
        } else if (permType === 'domain') {
          summary.domainAccess.push({ domain: perm.domain || '', role: 'editor' });
        } else {
          summary.editors.push(email);
        }
      } else if (role === 'commenter') {
        summary.commenters.push(email);
      } else if (role === 'reader') {
        if (permType === 'anyone') {
          summary.anyoneWithLink = 'view';
        } else if (permType === 'domain') {
          summary.domainAccess.push({ domain: perm.domain || '', role: 'viewer' });
        } else {
          summary.viewers.push(email);
        }
      }
    }

    return summary;
  }
}

// Example usage
async function main(): Promise<void> {
  const manager = await new DriveManager().init();

  // List recent files
  console.log('Recent files:');
  const files = await manager.findRecent(7);
  for (const f of files.slice(0, 5)) {
    console.log(`  - ${f.name} (${f.mimeType})`);
  }

  // Find Google Docs
  console.log('\nGoogle Docs:');
  const docs = await manager.findDocs();
  for (const doc of docs.slice(0, 5)) {
    console.log(`  - ${doc.name}`);
  }
}

// Run if executed directly
if (require.main === module) {
  main().catch(console.error);
}
```

---

## 7. Error Handling and Best Practices

### 7.1 Common Error Codes

| Error Code | Description | Solution |
|------------|-------------|----------|
| 400 | Bad Request | Check request parameters |
| 401 | Unauthorized | Token expired - re-authenticate |
| 403 | Forbidden | Check scopes, API enabled, quota |
| 404 | Not Found | Invalid file/folder ID |
| 429 | Rate Limit | Implement exponential backoff |
| 500 | Server Error | Retry with backoff |

### 7.2 Rate Limits

| API | Quota |
|-----|-------|
| Drive API | 12,000 requests/minute/project |
| Docs API | 300 requests/minute/project |
| Sheets API | 500 requests/100 seconds/project |
| Slides API | 500 requests/100 seconds/project |

### 7.3 Error Handling Pattern

```typescript
// TypeScript - Retry with exponential backoff
import { GaxiosError } from 'gaxios';

export interface RetryableRequest<T> {
  (): Promise<T>;
}

/**
 * Execute API request with exponential backoff.
 */
export async function executeWithRetry<T>(
  request: RetryableRequest<T>,
  maxRetries: number = 5
): Promise<T> {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await request();
    } catch (error) {
      if (error instanceof GaxiosError) {
        const status = error.response?.status;
        if (status && [429, 500, 502, 503, 504].includes(status)) {
          const waitTime = Math.pow(2, attempt) + Math.random();
          console.log(`Attempt ${attempt + 1} failed with ${status}. Retrying in ${waitTime.toFixed(2)} seconds...`);
          await new Promise(resolve => setTimeout(resolve, waitTime * 1000));
          continue;
        }
      }
      throw error;
    }
  }
  throw new Error(`Failed after ${maxRetries} retries`);
}

// Usage example
async function safeListFiles(service: drive_v3.Drive): Promise<drive_v3.Schema$File[]> {
  return executeWithRetry(async () => {
    const response = await service.files.list({
      pageSize: 100,
      fields: 'files(id, name)',
    });
    return response.data.files || [];
  });
}
```

### 7.4 Best Practices

1. **Use batch requests** - Combine multiple operations when possible
2. **Request only needed fields** - Use `fields` parameter to reduce response size
3. **Implement caching** - Cache file metadata to reduce API calls
4. **Handle pagination** - Always handle `nextPageToken` for list operations
5. **Use resumable uploads** - For files larger than 5MB
6. **Respect rate limits** - Implement exponential backoff

---

## 8. Quick Reference

### API Endpoints

| Operation | API | Method | Endpoint |
|-----------|-----|--------|----------|
| List files | Drive | GET | `/drive/v3/files` |
| Get file | Drive | GET | `/drive/v3/files/{fileId}` |
| Create file | Drive | POST | `/drive/v3/files` |
| Update file | Drive | PATCH | `/drive/v3/files/{fileId}` |
| Delete file | Drive | DELETE | `/drive/v3/files/{fileId}` |
| List permissions | Drive | GET | `/drive/v3/files/{fileId}/permissions` |
| Create permission | Drive | POST | `/drive/v3/files/{fileId}/permissions` |
| Delete permission | Drive | DELETE | `/drive/v3/files/{fileId}/permissions/{permissionId}` |
| Get document | Docs | GET | `/v1/documents/{documentId}` |
| Create document | Docs | POST | `/v1/documents` |
| Update document | Docs | POST | `/v1/documents/{documentId}:batchUpdate` |
| Get spreadsheet | Sheets | GET | `/v4/spreadsheets/{spreadsheetId}` |
| Create spreadsheet | Sheets | POST | `/v4/spreadsheets` |
| Get values | Sheets | GET | `/v4/spreadsheets/{id}/values/{range}` |
| Update values | Sheets | PUT | `/v4/spreadsheets/{id}/values/{range}` |
| Get presentation | Slides | GET | `/v1/presentations/{presentationId}` |
| Create presentation | Slides | POST | `/v1/presentations` |
| Update presentation | Slides | POST | `/v1/presentations/{id}:batchUpdate` |

### Common Search Queries

```
# Find all Google Docs
mimeType = 'application/vnd.google-apps.document' and trashed = false

# Find files by name
name contains 'Report' and trashed = false

# Find files in folder
'FOLDER_ID' in parents and trashed = false

# Find recent files
modifiedTime > '2024-01-01T00:00:00' and trashed = false

# Full text search
fullText contains 'quarterly sales' and trashed = false

# Find shared files
sharedWithMe = true and trashed = false

# Find files by owner
'user@example.com' in owners and trashed = false
```

---

## Sources

### Google Drive API
- [Drive API Documentation](https://developers.google.com/workspace/drive/api)
- [Drive API Reference](https://developers.google.com/workspace/drive/api/reference/rest/v3)
- [Search for files and folders](https://developers.google.com/workspace/drive/api/guides/search-files)
- [Search query terms and operators](https://developers.google.com/workspace/drive/api/guides/ref-search-terms)
- [Permissions REST Resource](https://developers.google.com/drive/api/reference/rest/v3/permissions)

### Google Docs API
- [Docs API Overview](https://developers.google.com/workspace/docs/api/how-tos/overview)
- [Docs API Reference](https://developers.google.com/workspace/docs/api/reference/rest)
- [Node.js Quickstart](https://developers.google.com/workspace/docs/api/quickstart/nodejs)

### Google Sheets API
- [Sheets API Overview](https://developers.google.com/workspace/sheets/api/guides/concepts)
- [Sheets API Reference](https://developers.google.com/workspace/sheets/api/reference/rest)
- [Node.js Quickstart](https://developers.google.com/workspace/sheets/api/quickstart/nodejs)

### Google Slides API
- [Slides API Overview](https://developers.google.com/workspace/slides/api/guides/overview)
- [Slides API Reference](https://developers.google.com/workspace/slides/api/reference/rest)
- [Node.js Quickstart](https://developers.google.com/workspace/slides/api/quickstart/nodejs)

### Client Libraries
- [Google API Node.js Client](https://github.com/googleapis/google-api-nodejs-client)
- [googleapis npm package](https://www.npmjs.com/package/googleapis)
- [TypeScript Support Documentation](https://github.com/googleapis/google-api-nodejs-client#typescript)

/**
 * Google Drive API Functions - Implementation from document lines 101-1121
 *
 * This module implements all Drive API functions from Section 2 of the guide.
 */
import * as fs from 'fs';
import * as path from 'path';
import { drive_v3 } from 'googleapis';

// ==================== FILE OPERATIONS (Section 2.1) ====================

/**
 * List files in Google Drive.
 *
 * @param service - Drive API service instance
 * @param pageSize - Maximum files per page (max 1000)
 * @param query - Optional search query string
 * @param maxResults - Maximum total results to return (default: 100, 0 = unlimited)
 * @returns List of file metadata objects
 *
 * NOTE: The original document implementation fetches ALL pages which can be
 * very slow for large Drive accounts. This version adds a maxResults parameter
 * to limit the total results. Set maxResults=0 for original behavior.
 */
export async function listFiles(
  service: drive_v3.Drive,
  pageSize: number = 100,
  query?: string,
  maxResults: number = 100
): Promise<drive_v3.Schema$File[]> {
  const files: drive_v3.Schema$File[] = [];
  let pageToken: string | undefined;

  // Calculate effective page size
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

    // Check if we've reached maxResults
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

// ==================== SEARCH AND QUERY (Section 2.2) ====================

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

// ==================== FOLDER MANAGEMENT (Section 2.3) ====================

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

// ==================== MOVE AND ORGANIZE FILES (Section 2.4) ====================

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

// ==================== PERMISSIONS MANAGEMENT (Section 2.5) ====================

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

/**
 * Google Drive Management Module - Complete TypeScript Implementation.
 * From document lines: 2905-3531
 */
import * as fs from 'fs';
import * as path from 'path';
import { drive_v3 } from 'googleapis';
import { getDriveService } from './google-workspace-auth';

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

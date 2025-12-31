# Google Workspace APIs Integration Guide

This guide provides comprehensive instructions for programmatically accessing Google Drive, Docs, Sheets, and Slides using Python and Node.js. It covers file management, document operations, permissions management, and organization workflows.

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
6. [Python Implementation](#6-python-implementation)
7. [Node.js Implementation](#7-nodejs-implementation)
8. [Error Handling and Best Practices](#8-error-handling-and-best-practices)
9. [Quick Reference](#9-quick-reference)
10. [Sources](#sources)

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

```python
# Python - List files
def list_files(service, page_size=100, query=None):
    """
    List files in Google Drive.

    Args:
        service: Drive API service instance
        page_size: Maximum files per page (max 1000)
        query: Optional search query string

    Returns:
        List of file metadata dictionaries
    """
    files = []
    page_token = None

    while True:
        params = {
            'pageSize': page_size,
            'fields': 'nextPageToken, files(id, name, mimeType, parents, createdTime, modifiedTime, owners, permissions)',
            'supportsAllDrives': True,
        }

        if query:
            params['q'] = query
        if page_token:
            params['pageToken'] = page_token

        results = service.files().list(**params).execute()
        files.extend(results.get('files', []))

        page_token = results.get('nextPageToken')
        if not page_token:
            break

    return files
```

#### Create File/Folder

```python
# Python - Create a folder
def create_folder(service, name, parent_id=None):
    """
    Create a folder in Google Drive.

    Args:
        service: Drive API service instance
        name: Folder name
        parent_id: Optional parent folder ID

    Returns:
        Created folder metadata
    """
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    if parent_id:
        file_metadata['parents'] = [parent_id]

    folder = service.files().create(
        body=file_metadata,
        fields='id, name, webViewLink'
    ).execute()

    return folder


# Python - Upload a file
def upload_file(service, file_path, name=None, parent_id=None, mime_type=None):
    """
    Upload a file to Google Drive.

    Args:
        service: Drive API service instance
        file_path: Local path to the file
        name: Optional name (defaults to filename)
        parent_id: Optional parent folder ID
        mime_type: Optional MIME type

    Returns:
        Uploaded file metadata
    """
    from googleapiclient.http import MediaFileUpload
    import os

    if name is None:
        name = os.path.basename(file_path)

    file_metadata = {'name': name}

    if parent_id:
        file_metadata['parents'] = [parent_id]

    media = MediaFileUpload(
        file_path,
        mimetype=mime_type,
        resumable=True
    )

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name, webViewLink'
    ).execute()

    return file
```

#### Update File Metadata

```python
# Python - Update file metadata
def update_file_metadata(service, file_id, new_name=None, description=None):
    """
    Update a file's metadata.

    Args:
        service: Drive API service instance
        file_id: ID of the file to update
        new_name: Optional new name
        description: Optional description

    Returns:
        Updated file metadata
    """
    file_metadata = {}

    if new_name:
        file_metadata['name'] = new_name
    if description:
        file_metadata['description'] = description

    updated_file = service.files().update(
        fileId=file_id,
        body=file_metadata,
        fields='id, name, description'
    ).execute()

    return updated_file
```

#### Delete File

```python
# Python - Delete a file (move to trash or permanently delete)
def delete_file(service, file_id, permanent=False):
    """
    Delete a file from Google Drive.

    Args:
        service: Drive API service instance
        file_id: ID of the file to delete
        permanent: If True, permanently delete; otherwise move to trash
    """
    if permanent:
        service.files().delete(fileId=file_id).execute()
    else:
        # Move to trash
        service.files().update(
            fileId=file_id,
            body={'trashed': True}
        ).execute()


def restore_from_trash(service, file_id):
    """Restore a file from trash."""
    service.files().update(
        fileId=file_id,
        body={'trashed': False}
    ).execute()
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

```python
# Python - Search functions
def search_files(service, query, page_size=100):
    """
    Search for files using a query string.

    Args:
        service: Drive API service instance
        query: Search query string
        page_size: Maximum results per page

    Returns:
        List of matching files
    """
    return list_files(service, page_size=page_size, query=query)


def find_docs_by_name(service, name_contains):
    """Find Google Docs containing a specific name."""
    query = f"name contains '{name_contains}' and mimeType = 'application/vnd.google-apps.document' and trashed = false"
    return search_files(service, query)


def find_sheets_by_name(service, name_contains):
    """Find Google Sheets containing a specific name."""
    query = f"name contains '{name_contains}' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
    return search_files(service, query)


def find_slides_by_name(service, name_contains):
    """Find Google Slides containing a specific name."""
    query = f"name contains '{name_contains}' and mimeType = 'application/vnd.google-apps.presentation' and trashed = false"
    return search_files(service, query)


def find_files_in_folder(service, folder_id):
    """Find all files in a specific folder."""
    query = f"'{folder_id}' in parents and trashed = false"
    return search_files(service, query)


def find_files_by_owner(service, owner_email):
    """Find files owned by a specific user."""
    query = f"'{owner_email}' in owners and trashed = false"
    return search_files(service, query)


def find_shared_with_me(service):
    """Find files shared with the current user."""
    query = "sharedWithMe = true and trashed = false"
    return search_files(service, query)


def find_recent_files(service, days=7):
    """Find files modified in the last N days."""
    from datetime import datetime, timedelta

    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat() + 'Z'
    query = f"modifiedTime > '{cutoff}' and trashed = false"
    return search_files(service, query)


def full_text_search(service, search_text):
    """Search file contents for specific text."""
    query = f"fullText contains '{search_text}' and trashed = false"
    return search_files(service, query)


def find_all_folders(service):
    """Find all folders."""
    query = "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    return search_files(service, query)
```

### 2.3 Folder Management

```python
# Python - Folder management functions
def get_folder_contents(service, folder_id, include_subfolders=False):
    """
    Get all contents of a folder.

    Args:
        service: Drive API service instance
        folder_id: ID of the folder
        include_subfolders: If True, recursively get subfolder contents

    Returns:
        List of files and folders
    """
    query = f"'{folder_id}' in parents and trashed = false"
    contents = search_files(service, query)

    if include_subfolders:
        folders = [f for f in contents if f['mimeType'] == 'application/vnd.google-apps.folder']
        for folder in folders:
            subfolder_contents = get_folder_contents(service, folder['id'], True)
            contents.extend(subfolder_contents)

    return contents


def get_folder_tree(service, folder_id, depth=0, max_depth=10):
    """
    Get a hierarchical view of folder structure.

    Args:
        service: Drive API service instance
        folder_id: ID of the root folder
        depth: Current depth (for recursion)
        max_depth: Maximum recursion depth

    Returns:
        Dictionary with folder tree structure
    """
    if depth > max_depth:
        return None

    folder_info = service.files().get(
        fileId=folder_id,
        fields='id, name'
    ).execute()

    query = f"'{folder_id}' in parents and trashed = false"
    contents = search_files(service, query)

    tree = {
        'id': folder_info['id'],
        'name': folder_info['name'],
        'type': 'folder',
        'children': []
    }

    for item in contents:
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            subtree = get_folder_tree(service, item['id'], depth + 1, max_depth)
            if subtree:
                tree['children'].append(subtree)
        else:
            tree['children'].append({
                'id': item['id'],
                'name': item['name'],
                'type': 'file',
                'mimeType': item['mimeType']
            })

    return tree


def create_folder_path(service, path, root_id=None):
    """
    Create a folder path, creating intermediate folders as needed.

    Args:
        service: Drive API service instance
        path: Folder path like 'Projects/2024/Q1'
        root_id: Optional root folder ID

    Returns:
        ID of the final folder in the path
    """
    folders = path.strip('/').split('/')
    parent_id = root_id

    for folder_name in folders:
        # Check if folder exists
        query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = search_files(service, query, page_size=1)

        if results:
            parent_id = results[0]['id']
        else:
            # Create the folder
            new_folder = create_folder(service, folder_name, parent_id)
            parent_id = new_folder['id']

    return parent_id
```

### 2.4 Move and Organize Files

```python
# Python - Move and organize functions
def move_file(service, file_id, new_parent_id, remove_from_current=True):
    """
    Move a file to a different folder.

    Args:
        service: Drive API service instance
        file_id: ID of the file to move
        new_parent_id: ID of the destination folder
        remove_from_current: If True, remove from current parent(s)

    Returns:
        Updated file metadata
    """
    # Get current parents
    file = service.files().get(
        fileId=file_id,
        fields='parents'
    ).execute()

    previous_parents = ','.join(file.get('parents', []))

    # Move the file
    updated_file = service.files().update(
        fileId=file_id,
        addParents=new_parent_id,
        removeParents=previous_parents if remove_from_current else None,
        fields='id, name, parents'
    ).execute()

    return updated_file


def copy_file(service, file_id, new_name=None, destination_folder_id=None):
    """
    Copy a file.

    Args:
        service: Drive API service instance
        file_id: ID of the file to copy
        new_name: Optional new name for the copy
        destination_folder_id: Optional destination folder

    Returns:
        Copied file metadata
    """
    copy_metadata = {}

    if new_name:
        copy_metadata['name'] = new_name
    if destination_folder_id:
        copy_metadata['parents'] = [destination_folder_id]

    copied_file = service.files().copy(
        fileId=file_id,
        body=copy_metadata,
        fields='id, name, webViewLink'
    ).execute()

    return copied_file


def add_to_folder(service, file_id, folder_id):
    """
    Add a file to an additional folder (create shortcut).

    Args:
        service: Drive API service instance
        file_id: ID of the file
        folder_id: ID of the folder to add to

    Returns:
        Updated file metadata
    """
    updated_file = service.files().update(
        fileId=file_id,
        addParents=folder_id,
        fields='id, name, parents'
    ).execute()

    return updated_file


def organize_files_by_type(service, source_folder_id):
    """
    Organize files in a folder by type into subfolders.

    Args:
        service: Drive API service instance
        source_folder_id: ID of the source folder

    Returns:
        Dictionary mapping types to created folder IDs
    """
    type_folders = {
        'application/vnd.google-apps.document': 'Documents',
        'application/vnd.google-apps.spreadsheet': 'Spreadsheets',
        'application/vnd.google-apps.presentation': 'Presentations',
        'application/pdf': 'PDFs',
        'image/': 'Images',
    }

    created_folders = {}
    contents = find_files_in_folder(service, source_folder_id)

    for file in contents:
        if file['mimeType'] == 'application/vnd.google-apps.folder':
            continue

        # Determine target folder
        target_folder_name = 'Other'
        for mime_prefix, folder_name in type_folders.items():
            if file['mimeType'].startswith(mime_prefix):
                target_folder_name = folder_name
                break

        # Create or get target folder
        if target_folder_name not in created_folders:
            folder = create_folder(service, target_folder_name, source_folder_id)
            created_folders[target_folder_name] = folder['id']

        # Move file to target folder
        move_file(service, file['id'], created_folders[target_folder_name])

    return created_folders
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

```python
# Python - Permissions management functions
def list_permissions(service, file_id):
    """
    List all permissions for a file.

    Args:
        service: Drive API service instance
        file_id: ID of the file

    Returns:
        List of permission objects
    """
    permissions = service.permissions().list(
        fileId=file_id,
        fields='permissions(id, type, role, emailAddress, domain, displayName, expirationTime, deleted)'
    ).execute()

    return permissions.get('permissions', [])


def get_permission_details(service, file_id, permission_id):
    """
    Get detailed information about a specific permission.

    Args:
        service: Drive API service instance
        file_id: ID of the file
        permission_id: ID of the permission

    Returns:
        Permission details
    """
    permission = service.permissions().get(
        fileId=file_id,
        permissionId=permission_id,
        fields='*'
    ).execute()

    return permission


def share_with_user(service, file_id, email, role='reader', send_notification=True, message=None):
    """
    Share a file with a specific user.

    Args:
        service: Drive API service instance
        file_id: ID of the file to share
        email: Email address of the user
        role: Permission role ('reader', 'commenter', 'writer')
        send_notification: Send email notification
        message: Optional message in notification

    Returns:
        Created permission
    """
    permission = {
        'type': 'user',
        'role': role,
        'emailAddress': email
    }

    created_permission = service.permissions().create(
        fileId=file_id,
        body=permission,
        sendNotificationEmail=send_notification,
        emailMessage=message,
        fields='id, type, role, emailAddress'
    ).execute()

    return created_permission


def share_with_group(service, file_id, group_email, role='reader'):
    """
    Share a file with a Google Group.

    Args:
        service: Drive API service instance
        file_id: ID of the file
        group_email: Email address of the Google Group
        role: Permission role

    Returns:
        Created permission
    """
    permission = {
        'type': 'group',
        'role': role,
        'emailAddress': group_email
    }

    return service.permissions().create(
        fileId=file_id,
        body=permission,
        fields='id, type, role, emailAddress'
    ).execute()


def share_with_domain(service, file_id, domain, role='reader'):
    """
    Share a file with an entire domain.

    Args:
        service: Drive API service instance
        file_id: ID of the file
        domain: Domain name (e.g., 'example.com')
        role: Permission role

    Returns:
        Created permission
    """
    permission = {
        'type': 'domain',
        'role': role,
        'domain': domain
    }

    return service.permissions().create(
        fileId=file_id,
        body=permission,
        fields='id, type, role, domain'
    ).execute()


def share_with_anyone(service, file_id, role='reader'):
    """
    Share a file with anyone who has the link.

    Args:
        service: Drive API service instance
        file_id: ID of the file
        role: Permission role ('reader' or 'commenter')

    Returns:
        Created permission
    """
    permission = {
        'type': 'anyone',
        'role': role
    }

    return service.permissions().create(
        fileId=file_id,
        body=permission,
        fields='id, type, role'
    ).execute()


def update_permission(service, file_id, permission_id, new_role):
    """
    Update an existing permission's role.

    Args:
        service: Drive API service instance
        file_id: ID of the file
        permission_id: ID of the permission to update
        new_role: New role ('reader', 'commenter', 'writer')

    Returns:
        Updated permission
    """
    return service.permissions().update(
        fileId=file_id,
        permissionId=permission_id,
        body={'role': new_role},
        fields='id, type, role, emailAddress'
    ).execute()


def revoke_permission(service, file_id, permission_id):
    """
    Revoke a permission (remove access).

    Args:
        service: Drive API service instance
        file_id: ID of the file
        permission_id: ID of the permission to revoke
    """
    service.permissions().delete(
        fileId=file_id,
        permissionId=permission_id
    ).execute()


def revoke_access_by_email(service, file_id, email):
    """
    Revoke access for a specific user by email.

    Args:
        service: Drive API service instance
        file_id: ID of the file
        email: Email address of the user

    Returns:
        True if access was revoked, False if user had no access
    """
    permissions = list_permissions(service, file_id)

    for perm in permissions:
        if perm.get('emailAddress', '').lower() == email.lower():
            revoke_permission(service, file_id, perm['id'])
            return True

    return False


def transfer_ownership(service, file_id, new_owner_email):
    """
    Transfer ownership of a file to another user.

    Args:
        service: Drive API service instance
        file_id: ID of the file
        new_owner_email: Email of the new owner

    Returns:
        Updated permission

    Note:
        - The new owner must be in the same domain for Google Workspace
        - For personal accounts, ownership transfer may be restricted
    """
    permission = {
        'type': 'user',
        'role': 'owner',
        'emailAddress': new_owner_email
    }

    return service.permissions().create(
        fileId=file_id,
        body=permission,
        transferOwnership=True,
        fields='id, type, role, emailAddress'
    ).execute()


def get_sharing_summary(service, file_id):
    """
    Get a summary of who has access to a file.

    Args:
        service: Drive API service instance
        file_id: ID of the file

    Returns:
        Dictionary with sharing summary
    """
    permissions = list_permissions(service, file_id)

    summary = {
        'owner': None,
        'writers': [],
        'commenters': [],
        'readers': [],
        'anyone_with_link': False,
        'domain_shared': []
    }

    for perm in permissions:
        role = perm.get('role')
        perm_type = perm.get('type')

        if role == 'owner':
            summary['owner'] = perm.get('emailAddress')
        elif role == 'writer':
            if perm_type == 'user':
                summary['writers'].append(perm.get('emailAddress'))
            elif perm_type == 'group':
                summary['writers'].append(f"group:{perm.get('emailAddress')}")
        elif role == 'commenter':
            summary['commenters'].append(perm.get('emailAddress'))
        elif role == 'reader':
            if perm_type == 'anyone':
                summary['anyone_with_link'] = True
            elif perm_type == 'domain':
                summary['domain_shared'].append(perm.get('domain'))
            elif perm_type == 'user':
                summary['readers'].append(perm.get('emailAddress'))

    return summary
```

---

## 3. Google Docs API

The Google Docs API allows you to create and manipulate documents programmatically.

### 3.1 Create Documents

```python
# Python - Create documents
def create_document(docs_service, title):
    """
    Create a new Google Document.

    Args:
        docs_service: Docs API service instance
        title: Document title

    Returns:
        Created document metadata
    """
    document = docs_service.documents().create(
        body={'title': title}
    ).execute()

    return document


def create_document_with_content(docs_service, title, content):
    """
    Create a new Google Document with initial content.

    Args:
        docs_service: Docs API service instance
        title: Document title
        content: Initial text content

    Returns:
        Created document metadata
    """
    # Create the document
    document = create_document(docs_service, title)
    document_id = document['documentId']

    # Insert content
    requests = [
        {
            'insertText': {
                'location': {'index': 1},
                'text': content
            }
        }
    ]

    docs_service.documents().batchUpdate(
        documentId=document_id,
        body={'requests': requests}
    ).execute()

    return document


def create_document_in_folder(drive_service, docs_service, title, folder_id):
    """
    Create a document in a specific folder.

    Args:
        drive_service: Drive API service instance
        docs_service: Docs API service instance
        title: Document title
        folder_id: Parent folder ID

    Returns:
        Created document metadata
    """
    # Create the document
    document = create_document(docs_service, title)
    document_id = document['documentId']

    # Move to folder
    move_file(drive_service, document_id, folder_id)

    return document
```

### 3.2 Read Document Content

```python
# Python - Read document content
def get_document(docs_service, document_id):
    """
    Get a document's full content.

    Args:
        docs_service: Docs API service instance
        document_id: ID of the document

    Returns:
        Document object with content
    """
    document = docs_service.documents().get(
        documentId=document_id
    ).execute()

    return document


def get_document_text(docs_service, document_id):
    """
    Extract plain text from a document.

    Args:
        docs_service: Docs API service instance
        document_id: ID of the document

    Returns:
        Plain text content of the document
    """
    document = get_document(docs_service, document_id)

    text_content = []

    def extract_text(elements):
        for element in elements:
            if 'paragraph' in element:
                for para_element in element['paragraph'].get('elements', []):
                    if 'textRun' in para_element:
                        text_content.append(para_element['textRun'].get('content', ''))
            elif 'table' in element:
                for row in element['table'].get('tableRows', []):
                    for cell in row.get('tableCells', []):
                        extract_text(cell.get('content', []))

    body = document.get('body', {})
    extract_text(body.get('content', []))

    return ''.join(text_content)


def get_document_summary(docs_service, document_id, max_chars=500):
    """
    Get a summary of document content (first N characters).

    Args:
        docs_service: Docs API service instance
        document_id: ID of the document
        max_chars: Maximum characters to return

    Returns:
        Dictionary with title and summary
    """
    document = get_document(docs_service, document_id)
    text = get_document_text(docs_service, document_id)

    summary = text[:max_chars].strip()
    if len(text) > max_chars:
        summary += '...'

    return {
        'title': document.get('title'),
        'documentId': document_id,
        'summary': summary,
        'totalLength': len(text)
    }


def get_document_structure(docs_service, document_id):
    """
    Get the structural elements of a document (headings, lists, tables).

    Args:
        docs_service: Docs API service instance
        document_id: ID of the document

    Returns:
        Dictionary with document structure
    """
    document = get_document(docs_service, document_id)

    structure = {
        'title': document.get('title'),
        'headings': [],
        'lists': 0,
        'tables': 0,
        'images': 0
    }

    body = document.get('body', {})

    for element in body.get('content', []):
        if 'paragraph' in element:
            paragraph = element['paragraph']
            style = paragraph.get('paragraphStyle', {}).get('namedStyleType', '')

            if style.startswith('HEADING'):
                text = ''
                for para_element in paragraph.get('elements', []):
                    if 'textRun' in para_element:
                        text += para_element['textRun'].get('content', '')

                structure['headings'].append({
                    'level': style,
                    'text': text.strip()
                })

            # Check for inline objects (images)
            for para_element in paragraph.get('elements', []):
                if 'inlineObjectElement' in para_element:
                    structure['images'] += 1

        elif 'table' in element:
            structure['tables'] += 1

    return structure
```

### 3.3 Update Documents

```python
# Python - Update documents
def append_text(docs_service, document_id, text):
    """
    Append text to the end of a document.

    Args:
        docs_service: Docs API service instance
        document_id: ID of the document
        text: Text to append
    """
    # Get the document to find the end index
    document = get_document(docs_service, document_id)
    end_index = document['body']['content'][-1]['endIndex'] - 1

    requests = [
        {
            'insertText': {
                'location': {'index': end_index},
                'text': text
            }
        }
    ]

    docs_service.documents().batchUpdate(
        documentId=document_id,
        body={'requests': requests}
    ).execute()


def insert_text_at_position(docs_service, document_id, text, index):
    """
    Insert text at a specific position in the document.

    Args:
        docs_service: Docs API service instance
        document_id: ID of the document
        text: Text to insert
        index: Position to insert at (1-based)
    """
    requests = [
        {
            'insertText': {
                'location': {'index': index},
                'text': text
            }
        }
    ]

    docs_service.documents().batchUpdate(
        documentId=document_id,
        body={'requests': requests}
    ).execute()


def replace_text(docs_service, document_id, old_text, new_text):
    """
    Replace all occurrences of text in a document.

    Args:
        docs_service: Docs API service instance
        document_id: ID of the document
        old_text: Text to find
        new_text: Replacement text

    Returns:
        Number of replacements made
    """
    requests = [
        {
            'replaceAllText': {
                'containsText': {
                    'text': old_text,
                    'matchCase': True
                },
                'replaceText': new_text
            }
        }
    ]

    result = docs_service.documents().batchUpdate(
        documentId=document_id,
        body={'requests': requests}
    ).execute()

    replies = result.get('replies', [])
    if replies:
        return replies[0].get('replaceAllText', {}).get('occurrencesChanged', 0)
    return 0


def delete_content_range(docs_service, document_id, start_index, end_index):
    """
    Delete content in a specific range.

    Args:
        docs_service: Docs API service instance
        document_id: ID of the document
        start_index: Start index (1-based)
        end_index: End index
    """
    requests = [
        {
            'deleteContentRange': {
                'range': {
                    'startIndex': start_index,
                    'endIndex': end_index
                }
            }
        }
    ]

    docs_service.documents().batchUpdate(
        documentId=document_id,
        body={'requests': requests}
    ).execute()


def add_heading(docs_service, document_id, text, heading_level=1):
    """
    Add a heading to the end of the document.

    Args:
        docs_service: Docs API service instance
        document_id: ID of the document
        text: Heading text
        heading_level: Heading level (1-6)
    """
    # Get the document to find the end index
    document = get_document(docs_service, document_id)
    end_index = document['body']['content'][-1]['endIndex'] - 1

    heading_styles = {
        1: 'HEADING_1',
        2: 'HEADING_2',
        3: 'HEADING_3',
        4: 'HEADING_4',
        5: 'HEADING_5',
        6: 'HEADING_6'
    }

    requests = [
        {
            'insertText': {
                'location': {'index': end_index},
                'text': text + '\n'
            }
        },
        {
            'updateParagraphStyle': {
                'range': {
                    'startIndex': end_index,
                    'endIndex': end_index + len(text) + 1
                },
                'paragraphStyle': {
                    'namedStyleType': heading_styles.get(heading_level, 'HEADING_1')
                },
                'fields': 'namedStyleType'
            }
        }
    ]

    docs_service.documents().batchUpdate(
        documentId=document_id,
        body={'requests': requests}
    ).execute()
```

### 3.4 Search Within Documents

```python
# Python - Search within documents
def search_in_document(docs_service, document_id, search_text):
    """
    Search for text within a document.

    Args:
        docs_service: Docs API service instance
        document_id: ID of the document
        search_text: Text to search for

    Returns:
        List of matches with context
    """
    text = get_document_text(docs_service, document_id)

    matches = []
    search_lower = search_text.lower()
    text_lower = text.lower()

    start = 0
    while True:
        index = text_lower.find(search_lower, start)
        if index == -1:
            break

        # Get context (50 chars before and after)
        context_start = max(0, index - 50)
        context_end = min(len(text), index + len(search_text) + 50)

        matches.append({
            'position': index,
            'context': text[context_start:context_end],
            'match': text[index:index + len(search_text)]
        })

        start = index + 1

    return matches


def search_documents_for_text(drive_service, docs_service, search_text, folder_id=None):
    """
    Search across multiple documents for specific text.

    Args:
        drive_service: Drive API service instance
        docs_service: Docs API service instance
        search_text: Text to search for
        folder_id: Optional folder to limit search

    Returns:
        List of documents containing the text
    """
    # First, use Drive's fullText search for efficiency
    query = f"fullText contains '{search_text}' and mimeType = 'application/vnd.google-apps.document' and trashed = false"

    if folder_id:
        query += f" and '{folder_id}' in parents"

    files = search_files(drive_service, query)

    results = []
    for file in files:
        try:
            matches = search_in_document(docs_service, file['id'], search_text)
            if matches:
                results.append({
                    'documentId': file['id'],
                    'name': file['name'],
                    'matchCount': len(matches),
                    'matches': matches[:5]  # First 5 matches
                })
        except Exception as e:
            print(f"Error searching {file['name']}: {e}")

    return results
```

---

## 4. Google Sheets API

The Google Sheets API v4 provides comprehensive spreadsheet operations.

### 4.1 Create Spreadsheets

```python
# Python - Create spreadsheets
def create_spreadsheet(sheets_service, title):
    """
    Create a new Google Spreadsheet.

    Args:
        sheets_service: Sheets API service instance
        title: Spreadsheet title

    Returns:
        Created spreadsheet metadata
    """
    spreadsheet = {
        'properties': {
            'title': title
        }
    }

    spreadsheet = sheets_service.spreadsheets().create(
        body=spreadsheet,
        fields='spreadsheetId,spreadsheetUrl'
    ).execute()

    return spreadsheet


def create_spreadsheet_with_sheets(sheets_service, title, sheet_names):
    """
    Create a spreadsheet with multiple named sheets.

    Args:
        sheets_service: Sheets API service instance
        title: Spreadsheet title
        sheet_names: List of sheet names

    Returns:
        Created spreadsheet metadata
    """
    sheets = [{'properties': {'title': name}} for name in sheet_names]

    spreadsheet = {
        'properties': {'title': title},
        'sheets': sheets
    }

    result = sheets_service.spreadsheets().create(
        body=spreadsheet,
        fields='spreadsheetId,spreadsheetUrl,sheets.properties'
    ).execute()

    return result


def create_spreadsheet_with_data(sheets_service, title, data, sheet_name='Sheet1'):
    """
    Create a spreadsheet and populate it with data.

    Args:
        sheets_service: Sheets API service instance
        title: Spreadsheet title
        data: 2D list of values
        sheet_name: Name of the sheet

    Returns:
        Created spreadsheet metadata
    """
    # Create the spreadsheet
    spreadsheet = create_spreadsheet(sheets_service, title)
    spreadsheet_id = spreadsheet['spreadsheetId']

    # Write the data
    write_values(sheets_service, spreadsheet_id, f'{sheet_name}!A1', data)

    return spreadsheet
```

### 4.2 Read Data

```python
# Python - Read spreadsheet data
def get_spreadsheet(sheets_service, spreadsheet_id):
    """
    Get spreadsheet metadata.

    Args:
        sheets_service: Sheets API service instance
        spreadsheet_id: ID of the spreadsheet

    Returns:
        Spreadsheet metadata
    """
    spreadsheet = sheets_service.spreadsheets().get(
        spreadsheetId=spreadsheet_id
    ).execute()

    return spreadsheet


def read_values(sheets_service, spreadsheet_id, range_name):
    """
    Read values from a spreadsheet range.

    Args:
        sheets_service: Sheets API service instance
        spreadsheet_id: ID of the spreadsheet
        range_name: A1 notation range (e.g., 'Sheet1!A1:D10')

    Returns:
        2D list of values
    """
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    return result.get('values', [])


def read_all_values(sheets_service, spreadsheet_id, sheet_name='Sheet1'):
    """
    Read all values from a sheet.

    Args:
        sheets_service: Sheets API service instance
        spreadsheet_id: ID of the spreadsheet
        sheet_name: Name of the sheet

    Returns:
        2D list of all values
    """
    return read_values(sheets_service, spreadsheet_id, sheet_name)


def read_multiple_ranges(sheets_service, spreadsheet_id, ranges):
    """
    Read multiple ranges at once.

    Args:
        sheets_service: Sheets API service instance
        spreadsheet_id: ID of the spreadsheet
        ranges: List of A1 notation ranges

    Returns:
        Dictionary mapping ranges to values
    """
    result = sheets_service.spreadsheets().values().batchGet(
        spreadsheetId=spreadsheet_id,
        ranges=ranges
    ).execute()

    return {
        vr['range']: vr.get('values', [])
        for vr in result.get('valueRanges', [])
    }


def get_sheet_summary(sheets_service, spreadsheet_id):
    """
    Get a summary of the spreadsheet.

    Args:
        sheets_service: Sheets API service instance
        spreadsheet_id: ID of the spreadsheet

    Returns:
        Dictionary with spreadsheet summary
    """
    spreadsheet = get_spreadsheet(sheets_service, spreadsheet_id)

    summary = {
        'title': spreadsheet['properties']['title'],
        'spreadsheetId': spreadsheet_id,
        'url': spreadsheet.get('spreadsheetUrl'),
        'sheets': []
    }

    for sheet in spreadsheet.get('sheets', []):
        props = sheet['properties']
        grid_props = props.get('gridProperties', {})

        summary['sheets'].append({
            'sheetId': props['sheetId'],
            'title': props['title'],
            'rowCount': grid_props.get('rowCount', 0),
            'columnCount': grid_props.get('columnCount', 0)
        })

    return summary
```

### 4.3 Update Data

```python
# Python - Update spreadsheet data
def write_values(sheets_service, spreadsheet_id, range_name, values):
    """
    Write values to a spreadsheet range.

    Args:
        sheets_service: Sheets API service instance
        spreadsheet_id: ID of the spreadsheet
        range_name: A1 notation range
        values: 2D list of values

    Returns:
        Update result
    """
    body = {'values': values}

    result = sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()

    return result


def append_values(sheets_service, spreadsheet_id, range_name, values):
    """
    Append values after the last row of data.

    Args:
        sheets_service: Sheets API service instance
        spreadsheet_id: ID of the spreadsheet
        range_name: A1 notation range (determines columns)
        values: 2D list of values to append

    Returns:
        Append result
    """
    body = {'values': values}

    result = sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()

    return result


def clear_values(sheets_service, spreadsheet_id, range_name):
    """
    Clear values from a range.

    Args:
        sheets_service: Sheets API service instance
        spreadsheet_id: ID of the spreadsheet
        range_name: A1 notation range
    """
    sheets_service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()


def update_multiple_ranges(sheets_service, spreadsheet_id, data):
    """
    Update multiple ranges at once.

    Args:
        sheets_service: Sheets API service instance
        spreadsheet_id: ID of the spreadsheet
        data: Dictionary mapping ranges to values

    Returns:
        Update result
    """
    value_ranges = [
        {'range': range_name, 'values': values}
        for range_name, values in data.items()
    ]

    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': value_ranges
    }

    result = sheets_service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()

    return result


def add_sheet(sheets_service, spreadsheet_id, sheet_name):
    """
    Add a new sheet to a spreadsheet.

    Args:
        sheets_service: Sheets API service instance
        spreadsheet_id: ID of the spreadsheet
        sheet_name: Name for the new sheet

    Returns:
        New sheet properties
    """
    requests = [{
        'addSheet': {
            'properties': {
                'title': sheet_name
            }
        }
    }]

    result = sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    return result['replies'][0]['addSheet']['properties']


def delete_sheet(sheets_service, spreadsheet_id, sheet_id):
    """
    Delete a sheet from a spreadsheet.

    Args:
        sheets_service: Sheets API service instance
        spreadsheet_id: ID of the spreadsheet
        sheet_id: ID of the sheet to delete
    """
    requests = [{
        'deleteSheet': {
            'sheetId': sheet_id
        }
    }]

    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()
```

### 4.4 Search and Query Data

```python
# Python - Search and query spreadsheet data
def find_in_sheet(sheets_service, spreadsheet_id, search_text, sheet_name='Sheet1'):
    """
    Find cells containing specific text.

    Args:
        sheets_service: Sheets API service instance
        spreadsheet_id: ID of the spreadsheet
        search_text: Text to search for
        sheet_name: Sheet to search

    Returns:
        List of matches with cell references
    """
    values = read_all_values(sheets_service, spreadsheet_id, sheet_name)

    matches = []
    search_lower = search_text.lower()

    for row_idx, row in enumerate(values):
        for col_idx, cell in enumerate(row):
            if search_lower in str(cell).lower():
                col_letter = chr(ord('A') + col_idx) if col_idx < 26 else f'{chr(ord("A") + col_idx // 26 - 1)}{chr(ord("A") + col_idx % 26)}'

                matches.append({
                    'cell': f'{col_letter}{row_idx + 1}',
                    'row': row_idx + 1,
                    'column': col_idx + 1,
                    'value': cell
                })

    return matches


def query_sheet(sheets_service, spreadsheet_id, column_filters, sheet_name='Sheet1'):
    """
    Query sheet data with column filters.

    Args:
        sheets_service: Sheets API service instance
        spreadsheet_id: ID of the spreadsheet
        column_filters: Dict of {column_index: filter_value}
        sheet_name: Sheet to query

    Returns:
        Filtered rows
    """
    values = read_all_values(sheets_service, spreadsheet_id, sheet_name)

    if not values:
        return []

    headers = values[0] if values else []
    results = []

    for row in values[1:]:  # Skip header row
        match = True
        for col_idx, filter_value in column_filters.items():
            if col_idx >= len(row):
                match = False
                break
            if str(filter_value).lower() not in str(row[col_idx]).lower():
                match = False
                break

        if match:
            results.append(dict(zip(headers, row)))

    return results


def get_column_values(sheets_service, spreadsheet_id, column, sheet_name='Sheet1'):
    """
    Get all values from a specific column.

    Args:
        sheets_service: Sheets API service instance
        spreadsheet_id: ID of the spreadsheet
        column: Column letter (e.g., 'A') or index (0-based)
        sheet_name: Sheet name

    Returns:
        List of column values
    """
    if isinstance(column, int):
        column = chr(ord('A') + column)

    range_name = f'{sheet_name}!{column}:{column}'
    values = read_values(sheets_service, spreadsheet_id, range_name)

    return [row[0] if row else '' for row in values]


def find_row_by_value(sheets_service, spreadsheet_id, column, value, sheet_name='Sheet1'):
    """
    Find a row by a value in a specific column.

    Args:
        sheets_service: Sheets API service instance
        spreadsheet_id: ID of the spreadsheet
        column: Column to search
        value: Value to find
        sheet_name: Sheet name

    Returns:
        Row data as dictionary (with headers) or None
    """
    values = read_all_values(sheets_service, spreadsheet_id, sheet_name)

    if not values or len(values) < 2:
        return None

    headers = values[0]

    if isinstance(column, str):
        col_idx = ord(column.upper()) - ord('A')
    else:
        col_idx = column

    for row in values[1:]:
        if col_idx < len(row) and str(row[col_idx]) == str(value):
            return dict(zip(headers, row))

    return None
```

---

## 5. Google Slides API

The Google Slides API allows you to create and modify presentations.

### 5.1 Create Presentations

```python
# Python - Create presentations
def create_presentation(slides_service, title):
    """
    Create a new Google Slides presentation.

    Args:
        slides_service: Slides API service instance
        title: Presentation title

    Returns:
        Created presentation metadata
    """
    presentation = {
        'title': title
    }

    presentation = slides_service.presentations().create(
        body=presentation
    ).execute()

    return presentation


def create_presentation_with_slides(slides_service, title, slide_count=5):
    """
    Create a presentation with multiple blank slides.

    Args:
        slides_service: Slides API service instance
        title: Presentation title
        slide_count: Number of slides to create

    Returns:
        Created presentation
    """
    presentation = create_presentation(slides_service, title)
    presentation_id = presentation['presentationId']

    # Add additional slides (first slide is created automatically)
    requests = []
    for i in range(slide_count - 1):
        requests.append({
            'createSlide': {
                'insertionIndex': i + 1,
                'slideLayoutReference': {
                    'predefinedLayout': 'BLANK'
                }
            }
        })

    if requests:
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()

    return presentation
```

### 5.2 Read Presentations

```python
# Python - Read presentations
def get_presentation(slides_service, presentation_id):
    """
    Get presentation metadata and content.

    Args:
        slides_service: Slides API service instance
        presentation_id: ID of the presentation

    Returns:
        Presentation object
    """
    presentation = slides_service.presentations().get(
        presentationId=presentation_id
    ).execute()

    return presentation


def get_presentation_summary(slides_service, presentation_id):
    """
    Get a summary of the presentation.

    Args:
        slides_service: Slides API service instance
        presentation_id: ID of the presentation

    Returns:
        Dictionary with presentation summary
    """
    presentation = get_presentation(slides_service, presentation_id)

    summary = {
        'title': presentation.get('title'),
        'presentationId': presentation_id,
        'slideCount': len(presentation.get('slides', [])),
        'slides': []
    }

    for idx, slide in enumerate(presentation.get('slides', [])):
        slide_info = {
            'slideNumber': idx + 1,
            'objectId': slide['objectId'],
            'textContent': []
        }

        # Extract text from slide elements
        for element in slide.get('pageElements', []):
            if 'shape' in element and 'text' in element['shape']:
                text_elements = element['shape']['text'].get('textElements', [])
                for text_el in text_elements:
                    if 'textRun' in text_el:
                        content = text_el['textRun'].get('content', '').strip()
                        if content:
                            slide_info['textContent'].append(content)

        summary['slides'].append(slide_info)

    return summary


def get_slide_text(slides_service, presentation_id, slide_index=0):
    """
    Get all text content from a specific slide.

    Args:
        slides_service: Slides API service instance
        presentation_id: ID of the presentation
        slide_index: Index of the slide (0-based)

    Returns:
        List of text strings from the slide
    """
    presentation = get_presentation(slides_service, presentation_id)
    slides = presentation.get('slides', [])

    if slide_index >= len(slides):
        return []

    slide = slides[slide_index]
    text_content = []

    for element in slide.get('pageElements', []):
        if 'shape' in element and 'text' in element['shape']:
            text_elements = element['shape']['text'].get('textElements', [])
            for text_el in text_elements:
                if 'textRun' in text_el:
                    content = text_el['textRun'].get('content', '').strip()
                    if content:
                        text_content.append(content)

    return text_content


def get_all_presentation_text(slides_service, presentation_id):
    """
    Get all text content from the entire presentation.

    Args:
        slides_service: Slides API service instance
        presentation_id: ID of the presentation

    Returns:
        Dictionary mapping slide numbers to text content
    """
    presentation = get_presentation(slides_service, presentation_id)
    all_text = {}

    for idx, slide in enumerate(presentation.get('slides', [])):
        slide_text = []

        for element in slide.get('pageElements', []):
            if 'shape' in element and 'text' in element['shape']:
                text_elements = element['shape']['text'].get('textElements', [])
                for text_el in text_elements:
                    if 'textRun' in text_el:
                        content = text_el['textRun'].get('content', '').strip()
                        if content:
                            slide_text.append(content)

        all_text[idx + 1] = slide_text

    return all_text
```

### 5.3 Update Presentations

```python
# Python - Update presentations
def add_slide(slides_service, presentation_id, layout='BLANK', insertion_index=None):
    """
    Add a new slide to the presentation.

    Args:
        slides_service: Slides API service instance
        presentation_id: ID of the presentation
        layout: Slide layout (BLANK, TITLE, TITLE_AND_BODY, etc.)
        insertion_index: Position to insert (None = end)

    Returns:
        Created slide info
    """
    request = {
        'createSlide': {
            'slideLayoutReference': {
                'predefinedLayout': layout
            }
        }
    }

    if insertion_index is not None:
        request['createSlide']['insertionIndex'] = insertion_index

    result = slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': [request]}
    ).execute()

    return result['replies'][0]['createSlide']


def delete_slide(slides_service, presentation_id, slide_object_id):
    """
    Delete a slide from the presentation.

    Args:
        slides_service: Slides API service instance
        presentation_id: ID of the presentation
        slide_object_id: Object ID of the slide to delete
    """
    requests = [{
        'deleteObject': {
            'objectId': slide_object_id
        }
    }]

    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()


def add_text_box(slides_service, presentation_id, slide_object_id, text,
                 x=100, y=100, width=300, height=50):
    """
    Add a text box to a slide.

    Args:
        slides_service: Slides API service instance
        presentation_id: ID of the presentation
        slide_object_id: Object ID of the slide
        text: Text content
        x, y: Position in points
        width, height: Size in points

    Returns:
        Created element info
    """
    import uuid
    element_id = f'textbox_{uuid.uuid4().hex[:8]}'

    requests = [
        {
            'createShape': {
                'objectId': element_id,
                'shapeType': 'TEXT_BOX',
                'elementProperties': {
                    'pageObjectId': slide_object_id,
                    'size': {
                        'width': {'magnitude': width, 'unit': 'PT'},
                        'height': {'magnitude': height, 'unit': 'PT'}
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': x,
                        'translateY': y,
                        'unit': 'PT'
                    }
                }
            }
        },
        {
            'insertText': {
                'objectId': element_id,
                'text': text
            }
        }
    ]

    result = slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()

    return result


def replace_text_in_presentation(slides_service, presentation_id, old_text, new_text):
    """
    Replace all occurrences of text in the presentation.

    Args:
        slides_service: Slides API service instance
        presentation_id: ID of the presentation
        old_text: Text to find
        new_text: Replacement text

    Returns:
        Number of replacements
    """
    requests = [{
        'replaceAllText': {
            'containsText': {
                'text': old_text,
                'matchCase': True
            },
            'replaceText': new_text
        }
    }]

    result = slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()

    replies = result.get('replies', [])
    if replies:
        return replies[0].get('replaceAllText', {}).get('occurrencesChanged', 0)
    return 0
```

---

## 6. Python Implementation

### 6.1 Environment Setup

```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install required packages
uv add google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 6.2 Complete Authentication Module

Create `google_workspace_auth.py`:

```python
"""Google Workspace APIs Authentication Module."""
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Comprehensive scopes for full access
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/presentations',
]


def get_credentials(credentials_path: str = 'credentials.json',
                   token_path: str = 'token.json',
                   scopes: list = None):
    """
    Get or refresh OAuth credentials.

    Args:
        credentials_path: Path to OAuth credentials JSON
        token_path: Path to store/retrieve access tokens
        scopes: List of OAuth scopes (defaults to SCOPES)

    Returns:
        Authenticated credentials object
    """
    if scopes is None:
        scopes = SCOPES

    if not os.path.exists(credentials_path):
        raise FileNotFoundError(
            f"Credentials file not found at {credentials_path}. "
            "Download it from Google Cloud Console."
        )

    creds = None

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, scopes
            )
            creds = flow.run_local_server(port=0)

        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return creds


def get_drive_service(credentials_path: str = 'credentials.json',
                      token_path: str = 'token.json'):
    """Get Google Drive API service instance."""
    creds = get_credentials(credentials_path, token_path)
    return build('drive', 'v3', credentials=creds)


def get_docs_service(credentials_path: str = 'credentials.json',
                     token_path: str = 'token.json'):
    """Get Google Docs API service instance."""
    creds = get_credentials(credentials_path, token_path)
    return build('docs', 'v1', credentials=creds)


def get_sheets_service(credentials_path: str = 'credentials.json',
                       token_path: str = 'token.json'):
    """Get Google Sheets API service instance."""
    creds = get_credentials(credentials_path, token_path)
    return build('sheets', 'v4', credentials=creds)


def get_slides_service(credentials_path: str = 'credentials.json',
                       token_path: str = 'token.json'):
    """Get Google Slides API service instance."""
    creds = get_credentials(credentials_path, token_path)
    return build('slides', 'v1', credentials=creds)


def get_all_services(credentials_path: str = 'credentials.json',
                     token_path: str = 'token.json'):
    """
    Get all Google Workspace API service instances.

    Returns:
        Dictionary with 'drive', 'docs', 'sheets', 'slides' services
    """
    creds = get_credentials(credentials_path, token_path)

    return {
        'drive': build('drive', 'v3', credentials=creds),
        'docs': build('docs', 'v1', credentials=creds),
        'sheets': build('sheets', 'v4', credentials=creds),
        'slides': build('slides', 'v1', credentials=creds),
    }
```

### 6.3 Complete Drive Manager Module

Create `drive_manager.py`:

```python
"""Google Drive Management Module - Complete Implementation."""
from google_workspace_auth import get_drive_service
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
import os


class DriveManager:
    """Manager class for Google Drive operations."""

    def __init__(self, credentials_path='credentials.json', token_path='token.json'):
        """Initialize with credentials."""
        self.service = get_drive_service(credentials_path, token_path)

    # ==================== FILE OPERATIONS ====================

    def list_files(self, query=None, page_size=100, order_by='modifiedTime desc'):
        """List files with optional query filter."""
        files = []
        page_token = None

        while True:
            params = {
                'pageSize': min(page_size, 1000),
                'fields': 'nextPageToken, files(id, name, mimeType, parents, createdTime, modifiedTime, owners, size, webViewLink)',
                'orderBy': order_by,
                'supportsAllDrives': True,
            }

            if query:
                params['q'] = query
            if page_token:
                params['pageToken'] = page_token

            results = self.service.files().list(**params).execute()
            files.extend(results.get('files', []))

            page_token = results.get('nextPageToken')
            if not page_token or len(files) >= page_size:
                break

        return files[:page_size]

    def get_file(self, file_id):
        """Get file metadata."""
        return self.service.files().get(
            fileId=file_id,
            fields='*',
            supportsAllDrives=True
        ).execute()

    def create_folder(self, name, parent_id=None):
        """Create a folder."""
        metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            metadata['parents'] = [parent_id]

        return self.service.files().create(
            body=metadata,
            fields='id, name, webViewLink'
        ).execute()

    def upload_file(self, file_path, name=None, parent_id=None, mime_type=None):
        """Upload a file."""
        if name is None:
            name = os.path.basename(file_path)

        metadata = {'name': name}
        if parent_id:
            metadata['parents'] = [parent_id]

        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

        return self.service.files().create(
            body=metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()

    def download_file(self, file_id, output_path):
        """Download a file."""
        request = self.service.files().get_media(fileId=file_id)

        with io.FileIO(output_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()

        return output_path

    def export_google_file(self, file_id, mime_type, output_path):
        """Export a Google Docs/Sheets/Slides file."""
        request = self.service.files().export_media(
            fileId=file_id,
            mimeType=mime_type
        )

        with io.FileIO(output_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()

        return output_path

    def update_file(self, file_id, name=None, description=None):
        """Update file metadata."""
        metadata = {}
        if name:
            metadata['name'] = name
        if description:
            metadata['description'] = description

        return self.service.files().update(
            fileId=file_id,
            body=metadata,
            fields='id, name, description'
        ).execute()

    def delete_file(self, file_id, permanent=False):
        """Delete or trash a file."""
        if permanent:
            self.service.files().delete(fileId=file_id).execute()
        else:
            self.service.files().update(
                fileId=file_id,
                body={'trashed': True}
            ).execute()

    def restore_file(self, file_id):
        """Restore a file from trash."""
        self.service.files().update(
            fileId=file_id,
            body={'trashed': False}
        ).execute()

    # ==================== SEARCH OPERATIONS ====================

    def search(self, query):
        """Search with custom query."""
        return self.list_files(query=query)

    def find_by_name(self, name, exact=False):
        """Find files by name."""
        if exact:
            query = f"name = '{name}' and trashed = false"
        else:
            query = f"name contains '{name}' and trashed = false"
        return self.search(query)

    def find_docs(self, name_contains=None):
        """Find Google Docs."""
        query = "mimeType = 'application/vnd.google-apps.document' and trashed = false"
        if name_contains:
            query = f"name contains '{name_contains}' and " + query
        return self.search(query)

    def find_sheets(self, name_contains=None):
        """Find Google Sheets."""
        query = "mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
        if name_contains:
            query = f"name contains '{name_contains}' and " + query
        return self.search(query)

    def find_slides(self, name_contains=None):
        """Find Google Slides."""
        query = "mimeType = 'application/vnd.google-apps.presentation' and trashed = false"
        if name_contains:
            query = f"name contains '{name_contains}' and " + query
        return self.search(query)

    def find_folders(self, name_contains=None):
        """Find folders."""
        query = "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if name_contains:
            query = f"name contains '{name_contains}' and " + query
        return self.search(query)

    def find_in_folder(self, folder_id):
        """Find files in a specific folder."""
        query = f"'{folder_id}' in parents and trashed = false"
        return self.search(query)

    def find_shared_with_me(self):
        """Find files shared with me."""
        return self.search("sharedWithMe = true and trashed = false")

    def find_recent(self, days=7):
        """Find recently modified files."""
        from datetime import datetime, timedelta
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat() + 'Z'
        return self.search(f"modifiedTime > '{cutoff}' and trashed = false")

    def full_text_search(self, text):
        """Search file contents."""
        return self.search(f"fullText contains '{text}' and trashed = false")

    # ==================== ORGANIZATION OPERATIONS ====================

    def move_file(self, file_id, new_parent_id):
        """Move a file to a different folder."""
        file = self.service.files().get(
            fileId=file_id,
            fields='parents'
        ).execute()

        previous_parents = ','.join(file.get('parents', []))

        return self.service.files().update(
            fileId=file_id,
            addParents=new_parent_id,
            removeParents=previous_parents,
            fields='id, name, parents'
        ).execute()

    def copy_file(self, file_id, new_name=None, destination_folder_id=None):
        """Copy a file."""
        metadata = {}
        if new_name:
            metadata['name'] = new_name
        if destination_folder_id:
            metadata['parents'] = [destination_folder_id]

        return self.service.files().copy(
            fileId=file_id,
            body=metadata,
            fields='id, name, webViewLink'
        ).execute()

    def create_folder_path(self, path, root_id=None):
        """Create folder path, creating intermediates as needed."""
        folders = path.strip('/').split('/')
        parent_id = root_id

        for folder_name in folders:
            query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            if parent_id:
                query += f" and '{parent_id}' in parents"

            results = self.search(query)

            if results:
                parent_id = results[0]['id']
            else:
                new_folder = self.create_folder(folder_name, parent_id)
                parent_id = new_folder['id']

        return parent_id

    # ==================== PERMISSIONS OPERATIONS ====================

    def list_permissions(self, file_id):
        """List all permissions for a file."""
        return self.service.permissions().list(
            fileId=file_id,
            fields='permissions(id, type, role, emailAddress, domain, displayName, deleted)'
        ).execute().get('permissions', [])

    def share_with_user(self, file_id, email, role='reader', notify=True, message=None):
        """Share with a specific user."""
        permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email
        }

        return self.service.permissions().create(
            fileId=file_id,
            body=permission,
            sendNotificationEmail=notify,
            emailMessage=message,
            fields='id, type, role, emailAddress'
        ).execute()

    def share_with_group(self, file_id, group_email, role='reader'):
        """Share with a Google Group."""
        permission = {
            'type': 'group',
            'role': role,
            'emailAddress': group_email
        }

        return self.service.permissions().create(
            fileId=file_id,
            body=permission,
            fields='id, type, role, emailAddress'
        ).execute()

    def share_with_domain(self, file_id, domain, role='reader'):
        """Share with entire domain."""
        permission = {
            'type': 'domain',
            'role': role,
            'domain': domain
        }

        return self.service.permissions().create(
            fileId=file_id,
            body=permission,
            fields='id, type, role, domain'
        ).execute()

    def share_with_anyone(self, file_id, role='reader'):
        """Share with anyone (public link)."""
        permission = {
            'type': 'anyone',
            'role': role
        }

        return self.service.permissions().create(
            fileId=file_id,
            body=permission,
            fields='id, type, role'
        ).execute()

    def update_permission(self, file_id, permission_id, new_role):
        """Update a permission's role."""
        return self.service.permissions().update(
            fileId=file_id,
            permissionId=permission_id,
            body={'role': new_role},
            fields='id, type, role, emailAddress'
        ).execute()

    def revoke_permission(self, file_id, permission_id):
        """Revoke a permission."""
        self.service.permissions().delete(
            fileId=file_id,
            permissionId=permission_id
        ).execute()

    def revoke_access_by_email(self, file_id, email):
        """Revoke access for a user by email."""
        permissions = self.list_permissions(file_id)

        for perm in permissions:
            if perm.get('emailAddress', '').lower() == email.lower():
                self.revoke_permission(file_id, perm['id'])
                return True
        return False

    def get_sharing_summary(self, file_id):
        """Get a summary of who has access."""
        permissions = self.list_permissions(file_id)

        summary = {
            'owner': None,
            'editors': [],
            'commenters': [],
            'viewers': [],
            'anyone_with_link': False,
            'domain_access': []
        }

        for perm in permissions:
            role = perm.get('role')
            perm_type = perm.get('type')
            email = perm.get('emailAddress', '')

            if role == 'owner':
                summary['owner'] = email
            elif role == 'writer':
                if perm_type == 'anyone':
                    summary['anyone_with_link'] = 'edit'
                elif perm_type == 'domain':
                    summary['domain_access'].append({'domain': perm.get('domain'), 'role': 'editor'})
                else:
                    summary['editors'].append(email)
            elif role == 'commenter':
                summary['commenters'].append(email)
            elif role == 'reader':
                if perm_type == 'anyone':
                    summary['anyone_with_link'] = 'view'
                elif perm_type == 'domain':
                    summary['domain_access'].append({'domain': perm.get('domain'), 'role': 'viewer'})
                else:
                    summary['viewers'].append(email)

        return summary


# Example usage
if __name__ == '__main__':
    manager = DriveManager()

    # List recent files
    print("Recent files:")
    files = manager.find_recent(days=7)
    for f in files[:5]:
        print(f"  - {f['name']} ({f['mimeType']})")

    # Find Google Docs
    print("\nGoogle Docs:")
    docs = manager.find_docs()
    for doc in docs[:5]:
        print(f"  - {doc['name']}")
```

---

## 7. Node.js Implementation

### 7.1 Environment Setup

```bash
# Initialize project
npm init -y

# Install required packages
npm install googleapis @google-cloud/local-auth
```

### 7.2 Authentication Module

Create `google-workspace-auth.js`:

```javascript
/**
 * Google Workspace APIs Authentication Module for Node.js
 */
const fs = require('fs').promises;
const path = require('path');
const { authenticate } = require('@google-cloud/local-auth');
const { google } = require('googleapis');

// Comprehensive scopes
const SCOPES = [
  'https://www.googleapis.com/auth/drive',
  'https://www.googleapis.com/auth/documents',
  'https://www.googleapis.com/auth/spreadsheets',
  'https://www.googleapis.com/auth/presentations',
];

const TOKEN_PATH = path.join(process.cwd(), 'token.json');
const CREDENTIALS_PATH = path.join(process.cwd(), 'credentials.json');

/**
 * Load saved credentials if they exist.
 */
async function loadSavedCredentials() {
  try {
    const content = await fs.readFile(TOKEN_PATH);
    const credentials = JSON.parse(content);
    return google.auth.fromJSON(credentials);
  } catch (err) {
    return null;
  }
}

/**
 * Save credentials to file.
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
 * Get authenticated credentials.
 */
async function getCredentials() {
  let client = await loadSavedCredentials();
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
 * Get Drive service.
 */
async function getDriveService() {
  const auth = await getCredentials();
  return google.drive({ version: 'v3', auth });
}

/**
 * Get Docs service.
 */
async function getDocsService() {
  const auth = await getCredentials();
  return google.docs({ version: 'v1', auth });
}

/**
 * Get Sheets service.
 */
async function getSheetsService() {
  const auth = await getCredentials();
  return google.sheets({ version: 'v4', auth });
}

/**
 * Get Slides service.
 */
async function getSlidesService() {
  const auth = await getCredentials();
  return google.slides({ version: 'v1', auth });
}

/**
 * Get all services.
 */
async function getAllServices() {
  const auth = await getCredentials();
  return {
    drive: google.drive({ version: 'v3', auth }),
    docs: google.docs({ version: 'v1', auth }),
    sheets: google.sheets({ version: 'v4', auth }),
    slides: google.slides({ version: 'v1', auth }),
  };
}

module.exports = {
  getCredentials,
  getDriveService,
  getDocsService,
  getSheetsService,
  getSlidesService,
  getAllServices,
  SCOPES,
};
```

### 7.3 Drive Manager Module

Create `drive-manager.js`:

```javascript
/**
 * Google Drive Manager Module for Node.js
 */
const { getDriveService } = require('./google-workspace-auth');
const fs = require('fs');
const path = require('path');

class DriveManager {
  constructor() {
    this.service = null;
  }

  async init() {
    this.service = await getDriveService();
    return this;
  }

  // ==================== FILE OPERATIONS ====================

  async listFiles(query = null, pageSize = 100) {
    const files = [];
    let pageToken = null;

    do {
      const params = {
        pageSize: Math.min(pageSize, 1000),
        fields: 'nextPageToken, files(id, name, mimeType, parents, createdTime, modifiedTime, owners, webViewLink)',
        supportsAllDrives: true,
      };

      if (query) params.q = query;
      if (pageToken) params.pageToken = pageToken;

      const response = await this.service.files.list(params);
      files.push(...(response.data.files || []));
      pageToken = response.data.nextPageToken;
    } while (pageToken && files.length < pageSize);

    return files.slice(0, pageSize);
  }

  async getFile(fileId) {
    const response = await this.service.files.get({
      fileId,
      fields: '*',
      supportsAllDrives: true,
    });
    return response.data;
  }

  async createFolder(name, parentId = null) {
    const metadata = {
      name,
      mimeType: 'application/vnd.google-apps.folder',
    };
    if (parentId) metadata.parents = [parentId];

    const response = await this.service.files.create({
      requestBody: metadata,
      fields: 'id, name, webViewLink',
    });
    return response.data;
  }

  async deleteFile(fileId, permanent = false) {
    if (permanent) {
      await this.service.files.delete({ fileId });
    } else {
      await this.service.files.update({
        fileId,
        requestBody: { trashed: true },
      });
    }
  }

  // ==================== SEARCH OPERATIONS ====================

  async search(query) {
    return this.listFiles(query);
  }

  async findByName(nameContains) {
    return this.search(`name contains '${nameContains}' and trashed = false`);
  }

  async findDocs(nameContains = null) {
    let query = "mimeType = 'application/vnd.google-apps.document' and trashed = false";
    if (nameContains) query = `name contains '${nameContains}' and ${query}`;
    return this.search(query);
  }

  async findSheets(nameContains = null) {
    let query = "mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false";
    if (nameContains) query = `name contains '${nameContains}' and ${query}`;
    return this.search(query);
  }

  async findSlides(nameContains = null) {
    let query = "mimeType = 'application/vnd.google-apps.presentation' and trashed = false";
    if (nameContains) query = `name contains '${nameContains}' and ${query}`;
    return this.search(query);
  }

  async findInFolder(folderId) {
    return this.search(`'${folderId}' in parents and trashed = false`);
  }

  async fullTextSearch(text) {
    return this.search(`fullText contains '${text}' and trashed = false`);
  }

  // ==================== ORGANIZATION ====================

  async moveFile(fileId, newParentId) {
    const file = await this.service.files.get({
      fileId,
      fields: 'parents',
    });

    const previousParents = (file.data.parents || []).join(',');

    const response = await this.service.files.update({
      fileId,
      addParents: newParentId,
      removeParents: previousParents,
      fields: 'id, name, parents',
    });

    return response.data;
  }

  async copyFile(fileId, newName = null, destinationFolderId = null) {
    const metadata = {};
    if (newName) metadata.name = newName;
    if (destinationFolderId) metadata.parents = [destinationFolderId];

    const response = await this.service.files.copy({
      fileId,
      requestBody: metadata,
      fields: 'id, name, webViewLink',
    });

    return response.data;
  }

  // ==================== PERMISSIONS ====================

  async listPermissions(fileId) {
    const response = await this.service.permissions.list({
      fileId,
      fields: 'permissions(id, type, role, emailAddress, domain, displayName, deleted)',
    });
    return response.data.permissions || [];
  }

  async shareWithUser(fileId, email, role = 'reader', notify = true) {
    const response = await this.service.permissions.create({
      fileId,
      sendNotificationEmail: notify,
      requestBody: {
        type: 'user',
        role,
        emailAddress: email,
      },
      fields: 'id, type, role, emailAddress',
    });
    return response.data;
  }

  async shareWithAnyone(fileId, role = 'reader') {
    const response = await this.service.permissions.create({
      fileId,
      requestBody: {
        type: 'anyone',
        role,
      },
      fields: 'id, type, role',
    });
    return response.data;
  }

  async revokePermission(fileId, permissionId) {
    await this.service.permissions.delete({
      fileId,
      permissionId,
    });
  }

  async revokeAccessByEmail(fileId, email) {
    const permissions = await this.listPermissions(fileId);

    for (const perm of permissions) {
      if ((perm.emailAddress || '').toLowerCase() === email.toLowerCase()) {
        await this.revokePermission(fileId, perm.id);
        return true;
      }
    }
    return false;
  }

  async getSharingSummary(fileId) {
    const permissions = await this.listPermissions(fileId);

    const summary = {
      owner: null,
      editors: [],
      commenters: [],
      viewers: [],
      anyoneWithLink: false,
      domainAccess: [],
    };

    for (const perm of permissions) {
      const { role, type, emailAddress, domain } = perm;

      if (role === 'owner') {
        summary.owner = emailAddress;
      } else if (role === 'writer') {
        if (type === 'anyone') summary.anyoneWithLink = 'edit';
        else if (type === 'domain') summary.domainAccess.push({ domain, role: 'editor' });
        else summary.editors.push(emailAddress);
      } else if (role === 'commenter') {
        summary.commenters.push(emailAddress);
      } else if (role === 'reader') {
        if (type === 'anyone') summary.anyoneWithLink = 'view';
        else if (type === 'domain') summary.domainAccess.push({ domain, role: 'viewer' });
        else summary.viewers.push(emailAddress);
      }
    }

    return summary;
  }
}

module.exports = { DriveManager };

// Example usage
if (require.main === module) {
  (async () => {
    const manager = await new DriveManager().init();

    console.log('Recent Google Docs:');
    const docs = await manager.findDocs();
    docs.slice(0, 5).forEach((doc) => {
      console.log(`  - ${doc.name}`);
    });
  })();
}
```

---

## 8. Error Handling and Best Practices

### 8.1 Common Error Codes

| Error Code | Description | Solution |
|------------|-------------|----------|
| 400 | Bad Request | Check request parameters |
| 401 | Unauthorized | Token expired - re-authenticate |
| 403 | Forbidden | Check scopes, API enabled, quota |
| 404 | Not Found | Invalid file/folder ID |
| 429 | Rate Limit | Implement exponential backoff |
| 500 | Server Error | Retry with backoff |

### 8.2 Rate Limits

| API | Quota |
|-----|-------|
| Drive API | 12,000 requests/minute/project |
| Docs API | 300 requests/minute/project |
| Sheets API | 500 requests/100 seconds/project |
| Slides API | 500 requests/100 seconds/project |

### 8.3 Error Handling Pattern

```python
# Python - Retry with exponential backoff
from googleapiclient.errors import HttpError
import time
import random

def execute_with_retry(request, max_retries=5):
    """Execute API request with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return request.execute()
        except HttpError as error:
            if error.resp.status in [429, 500, 502, 503, 504]:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                raise
    raise Exception(f"Failed after {max_retries} retries")
```

### 8.4 Best Practices

1. **Use batch requests** - Combine multiple operations when possible
2. **Request only needed fields** - Use `fields` parameter to reduce response size
3. **Implement caching** - Cache file metadata to reduce API calls
4. **Handle pagination** - Always handle `nextPageToken` for list operations
5. **Use resumable uploads** - For files larger than 5MB
6. **Respect rate limits** - Implement exponential backoff

---

## 9. Quick Reference

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
- [Python Quickstart](https://developers.google.com/workspace/docs/api/quickstart/python)

### Google Sheets API
- [Sheets API Overview](https://developers.google.com/workspace/sheets/api/guides/concepts)
- [Sheets API Reference](https://developers.google.com/workspace/sheets/api/reference/rest)
- [Python Quickstart](https://developers.google.com/workspace/sheets/api/quickstart/python)
- [gspread Library](https://docs.gspread.org/)

### Google Slides API
- [Slides API Overview](https://developers.google.com/workspace/slides/api/guides/overview)
- [Slides API Reference](https://developers.google.com/workspace/slides/api/reference/rest)
- [Python Quickstart](https://developers.google.com/workspace/slides/api/quickstart/python)

### Client Libraries
- [Google API Python Client](https://github.com/googleapis/google-api-python-client)
- [Google API Node.js Client](https://github.com/googleapis/google-api-nodejs-client)
- [Python Client Library Docs](https://googleapis.github.io/google-api-python-client/docs/)

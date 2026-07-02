---
name: domusdocs
description: DomusDocs API for AI-powered document extraction at Alter Domus. Use this skill when working with document uploads, blueprints, batches, or extraction results.
license: Apache-2.0
---

# DomusDocs API

DomusDocs is an AI-powered document extraction platform. It uses configurable blueprints to extract structured data from uploaded documents (PDFs, images).

## Base URLs

| Environment | URL |
|-------------|-----|
| Development | `https://api.alterdomus.dev/domusdocs/v1` |
| Production | `https://api.alterdomus.com/domusdocs/v1` |

## Authentication

All requests require:
- `Authorization: Bearer {token}` - OAuth 2.0 access token
- `x-workspace-id: {workspace_id}` - Workspace UUID for tenant isolation

## Documents API

Manage individual document uploads and extraction.

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/documents` | GET | List documents (paginated, searchable, sortable) |
| `/documents` | POST | Create document entry and get presigned S3 upload URL |
| `/documents/{document_id}` | GET | Get document by ID |
| `/documents/{document_id}` | DELETE | Delete document |
| `/documents/{document_id}/start` | PUT | Start extraction processing |
| `/documents/{document_id}/reanalyze` | PUT | Re-run extraction on existing document |
| `/documents/{document_id}/results` | GET | Get extraction results |
| `/documents/{document_id}/export` | GET | Export results as Excel |
| `/documents/{document_id}/file` | GET | Get presigned download URL |

### Document Statuses

```
PENDING_UPLOAD -> UPLOADED -> CLASSIFICATION_IN_PROGRESS -> CLASSIFIED -> EXTRACTION_IN_PROGRESS -> COMPLETED
                                                                                                  -> ERROR
```

### Create Document

```bash
curl -X POST "https://api.alterdomus.dev/domusdocs/v1/documents" \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-workspace-id: $WORKSPACE_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "invoice.pdf",
    "mime_type": "application/pdf",
    "classification_type": "uuid-of-blueprint"
  }'
```

Response:
```json
{
  "id": "document-uuid",
  "filename": "invoice.pdf",
  "mime_type": "application/pdf",
  "status": "PENDING_UPLOAD",
  "presigned_url": "https://s3.amazonaws.com/..."
}
```

### Processing Flow

1. **Create** - `POST /documents` returns document ID and presigned S3 URL
2. **Upload** - `PUT` file to presigned URL
3. **Start** - `PUT /documents/{id}/start` triggers extraction
4. **Poll** - `GET /documents/{id}` until status is `COMPLETED` or `ERROR`
5. **Results** - `GET /documents/{id}/results` returns extracted data

## Batches API

Process multiple documents together with the same blueprint.

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/batches` | GET | List batches (paginated, searchable, sortable) |
| `/batches` | POST | Create new batch |
| `/batches/{batch_id}` | GET | Get batch details |
| `/batches/{batch_id}` | DELETE | Delete batch and all documents |
| `/batches/{batch_id}/documents` | GET | List documents in batch |
| `/batches/{batch_id}/documents` | POST | Add document to batch |
| `/batches/{batch_id}/documents/{document_id}` | DELETE | Remove document from batch |
| `/batches/{batch_id}/documents/{document_id}/file` | GET | Get document download URL |
| `/batches/{batch_id}/start` | PUT | Start processing all documents |
| `/batches/{batch_id}/rerun` | PUT | Re-run failed documents |
| `/batches/{batch_id}/results` | GET | Get all extraction results |
| `/batches/{batch_id}/export` | GET | Export results as Excel |

### Batch Statuses

```
CREATED -> IN_PROGRESS -> COMPLETED | COMPLETED_WITH_ERRORS | ERROR
```

### Create Batch

```bash
curl -X POST "https://api.alterdomus.dev/domusdocs/v1/batches" \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-workspace-id: $WORKSPACE_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "January Invoices",
    "classification_type": "uuid-of-blueprint"
  }'
```

### Batch Processing Flow

1. **Create Batch** - `POST /batches` with name and blueprint
2. **Add Documents** - `POST /batches/{id}/documents` for each file (returns presigned URLs)
3. **Upload Files** - `PUT` each file to its presigned URL
4. **Start Processing** - `PUT /batches/{id}/start`
5. **Monitor** - `GET /batches/{id}` shows `total`, `remaining`, `errored` counts
6. **Get Results** - `GET /batches/{id}/results` returns all extracted data

## Blueprints API

Configure extraction templates that define what data to extract.

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/blueprints` | GET | List blueprints |
| `/blueprints` | POST | Create blueprint |
| `/blueprints/{blueprint_id}` | GET | Get blueprint |
| `/blueprints/{blueprint_id}` | PUT | Update blueprint |
| `/blueprints/{blueprint_id}` | DELETE | Delete blueprint |
| `/blueprints/{blueprint_id}/versions` | GET | List versions |
| `/blueprints/{blueprint_id}/versions` | POST | Create new version |
| `/blueprints/{blueprint_id}/versions/{version}` | GET | Get version details |
| `/blueprints/{blueprint_id}/versions/{version}` | PUT | Update version |
| `/blueprints/{blueprint_id}/versions/{version}/export` | GET | Export as JSON |
| `/blueprints/{blueprint_id}/versions/import` | POST | Import from JSON |
| `/blueprints/imported` | GET | List imported blueprints |
| `/blueprints/{blueprint_id}/update-imported` | PUT | Update to latest marketplace version |

### Blueprint Version Structure

```json
{
  "id": "version-uuid",
  "blueprint_id": "blueprint-uuid",
  "version": 1,
  "published": false,
  "published_to_marketplace": false,
  "prompt_description": "Extract invoice information",
  "extraction_prompts": [
    {
      "name": "invoice_data",
      "prompt": "Extract the invoice details",
      "return_type": "object",
      "fields": [
        { "name": "invoice_number", "type": "string", "prompt": "The invoice number" },
        { "name": "total_amount", "type": "number", "prompt": "Total amount due" },
        { "name": "due_date", "type": "string", "prompt": "Payment due date" }
      ]
    },
    {
      "name": "line_items",
      "prompt": "Extract all line items",
      "return_type": "object_array",
      "fields": [
        { "name": "description", "type": "string", "prompt": "Item description" },
        { "name": "quantity", "type": "number", "prompt": "Quantity" },
        { "name": "unit_price", "type": "number", "prompt": "Price per unit" }
      ]
    }
  ]
}
```

### Extraction Prompt Types

| `return_type` | Description |
|---------------|-------------|
| `object` | Returns a single object with the defined fields |
| `object_array` | Returns an array of objects (e.g., line items, table rows) |

## Marketplace API

Share blueprints across workspaces within an organization.

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/marketplace/blueprints` | GET | List published blueprints |
| `/marketplace/blueprints/{id}` | GET | Get marketplace blueprint details |
| `/marketplace/blueprints/{id}/import` | POST | Import blueprint to workspace |

### Publishing Flow

1. Create and test blueprint in your workspace
2. Set `published: true` on the version
3. Set `published_to_marketplace: true` to share with organization
4. Other workspaces can import via marketplace

## Query Parameters

### Pagination

All list endpoints support:
- `page` - Page number (default: 1)
- `size` - Items per page (default: 20)

### Sorting (Documents & Batches)

- `sort_by` - Column to sort: `filename`, `status`, `created_at`, `blueprint_name`
- `sort_order` - `asc` or `desc`

### Search (Documents & Batches)

- `search` - Case-insensitive search across filename, status, blueprint name

## Response Format

### Paginated Response

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 20,
  "pages": 5,
  "next": "/documents?page=2",
  "previous": null
}
```

### Error Response

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Integration Example

```python
import httpx

class DomusDocsClient:
    def __init__(self, base_url: str, token: str, workspace_id: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "x-workspace-id": workspace_id,
        }

    def create_document(self, filename: str, blueprint_id: str) -> dict:
        response = httpx.post(
            f"{self.base_url}/documents",
            headers=self.headers,
            json={
                "filename": filename,
                "mime_type": "application/pdf",
                "classification_type": blueprint_id,
            }
        )
        return response.json()

    def upload_file(self, presigned_url: str, file_path: str):
        with open(file_path, "rb") as f:
            httpx.put(presigned_url, content=f.read())

    def start_processing(self, document_id: str) -> dict:
        response = httpx.put(
            f"{self.base_url}/documents/{document_id}/start",
            headers=self.headers
        )
        return response.json()

    def get_results(self, document_id: str) -> dict:
        response = httpx.get(
            f"{self.base_url}/documents/{document_id}/results",
            headers=self.headers
        )
        return response.json()
```

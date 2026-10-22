# Google Drive Integration

Read, write, and watch files in Google Drive from your workflows.

## Connecting

OAuth via your Google account. Helix requests these scopes:

- `drive.file` — Access only files Helix creates or that the user explicitly opens with Helix.
- `drive.readonly` — Read access to all files (optional, requested only if you opt in).

We default to the narrower scope unless you specifically need to read files Helix did not create.

## Triggers

- **New file in folder**: Fires when a file is added to a watched folder.
- **File modified**: Fires when a watched file is updated.
- **New row in Sheet**: Fires when a row is appended to a Google Sheet.

## Actions

- **Create file**: Upload a new file to Drive.
- **Read file**: Download file contents.
- **Update file**: Replace a file's contents.
- **Move file**: Move a file between folders.
- **Append row to Sheet**: Add a row to the bottom of a Sheet.
- **Update cell**: Set a specific cell's value.

## File size limits

Files up to 50 MB can be passed as data through workflows. For larger files, use the file's Drive ID and download/upload via the HTTP integration to avoid memory issues.

## Sheets pagination

When reading large Sheets, results are paginated at 1,000 rows per page. Use the **Read all rows** action with care on Sheets larger than 50,000 rows; consider filtering at the source.

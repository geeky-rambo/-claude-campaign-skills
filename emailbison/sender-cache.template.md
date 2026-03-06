# EmailBison Sender Cache

Read this file before attaching senders to any campaign.
If the current workspace has an entry, use the cached IDs and skip API pagination.
After fetching senders for a new workspace, append the IDs here.

**Setup:** Copy this file to `sender-cache.md` in the same directory.
Your local `sender-cache.md` is gitignored and will never be committed.

## [Workspace Name] (Workspace ID N)
- [Batch label]: ID, ID, ID, ...

## [Next Workspace] (Workspace ID N)
- All senders: ID, ID, ...

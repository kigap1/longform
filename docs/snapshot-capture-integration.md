# Snapshot Capture Integration Options

## Current boundary

- API and UI now persist snapshot metadata, storage location, project link, and evidence attachments.
- `SnapshotProviderPort` is the integration boundary for real capture engines.
- The default adapter is `MockSnapshotAdapter`, which stores a stub SVG and marks the capture as `stub`.

## Option 1: Playwright or browser automation

- Best fit when we need full-page or chart-area capture from arbitrary URLs.
- A real adapter can launch a browser, wait for selectors, capture PNG bytes, and return them through `SnapshotPayload`.
- Good for project-controlled workflows, but needs browser binaries, login/session handling, and retry logic.

## Option 2: Remote browser or capture worker

- Best fit when local API servers should stay lightweight.
- The adapter can call a separate capture service and receive image bytes plus metadata.
- Easier to scale and isolate flaky browser workloads, but adds network and queue orchestration.

## Option 3: Provider-native chart export

- Best fit when the source platform already exposes chart images or export endpoints.
- The adapter can skip a headless browser and directly download rendered assets.
- Lowest overhead, but only works for supported providers and often needs provider-specific mapping.

## Option 4: Browser extension or manual upload assist

- Best fit when human-guided capture is acceptable.
- The adapter boundary can be satisfied by uploading a user-created screenshot plus metadata.
- Fast to ship, but less automated and harder to standardize.

## What remains for real integrations

- URL allowlist and login/session policy
- capture wait conditions and crop/viewport rules
- retry, timeout, and job observability
- S3 preview URL generation or signed URL support
- source-specific compliance review for third-party sites

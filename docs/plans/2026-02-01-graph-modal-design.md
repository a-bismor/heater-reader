# Graph and Reading Modal Design

Date: 2026-02-01

## Goal

Redesign the readings graph to use a fixed temperature range (10-70), show evenly spaced time labels, and open an in-page modal when a label is clicked. The modal allows inline edits of the temperatures and mode.

## Scope

In scope:
- Chart: points connected by lines with y-axis range 10-70.
- X-axis label strip: formatted labels (DD-MM + line break + HH:MM) aligned evenly, clickable, and mapped to readings.
- In-page modal: show image and editable fields (boiler current/set, radiator current/set, mode) with Save action.
- Seed data: JSON fixtures and seed script already added to show sample data.

Out of scope:
- Editing captured_at timestamps.
- New backend endpoints unless required for image retrieval.

## Current State

- Chart.js line chart with labels set to captured_at strings.
- Table shows readings and uses contenteditable + blur to save edits.
- /api/readings returns effective readings sorted by captured_at.
- /api/readings/{id}/edit accepts edits.

## Proposed UI Structure

- Chart area: 50vh height, 100% width.
- Chart.js x-axis ticks hidden.
- Label strip below chart:
  - CSS grid with repeat(n, 1fr) columns to center one label and evenly distribute many.
  - Each label shows `DD-MM` and `HH:MM` on two lines.
  - Each label is clickable and opens modal for the reading id.
- Reading table:
  - Hidden when empty (already implemented).
  - Can remain below chart but not required for editing once modal is in place.

## Modal Behavior

- Opens on label click (label only; points are not clickable).
- Displays:
  - captured_at (read-only)
  - reading image
  - editable inputs: boiler_current, boiler_set, radiator_current, radiator_set, mode
- Save:
  - POST /api/readings/{id}/edit with edited fields and edited_by
  - Disable Save while request is in-flight
  - Close modal on success and refresh readings
  - Show error message on failure
- Close:
  - X button and Escape key

## Data Flow

1. GET /api/readings on page load.
2. Render chart and label strip from the same readings array.
3. On label click, open modal with data from readings array.
4. On Save, POST edits, then refresh readings and re-render chart/labels.

## Error Handling

- If modal save fails, keep modal open and show error text.
- If image is missing/unavailable, show placeholder text in modal.

## Testing Strategy

- UI tests: verify chart container exists and label strip is rendered in HTML.
- Unit tests for any new helper functions (date formatting, label rendering).
- Manual verification for modal click behavior (label only) and save flow.

## Open Questions

- Mode input: plain text or constrained options (defaults to plain text unless specified).
- Keep or remove the readings table once modal edits are in place.

# Phase 2 — F7: WhatsApp Notification Infrastructure + Final QA

## TL;DR

> **Quick Summary**: Complete the WhatsApp notification abstraction (fix corrupted file, create service, wire hooks into message/review endpoints), then run final E2E QA across all Phase 2 features.
>
> **Deliverables**:
> - Fixed `app/core/notifications.py` (clean Python syntax, no escaped quotes)
> - New `app/services/notification_service.py` (provider dispatch service)
> - Updated `app/core/config.py` (NotificationConfig + WhatsAppConfig)
> - Updated `.env.example` (WHATSAPP_* env vars)
> - Notification hooks in `send_message` and `create_review` services
> - Updated `README.md` with new endpoints and architecture
> - Final E2E QA: all features passing, server healthy
>
> **Estimated Effort**: Short (30-45 min)
> **Parallel Execution**: YES - Wave 1 (4 independent file tasks), Wave 2 (2 integration hooks), Wave 3 (final QA)

---

## Context

### Original Request
User asked to "lay the infra for integrating with WhatsApp" as the final backend feature.

### Interview Summary
**Key Discussions**:
- Notifications should use provider pattern: ConsoleProvider (dev) + WhatsAppProvider (prod stub)
- Trigger notifications on: new message received, new review posted
- WhatsApp Business API not yet configured — stub with TODO for later implementation
- Default to console provider in dev mode

### Current State
- `notifications.py` exists but has corrupted syntax (escaped `\"\"\"` instead of proper `"""`) — caused by PowerShell heredoc from subagent
- `notification_service.py` never created
- `config.py` missing NotificationConfig + WhatsAppConfig
- `.env.example` missing WhatsApp env vars
- No notification hooks in message/review services

---

## Work Objectives

### Core Objective
Complete F7: Build notification infrastructure with provider pattern, wire it into existing message/review flows, and do final QA.

### Concrete Deliverables
- `app/core/notifications.py` — fixed, clean Python
- `app/services/notification_service.py` — new file
- `app/core/config.py` — appended config classes
- `.env.example` — appended env vars
- `app/services/message_service.py` — notification hook on new message
- `app/services/review_service.py` — notification hook on new review

### Definition of Done
- [ ] `uv run python -c "from app.core.notifications import NotificationProvider, ConsoleProvider, WhatsAppProvider"` — no import errors
- [ ] `uv run python -c "from app.services.notification_service import notify_new_message, notify_new_review"` — no import errors
- [ ] Server starts without errors on port 8006
- [ ] Sending a message logs `[NOTIFICATION]` in console
- [ ] Creating a review logs `[NOTIFICATION]` in console
- [ ] All existing endpoints still work (no regressions)

### Must Have
- ConsoleProvider as default (dev mode)
- WhatsAppProvider stub with TODO for actual API implementation
- Notification triggered on new message (notify listing owner)
- Notification triggered on new review (notify seller)
- Clean, SOLID-compliant code matching existing patterns

### Must NOT Have (Guardrails)
- NO actual WhatsApp API calls (credentials not available)
- NO new collections or database changes
- NO changes to existing endpoint signatures
- NO breaking existing functionality

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (uv + Python import checks)
- **Automated tests**: NO (no test framework in project)
- **Agent-Executed QA**: YES (curl + server log assertions)

### QA Policy
Every task includes agent-executed QA scenarios with curl commands, server log checks, and evidence capture.

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately - 4 independent file tasks):
├── Task 1: Fix app/core/notifications.py [quick]
├── Task 2: Create app/services/notification_service.py [quick]
├── Task 3: Append to app/core/config.py [quick]
└── Task 4: Append to .env.example [quick]

Wave 2 (After Wave 1 - notification hooks):
├── Task 5: Wire notification into message_service.py [quick]
└── Task 6: Wire notification into review_service.py [quick]

Wave 3 (After Wave 2 - verification):
├── Task 7: Import verification + server restart + E2E smoke test [unspecified-high]
└── Task 8: Update README.md with new features [writing]

Critical Path: Tasks 1-4 → Tasks 5-6 → Tasks 7-8
Max Concurrent: 4
```

### Dependency Matrix
- **1**: - (no deps)
- **2**: 1, 3 (needs notifications.py + config to be ready)
- **3**: - (no deps)
- **4**: - (no deps)
- **5**: 2, 6 (needs notification service + message service context)
- **6**: 2, 3 (needs notification service + config)
- **7**: 5, 6 (needs all hooks wired)
- **8**: 7 (after verification passes)

---

## TODOs

- [ ] 1. Fix `app/core/notifications.py` — replace corrupted file with clean syntax

  **What to do**:
  - Rewrite `app/core/notifications.py` with proper Python `"""` docstrings (not escaped `\"\"\"`)
  - Keep the exact same class structure: NotificationProvider (ABC), ConsoleProvider, WhatsAppProvider
  - Use `%s` formatting in logger calls (not f-strings) for lazy evaluation
  - Keep the WhatsApp API call commented out with TODO

  **Must NOT do**:
  - Change class names or method signatures
  - Remove the TODO comment for actual API implementation

  **Recommended Agent Profile**:
  - **Category**: `quick` — single file rewrite, straightforward
  - **Skills**: `[]` — no specialized skills needed
  - **Skills Evaluated but Omitted**: none needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 3, 4)
  - **Blocks**: Task 2 (needs notifications.py), Task 5
  - **Blocked By**: None

  **References**:
  - `app/core/notifications.py` — the corrupted file to replace
  - `app/core/exceptions.py` — reference for clean docstring style
  - `app/core/config.py` — reference for logging pattern

  **Acceptance Criteria**:
  - `uv run python -c "from app.core.notifications import NotificationProvider, ConsoleProvider, WhatsAppProvider"` exits 0
  - File has proper `"""` docstrings, not `\"\"\"`

  **QA Scenarios**:
  ```
  Scenario: Import all notification classes
    Tool: Bash (python)
    Steps:
      1. cd D:\AHMED_DATA\Projects\test_used_website
      2. uv run python -c "from app.core.notifications import NotificationProvider, ConsoleProvider, WhatsAppProvider; print('OK')"
    Expected: Output contains "OK", exit code 0
    Evidence: .sisyphus/evidence/task-1-import-check.txt
  ```

- [ ] 2. Create `app/services/notification_service.py` — provider dispatch service

  **What to do**:
  - Create new file with `get_provider()` singleton function
  - Implement 3 notification functions: `notify_new_message`, `notify_new_review`, `notify_listing_sold`
  - Import `notification_config` from `app.core.config`
  - Import `ConsoleProvider`, `WhatsAppProvider` from `app.core.notifications`
  - Lazy-init provider based on `notification_config.provider` (default: "console")

  **Must NOT do**:
  - Create new database connections
  - Add HTTP endpoints (this is service-layer only)

  **Recommended Agent Profile**:
  - **Category**: `quick` — single file creation following existing service patterns
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (after Tasks 1 and 3 are done)
  - **Parallel Group**: Wave 1 (logically depends on 1+3, can run in parallel since those are just file writes)
  - **Blocks**: Tasks 5, 6
  - **Blocked By**: Task 1, Task 3

  **References**:
  - `app/services/message_service.py` — service module style reference
  - `app/services/review_service.py` — service module style reference
  - `app/core/config.py` — for `notification_config` import
  - `app/core/notifications.py` — for provider class imports

  **Acceptance Criteria**:
  - `uv run python -c "from app.services.notification_service import notify_new_message, notify_new_review, notify_listing_sold; print('OK')"` exits 0

  **QA Scenarios**:
  ```
  Scenario: Import all notification service functions
    Tool: Bash (python)
    Steps:
      1. cd D:\AHMED_DATA\Projects\test_used_website
      2. uv run python -c "from app.services.notification_service import notify_new_message, notify_new_review, notify_listing_sold; print('OK')"
    Expected: Output contains "OK", exit code 0
    Evidence: .sisyphus/evidence/task-2-import-check.txt
  ```

- [ ] 3. Append NotificationConfig + WhatsAppConfig to `app/core/config.py`

  **What to do**:
  - Append two new classes after line 60 (after `database_config = DatabaseConfig()`)
  - `NotificationConfig`: property `provider` → reads `NOTIFICATION_PROVIDER` env var, defaults to "console"
  - `WhatsAppConfig`: properties `token`, `phone_number_id`, `template_name` → read respective env vars
  - Append singleton instances: `notification_config = NotificationConfig()`, `whatsapp_config = WhatsAppConfig()`

  **Must NOT do**:
  - Modify existing config classes
  - Change import structure

  **Recommended Agent Profile**:
  - **Category**: `quick` — simple append to existing file
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 4)
  - **Blocks**: Task 2 (notification_service imports notification_config)
  - **Blocked By**: None

  **References**:
  - `app/core/config.py:48-60` — DatabaseConfig pattern to follow for new classes
  - `app/core/config.py:34-37` — env var reading pattern

  **Acceptance Criteria**:
  - `uv run python -c "from app.core.config import notification_config, whatsapp_config; print(notification_config.provider)"` outputs "console"

  **QA Scenarios**:
  ```
  Scenario: Import and use new config classes
    Tool: Bash (python)
    Steps:
      1. cd D:\AHMED_DATA\Projects\test_used_website
      2. uv run python -c "from app.core.config import notification_config, whatsapp_config; print('provider:', notification_config.provider, '| token:', whatsapp_config.token)"
    Expected: Output "provider: console | token: " (empty token), exit code 0
    Evidence: .sisyphus/evidence/task-3-config-check.txt
  ```

- [ ] 4. Append WhatsApp env vars to `.env.example`

  **What to do**:
  - Append blank line + comment + 3 env vars to `.env.example`
  - `NOTIFICATION_PROVIDER=console`
  - `WHATSAPP_TOKEN=`
  - `WHATSAPP_PHONE_NUMBER_ID=`
  - `WHATSAPP_TEMPLATE_NAME=notification_template`

  **Must NOT do**:
  - Modify existing env vars
  - Change file encoding

  **Recommended Agent Profile**:
  - **Category**: `quick` — 5-line append
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3)
  - **Blocks**: None
  - **Blocked By**: None

  **References**:
  - `.env.example` — current file to append to

  **Acceptance Criteria**:
  - File ends with WHATSAPP_TEMPLATE_NAME line
  - All 4 new env vars present

  **QA Scenarios**:
  ```
  Scenario: Verify .env.example has WhatsApp vars
    Tool: Bash (powershell)
    Steps:
      1. Select-String -Path ".env.example" -Pattern "WHATSAPP" | Measure-Object
    Expected: Count >= 3
    Evidence: .sisyphus/evidence/task-4-env-check.txt
  ```

- [ ] 5. Wire notification hook into `send_message` in `app/services/message_service.py`

  **What to do**:
  - Add `import` for `notify_new_message` from `app.services.notification_service` at top of file
  - After successful `insert_one` in `send_message()`, add async notification call:
    - Look up the listing to get title and owner phone
    - Call `await notify_new_message(recipient_phone, sender_name, listing_title)`
  - The notification should be fire-and-forget (wrapped in try/except to not break messaging if notification fails)

  **Must NOT do**:
  - Change the return value of `send_message`
  - Raise exceptions if notification fails
  - Add notification as a required step

  **Recommended Agent Profile**:
  - **Category**: `quick` — add 5-10 lines to existing function
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Tasks 1-4)
  - **Parallel Group**: Wave 2 (with Task 6)
  - **Blocks**: Task 7
  - **Blocked By**: Tasks 1, 2, 3, 4

  **References**:
  - `app/services/message_service.py:26-50` — `send_message` function to modify
  - `app/services/message_service.py:87-96` — `get_listing_owner` helper (can be reused to get seller info)
  - `app/services/notification_service.py` — notification functions to call
  - `app/repositories/user_repo.py` — how to get user phone by ID

  **Acceptance Criteria**:
  - `send_message` still returns the same dict structure
  - Notification is called after message insert
  - Notification failure does not affect message creation

  **QA Scenarios**:
  ```
  Scenario: Send message triggers notification log
    Tool: Bash (curl)
    Steps:
      1. Sign in to get JWT token
      2. Create a laptop listing
      3. Sign in as different user (or use same with different account)
      4. POST /api/messages with sender_id, recipient_id (listing owner), listing_id, listing_type="laptop", content="Is this available?"
    Expected: Response 201 with message data, server console shows "[NOTIFICATION]" line
    Evidence: .sisyphus/evidence/task-5-message-notification.txt
  ```

- [ ] 6. Wire notification hook into `create_review` in `app/services/review_service.py`

  **What to do**:
  - Add `import` for `notify_new_review` from `app.services.notification_service` at top of file
  - After successful `insert_one` in `create_review()`, add async notification call:
    - Look up the reviewer to get their name
    - Call `await notify_new_review(seller_phone, reviewer_name, rating)`
  - Fire-and-forget (try/except)

  **Must NOT do**:
  - Change the return value of `create_review`
  - Raise exceptions if notification fails

  **Recommended Agent Profile**:
  - **Category**: `quick` — add 5-10 lines to existing function
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Tasks 1-4)
  - **Parallel Group**: Wave 2 (with Task 5)
  - **Blocks**: Task 7
  - **Blocked By**: Tasks 1, 2, 3, 4

  **References**:
  - `app/services/review_service.py:26-56` — `create_review` function to modify
  - `app/services/notification_service.py` — notification functions to call
  - `app/repositories/user_repo.py` — how to get user phone by ID

  **Acceptance Criteria**:
  - `create_review` still returns the same dict structure
  - Notification is called after review insert
  - Notification failure does not affect review creation

  **QA Scenarios**:
  ```
  Scenario: Create review triggers notification log
    Tool: Bash (curl)
    Steps:
      1. Sign in as user A, create laptop listing
      2. Sign in as user B, POST /api/reviews/seller/{userA_id} with rating=5, comment="Great seller!"
    Expected: Response 201 with review data, server console shows "[NOTIFICATION]" line
    Evidence: .sisyphus/evidence/task-6-review-notification.txt
  ```

- [ ] 7. Import verification + server restart + E2E smoke test

  **What to do**:
  - Verify all imports work (notifications, notification_service, config classes)
  - Kill existing server process on port 8006
  - Restart server with `uv run uvicorn app.main:app --reload --port 8006`
  - Run smoke tests: signin, create listing, send message, create review
  - Verify `[NOTIFICATION]` appears in server logs for message and review
  - Run `lsp_diagnostics` on `app/` — must be 0 errors

  **Must NOT do**:
  - Modify any code files
  - Skip notification verification

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high` — requires multi-step verification, server management
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Tasks 5, 6)
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 8
  - **Blocked By**: Tasks 5, 6

  **Acceptance Criteria**:
  - Server starts without errors
  - All smoke test endpoints return expected status codes
  - Notification logs appear for message and review
  - LSP diagnostics: 0 errors

  **QA Scenarios**:
  ```
  Scenario: Full E2E smoke test with notifications
    Tool: Bash (curl)
    Steps:
      1. POST /api/auth/signin → get token
      2. POST /api/laptops → create listing, save ID
      3. POST /api/messages → send message about listing
      4. Check server logs for "[NOTIFICATION]" 
      5. POST /api/reviews/seller/{id} → create review
      6. Check server logs for "[NOTIFICATION]"
    Expected: All endpoints 200/201, notification logs present
    Evidence: .sisyphus/evidence/task-7-e2e-smoke.txt
  ```

- [ ] 8. Update README.md with Phase 2 endpoints and notification infrastructure

  **What to do**:
  - Add new endpoint sections: Search/Filtering, Refresh Tokens, User Profiles, Favorites, Reviews, Messaging
  - Add notification infrastructure description to Architecture section
  - Update project structure tree with new files
  - Add new environment variables table entries

  **Must NOT do**:
  - Remove existing documentation
  - Add frontend instructions

  **Recommended Agent Profile**:
  - **Category**: `writing` — documentation update
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Task 7 verification)
  - **Parallel Group**: Wave 3
  - **Blocks**: None
  - **Blocked By**: Task 7

  **Acceptance Criteria**:
  - README includes all Phase 2 endpoints
  - Project structure tree includes new files
  - Environment variables table includes notification vars

---

## Final Verification Wave (MANDATORY)

- [ ] F1. **Plan Compliance Audit** — `oracle`
- [ ] F2. **Code Quality Review** — `unspecified-high`
- [ ] F3. **Real Manual QA** — `unspecified-high`
- [ ] F4. **Scope Fidelity Check** — `deep`

---

## Commit Strategy

- **Wave 1 (Tasks 1-4)**: `feat(notifications): add notification provider infrastructure`
  - Files: `app/core/notifications.py`, `app/services/notification_service.py`, `app/core/config.py`, `.env.example`
- **Wave 2 (Tasks 5-6)**: `feat(notifications): wire notification hooks into message and review services`
  - Files: `app/services/message_service.py`, `app/services/review_service.py`
- **Wave 3 (Tasks 7-8)**: `docs: update README with Phase 2 endpoints and notification features`
  - Files: `README.md`

---

## Success Criteria

### Verification Commands
```bash
uv run python -c "from app.core.notifications import NotificationProvider, ConsoleProvider, WhatsAppProvider; print('OK')"
uv run python -c "from app.services.notification_service import notify_new_message; print('OK')"
uv run uvicorn app.main:app --reload --port 8006  # Starts without errors
```

### Final Checklist
- [ ] All imports work (0 import errors)
- [ ] Server starts cleanly
- [ ] Message sending triggers `[NOTIFICATION]` log
- [ ] Review creation triggers `[NOTIFICATION]` log
- [ ] All existing endpoints still work (no regressions)
- [ ] LSP diagnostics: 0 errors
- [ ] README updated with Phase 2 features

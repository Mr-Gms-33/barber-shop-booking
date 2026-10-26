# Barber Shop Online Booking — Project Handoff

**Audience:** Implementation agents (full-stack, platform, QA, observability).  
**Language:** English (course requirement for documentation).  
**Scope of this document:** Product and functionality only. **Technology stack is not decided here** — choose stack separately unless the owner specifies otherwise.

**Owner:** Mounir (data scientist).  
**App concept:** Single barber shop — customers book online; admins approve, assign barbers when needed, checkout visits, and view history plus sales dashboard.

---

## 1. Course context (why this app exists)

This is the **Final Project** for an AI/dev course. One application end-to-end, not four separate assignments. Deliverables expected over time (for platform/SRE agents, not all in this spec):

| Area | Expectation |
|------|-------------|
| Spec | Problem + acceptance criteria before heavy coding; public task tracker with evidence agents used it |
| App | Frontend + backend + persistent database; full E2E; run locally with a single command |
| Tests | Unit + integration (+ frontend tests as applicable); one command to run and pass |
| Containers | Full system including DB via Docker Compose; one command start |
| Deploy | Public URL or clear demo |
| CI/CD | Tests on PR; CD to dev; manual prod deploy (ideal: 3-point rubric) |
| Observability | Key user journey: metrics, traces, structured logs with shared trace ID; viewable UI |
| Alerting | At least one alert on **user impact**, not CPU-only |
| Responder | Agent that wakes on alert and addresses/fixes the issue |
| Docs | `AGENTS.md` (+ modular docs); README describes problem and behavior |
| Peer review | Owner must review 3 other projects (process, not build) |

This handoff covers **product specification** so build agents can implement features and acceptance criteria while platform agents satisfy the rows above.

---

## 2. Problem statement

Small barber shops spend time on phone bookings and risk double-booking. Customers want to choose a **service**, **time**, and optionally a **barber** without calling. Staff need one place to **approve** requests, **assign** a barber when the customer did not choose one, **check out** after the service (record revenue), and see **appointment history** and **sales** — without adopting a generic unrelated product.

---

## 3. Brainstorming decisions (functionality)

All answers came from structured Q&A with the project owner. **Do not change these without owner approval.**

| Topic | Decision |
|-------|----------|
| Booking confirmation | Stays **pending** until admin **accepts** (customer sees waiting state) |
| Customer chose barber but slot busy | **Suggest** nearby times and/or other barbers for the same service (do not silently fail) |
| Services | **Fixed catalog**: name, duration, price — admin can edit catalog |
| Customer accounts | **Guest booking** (name + contact); optional registered account may come later — **not required in v1** |
| Payment | **Pay at shop only** — booking reserves a slot; no online payment in v1 |
| Cancel / reschedule | Customer can **both** cancel and reschedule until **2 hours** before appointment start |
| Admin accept + barber | If customer chose a barber → accept with that barber; if **“any barber”** → admin **picks barber on accept** |
| Reject booking | Admin can reject; customer sees **“declined” only** (no reason message) |
| Sales dashboard | Focus on **revenue from completed** appointments (plus sensible breakdowns — see §6) |
| When revenue counts | Admin **checkout** at visit: mark completed and record revenue; **final price adjustable** at checkout if needed |
| Shop scope | **Single shop** only in v1 |
| Availability | Admin sets **weekly working hours per barber** (shop closed days / exceptions are reasonable to include if simple) |
| Customer notifications | **No email/SMS in v1** — customer checks **“my booking”** via link or booking code |
| Cancel/reschedule cutoff | **2 hours** before start (should be configurable constant for prod hardening) |

---

## 4. Open decision (owner has not answered yet)

| Question | Options | Impact |
|----------|---------|--------|
| Guest contact fields | Phone only / email only / both required | Validation, “my booking” lookup (code-only vs code + phone verification) |

**Default recommendation for implementers if owner does not reply:** require **phone** + **name**; optional email; status page accessed by **booking code** (and optionally last 4 digits of phone for light verification).

---

## 5. Personas

### Customer (guest)

- Wants fast booking, optional barber preference, clear status after submit.
- Pays in person; cares about not being double-booked.
- Uses status page instead of notifications in v1.

### Admin (shop staff / owner)

- Manages catalog, barbers, and weekly schedules.
- Works a **pending queue** (accept / reject).
- Runs **checkout** to complete visits and record revenue.
- Uses **history** and **sales dashboard** for operations.

### Barber (v1)

- No separate login in v1; barbers are **entities** managed by admin (name, active flag, hours).
- Future: barber self-service availability is out of scope.

---

## 6. User journeys

### 6.1 Customer — create booking

1. Open public booking UI (single shop — no location picker).
2. Select one or more services from catalog (if multi-service per visit is allowed, see §7; otherwise one service per booking).
3. Select date/time from available slots (respect barber hours + existing confirmed/pending holds — define hold rules in §7).
4. Choose **specific barber** or **any available barber**.
5. If choice is invalid: show **suggestions** (alternate times/barbers).
6. Enter guest details (name + contact per §4).
7. Submit → booking status **`pending`**.
8. Show **booking code** + link to **my booking** status page.

### 6.2 Customer — my booking

1. Open status URL or enter booking code (and verification if implemented).
2. See status: `pending` | `confirmed` | `declined` | `cancelled` | `completed`.
3. If more than 2 hours before start and status allows: **cancel** or **reschedule** (reschedule reuses slot/suggestion rules).

### 6.3 Admin — accept or reject

1. View **pending** list (and/or calendar).
2. **Accept:** `pending` → `confirmed`; set barber per rules in §3.
3. **Reject:** `pending` → `declined` (customer-facing message: declined only).

### 6.4 Admin — checkout (revenue)

1. From confirmed (or in-progress) appointment, open **checkout**.
2. Default revenue = catalog price (sum if multiple services); admin may **adjust** final amount.
3. Save → status **`completed`**; revenue stored for dashboard and history.

### 6.5 Admin — dashboard & history

1. **History:** filterable list (date range, barber, status).
2. **Dashboard:** totals and breakdown for **completed** revenue in a selected period (minimum: total revenue; recommended: by day, by service, by barber).

---

## 7. Functional requirements (detailed)

### 7.1 Service catalog

- Fields: name, duration (minutes), price (currency — single currency for v1).
- Admin: create, read, update, deactivate/delete (prefer soft-delete if appointments reference services).
- Customer: read active services only.

### 7.2 Barbers

- Fields: display name, active/inactive.
- Admin CRUD.
- Customer sees only active barbers.

### 7.3 Availability

- Per barber: weekly schedule (e.g. day-of-week + start/end times).
- Optional: shop-wide closed days or barber time off (implement if low effort; otherwise document as v1.1).
- Slot generation uses service **duration**; no overlapping appointments for the same barber.

### 7.4 Appointments / bookings

**Suggested status enum:**

- `pending` — awaiting admin
- `confirmed` — accepted by admin
- `declined` — rejected by admin
- `cancelled` — cancelled by customer or admin (define who can admin-cancel)
- `completed` — checked out

**Core fields (conceptual):**

- Guest name, contact
- Service(s) — see open point below
- Start datetime (end = start + duration, or explicit end)
- Barber: assigned barber id, or flag “customer requested any”
- Booking code (public reference for status page)
- Timestamps: created, updated, confirmed, completed
- Revenue amount (set at checkout)

**Open product point — one service vs many per booking:**

- Owner did not specify. **Recommendation:** one service per appointment in v1 to simplify slots and checkout; note in tracker if extended.

**Open product point — do pending bookings block slots?**

- **Recommendation:** yes — treat `pending` and `confirmed` as blocking the barber slot to avoid overbooking while admin works the queue; release on `declined` / `cancelled`.

### 7.5 Suggestions when barber/time unavailable

- When customer selects unavailable barber/time: return alternates (same service):
  - Same barber, nearby times, and/or
  - Same time (or nearby), other barbers
- UX: customer picks from suggestions; no “force submit for admin to fix later” (owner rejected that option).

### 7.6 Cancel and reschedule rules

- Allowed only if appointment start is **more than 2 hours** away (server-side enforcement).
- Reschedule: same validation as new booking; status may return to `pending` if business requires re-approval — **owner did not specify**. **Recommendation:** rescheduled bookings go to **`pending`** again so admin can accept; document clearly for customer on status page.

### 7.7 Admin authorization

- Admin interface is authenticated; public booking and status page are not.
- Role model in v1: single **admin** role is enough unless course security requirements need more.

---

## 8. Acceptance criteria (task-tracker ready)

Copy into issues/tasks; each item should be testable.

### Catalog & barbers & availability

- [ ] Admin can create/edit/deactivate services with name, duration, and price.
- [ ] Admin can create/edit/deactivate barbers.
- [ ] Admin can set weekly working hours per barber.
- [ ] Customer cannot book inactive barbers or inactive services.
- [ ] System prevents double-booking the same barber for overlapping times.
- [ ] Pending and confirmed appointments block slots (unless product owner changes this).

### Customer booking

- [ ] Guest can submit a booking with name and contact fields (per §4 default).
- [ ] Customer can select service, time, and specific or any barber.
- [ ] New booking is `pending` immediately after submit.
- [ ] Customer receives booking code and can open status page without account.
- [ ] If selected barber/time invalid, UI offers suggestions and allows choosing an alternative.

### Customer cancel / reschedule

- [ ] Cancel succeeds when >2h before start; fails with clear message inside cutoff.
- [ ] Reschedule succeeds when >2h before start; fails inside cutoff.
- [ ] Reschedule follows slot and suggestion rules.

### Admin workflow

- [ ] Admin can list/filter pending bookings.
- [ ] Accept moves `pending` → `confirmed` and assigns barber per §3 rules.
- [ ] Reject moves `pending` → `declined`; customer status shows declined without reason text.
- [ ] Admin can view history with filters (date, barber, status).

### Checkout & dashboard

- [ ] Admin can checkout a confirmed appointment → `completed`.
- [ ] Checkout records revenue with optional price adjustment from catalog default.
- [ ] Dashboard shows total completed revenue for a date range.
- [ ] Dashboard shows at least one breakdown (by service, barber, or day — implement all three if time allows).

### Non-functional (for course — assign to platform agent)

- [ ] README describes problem, behavior, and how to run locally (one command).
- [ ] `AGENTS.md` describes agent roles and links to modular docs (process, deploy, observability).
- [ ] Public task tracker linked from README with tasks tied to §8 criteria.
- [ ] Tests, Docker, deploy, CI/CD, observability, alert, responder — per §1.

---

## 9. Explicitly out of scope (v1)

- Online payments (deposit or full).
- Email/SMS/push notifications.
- Multiple shop locations.
- Barber login and self-managed calendars.
- Customer registration/login (optional future).
- Rejection reasons visible to customer.
- Auto-confirm without admin accept.

---

## 10. Suggested agent team (for `AGENTS.md`)

| Agent / role | Responsibility |
|--------------|----------------|
| Product / spec | Keep tracker in sync with §8; resolve §4 and §7 open points with owner |
| Full-stack | API + DB schema + customer UI + admin UI |
| QA | Unit tests (domain rules: cutoff, overlap, status transitions); integration tests (API + DB); frontend tests for critical flows |
| Platform | Docker Compose, deploy, CI/CD (test on PR, deploy dev, manual prod + rollback path) |
| SRE / observability | Instrument **booking journey** (submit → confirm → checkout); trace ID across logs; user-impact alert (e.g. spike in failed bookings or checkout errors); **responder agent** runbook |

---

## 11. Key domain rules (quick reference for implementers)

```
pending --accept--> confirmed --checkout--> completed
pending --reject--> declined
pending|confirmed --cancel (customer if >2h)--> cancelled
confirmed --reschedule--> pending (recommended) or confirmed (only if owner says no re-approval)

Barber on accept:
  customer picked barber     -> keep that barber
  customer picked "any"      -> admin selects barber on accept

Payment: none online; revenue recorded at admin checkout only.
Cutoff: 2 hours before start for customer cancel/reschedule.
```

---

## 12. Recommended next steps for the next agent

1. Confirm §4 (contact fields) and §7 open points (multi-service, reschedule → pending vs confirmed) with owner or apply documented defaults.
2. Create `README.md` (problem + how to run) and `AGENTS.md` (team + links).
3. Create public task tracker; one task per §8 checkbox.
4. Propose stack and data model; get owner sign-off if required.
5. Implement vertical slice: guest book → admin accept → checkout → dashboard metric.
6. Add tests, containers, deploy, CI/CD, then observability + alert + responder per course rubric.

---

## 13. Document history

| Date | Event |
|------|--------|
| 2026-10-26 | Initial brainstorming with owner; decisions captured in this handoff |
| 2026-10-26 | Implementation started: FastAPI + React + Postgres; §4 defaults applied (phone+name, code+last4) |

---

*End of handoff. Do not infer technology choices from this file.*

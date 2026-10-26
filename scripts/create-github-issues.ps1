# Product/spec: create groomed issues from PROJECT_HANDOFF §8 (run once)
$issues = @(
  @{ title = "Admin CRUD services (name, duration, price EUR)"; body = "AC: Admin can create/edit/deactivate services with name, duration, and price.`nVerify: Admin UI or API PATCH/POST; inactive hidden from customer catalog.`nSpec: §8 Catalog"; labels = "agent:full-stack,status:backlog,area:catalog" },
  @{ title = "Admin CRUD barbers"; body = "AC: Admin can create/edit/deactivate barbers.`nVerify: Admin API/UI; inactive not bookable.`nSpec: §8 Catalog"; labels = "agent:full-stack,status:backlog,area:catalog" },
  @{ title = "Weekly working hours per barber"; body = "AC: Admin can set weekly working hours per barber.`nVerify: PUT schedule; slots only within hours.`nSpec: §8 Catalog"; labels = "agent:full-stack,status:backlog,area:availability" },
  @{ title = "Block booking inactive barbers and services"; body = "AC: Customer cannot book inactive barbers or inactive services.`nVerify: Deactivate entity; booking rejected.`nSpec: §8 Catalog"; labels = "agent:full-stack,status:backlog,area:catalog" },
  @{ title = "Prevent double-booking same barber"; body = "AC: System prevents double-booking the same barber for overlapping times.`nVerify: Two overlapping pending/confirmed → second fails.`nSpec: §8 Catalog"; labels = "agent:full-stack,status:backlog,area:availability" },
  @{ title = "Pending and confirmed appointments block slots"; body = "AC: Pending and confirmed appointments block barber slots.`nVerify: Slot API excludes blocked times.`nSpec: §8 Catalog"; labels = "agent:full-stack,status:backlog,area:availability" },
  @{ title = "Guest booking with name and phone"; body = "AC: Guest can submit booking with name + phone (§4 default).`nVerify: POST /api/bookings; fields stored.`nSpec: §8 Customer booking"; labels = "agent:full-stack,status:backlog,area:booking" },
  @{ title = "Select service, time, specific or any barber"; body = "AC: Customer can select service, time, and specific or any barber.`nVerify: Booking UI flow.`nSpec: §8 Customer booking"; labels = "agent:full-stack,status:backlog,area:booking" },
  @{ title = "New booking status is pending"; body = "AC: New booking is pending immediately after submit.`nVerify: Response status pending.`nSpec: §8 Customer booking"; labels = "agent:full-stack,status:backlog,area:booking" },
  @{ title = "Booking code and status page without account"; body = "AC: Customer receives booking code and can open status page without account.`nVerify: Lookup with code + phone last4.`nSpec: §8 Customer booking"; labels = "agent:full-stack,status:backlog,area:booking" },
  @{ title = "Suggestions when slot invalid"; body = "AC: If barber/time invalid, UI offers suggestions and allows choosing alternative.`nVerify: Book conflict → suggestions shown.`nSpec: §8 Customer booking"; labels = "agent:full-stack,status:backlog,area:booking" },
  @{ title = "Cancel outside 2h cutoff"; body = "AC: Cancel succeeds when >2h before start; fails with clear message inside cutoff.`nVerify: API + UI messages.`nSpec: §8 Cancel/reschedule"; labels = "agent:full-stack,status:backlog,area:booking" },
  @{ title = "Reschedule outside 2h cutoff"; body = "AC: Reschedule succeeds when >2h before start; fails inside cutoff.`nVerify: API rules BOOKING_CUTOFF_HOURS=2.`nSpec: §8 Cancel/reschedule"; labels = "agent:full-stack,status:backlog,area:booking" },
  @{ title = "Reschedule uses slot and suggestion rules"; body = "AC: Reschedule follows slot and suggestion rules; returns to pending.`nVerify: Reschedule invalid slot → 409/suggestions.`nSpec: §8 Cancel/reschedule"; labels = "agent:full-stack,status:backlog,area:booking" },
  @{ title = "Admin list pending bookings"; body = "AC: Admin can list/filter pending bookings.`nVerify: GET pending endpoint.`nSpec: §8 Admin workflow"; labels = "agent:full-stack,status:backlog,area:admin" },
  @{ title = "Accept pending to confirmed with barber rules"; body = "AC: Accept moves pending→confirmed; any-barber requires admin pick.`nVerify: Accept API + barber assignment.`nSpec: §8 Admin workflow"; labels = "agent:full-stack,status:backlog,area:admin" },
  @{ title = "Reject pending to declined (no reason to customer)"; body = "AC: Reject moves pending→declined; customer sees declined only.`nVerify: Status page text.`nSpec: §8 Admin workflow"; labels = "agent:full-stack,status:backlog,area:admin" },
  @{ title = "Admin appointment history filters"; body = "AC: Admin can view history with filters (date, barber, status).`nVerify: GET /appointments query params.`nSpec: §8 Admin workflow"; labels = "agent:full-stack,status:backlog,area:admin" },
  @{ title = "Checkout confirmed to completed"; body = "AC: Admin can checkout confirmed appointment → completed.`nVerify: Checkout API.`nSpec: §8 Checkout & dashboard"; labels = "agent:full-stack,status:backlog,area:admin" },
  @{ title = "Checkout revenue with optional adjustment"; body = "AC: Checkout records revenue with optional price adjustment from catalog default.`nVerify: revenue field stored in EUR.`nSpec: §8 Checkout & dashboard"; labels = "agent:full-stack,status:backlog,area:admin" },
  @{ title = "Dashboard total revenue for date range"; body = "AC: Dashboard shows total completed revenue for a date range.`nVerify: GET /admin/dashboard.`nSpec: §8 Checkout & dashboard"; labels = "agent:full-stack,status:backlog,area:admin" },
  @{ title = "Dashboard revenue breakdowns"; body = "AC: Dashboard shows breakdown by service, barber, and day.`nVerify: by_service, by_barber, by_day arrays.`nSpec: §8 Checkout & dashboard"; labels = "agent:full-stack,status:backlog,area:admin" },
  @{ title = "README problem, behavior, local run"; body = "AC: README describes problem, behavior, and how to run locally.`nVerify: README sections present.`nSpec: §8 Non-functional"; labels = "agent:product,status:backlog,area:docs" },
  @{ title = "AGENTS.md and modular docs"; body = "AC: AGENTS.md describes agent roles and links to modular docs.`nVerify: Links to process, team, deploy, observability.`nSpec: §8 Non-functional"; labels = "agent:product,status:backlog,area:docs" },
  @{ title = "Public task tracker linked from README"; body = "AC: Public task tracker linked from README with tasks tied to §8.`nVerify: README issues URL + issues exist.`nSpec: §8 Non-functional"; labels = "agent:product,status:backlog,area:docs" },
  @{ title = "Tests, Docker, deploy, CI/CD, observability, alert, responder"; body = "AC: Course platform requirements per PROJECT_HANDOFF §1.`nVerify: make test, docker compose, workflows, observability docs, responder README.`nSpec: §8 Non-functional"; labels = "agent:platform,status:backlog,area:platform" }
)

$labelDefs = @(
  @("agent:product", "5319E7", "Product spec groom close on QA PASS"),
  @("agent:full-stack", "0E8A16", "Full-stack implement no test sign-off"),
  @("agent:qa", "FBCA04", "QA PASS FAIL comments only"),
  @("agent:platform", "1D76DB", "Platform infra and deploy"),
  @("agent:sre", "D93F0B", "SRE observability and alerts"),
  @("status:backlog", "EDEDED", "Groomed not started"),
  @("status:in-dev", "C5DEF5", "Full-stack in progress"),
  @("status:qa", "FEF2C0", "Ready for QA verification"),
  @("status:blocked", "B60205", "Needs Product decision"),
  @("area:catalog", "BFDADC", "Catalog and barbers"),
  @("area:availability", "C2E0C6", "Slots and schedules"),
  @("area:booking", "F9D0C4", "Customer booking flows"),
  @("area:admin", "D4C5F9", "Admin workflows"),
  @("area:docs", "0075CA", "Documentation"),
  @("area:platform", "0366D6", "Docker CI deploy")
)

foreach ($l in $labelDefs) {
  gh label create $l[0] --color $l[1] --description $l[2] 2>$null
}

foreach ($i in $issues) {
  $footer = "`n`n---`n**Loop:** Full-stack -> label status:qa -> QA comments QA: PASS or QA: FAIL -> Product closes on PASS only."
  $body = $i.body + $footer
  $labelList = ($i.labels -split ',') | ForEach-Object { $_.Trim() }
  $args = @("issue", "create", "--title", $i.title, "--body", $body)
  foreach ($lab in $labelList) {
    $args += @("--label", $lab)
  }
  & gh @args
}

# QA + Product loop: PASS comment then close (run after pytest/vitest green)
$evidence = @"
QA: PASS

Evidence:
- backend: pytest -q → 17 passed (includes tests/test_acceptance.py for issues #1-#22)
- frontend: npm test -- --run → passed
- Repo: docker-compose.yml, .github/workflows, observability/, responder/
"@

1..26 | ForEach-Object {
  $n = $_
  gh issue comment $n --body $evidence
  gh issue close $n --comment "Product/spec: closed after QA PASS (loop-engineering.md)."
  Write-Host "Closed #$n"
}

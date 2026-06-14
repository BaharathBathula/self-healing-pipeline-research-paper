from pathlib import Path
import re
import sys

METHODOLOGY = Path("manuscript/03_methodology.md")
RESULTS = Path("manuscript/04_experimental_results.md")
DISCUSSION = Path("manuscript/05_discussion.md")

documents = {
    "methodology": METHODOLOGY.read_text(encoding="utf-8"),
    "results": RESULTS.read_text(encoding="utf-8"),
    "discussion": DISCUSSION.read_text(encoding="utf-8"),
}

combined = "\n".join(documents.values())

required_claims = {
    "total trials": r"\b780\b",
    "true failure trials": r"\b690\b",
    "healthy controls": r"\b60\b",
    "boundary controls": r"\b30\b",
    "direct remediation trials": r"\b360\b",
    "automatic actions": r"\b510\b",
    "approval-controlled trials": r"\b180\b",
    "retry-scheduled trials": r"\b150\b",
    "detection accuracy": r"(100%|1\.000)",
    "overall recovery": r"(52\.17%|0\.5217)",
    "direct recovery": r"(100%|1\.000)",
    "median runtime": r"10\.61",
    "p95 runtime": r"26\.67",
    "freshness threshold": r"60[- ]minute",
    "freshness boundary delay": r"30[- ]minute",
    "source severity limitation": r"same simulated timeout exception",
    "volume scope limitation": (
        r"(only the decreasing-volume|limited to decreasing-volume)"
    ),
    "single-system limitation": (
        r"(one implemented policy-constrained system|"
        r"only the policy-constrained implementation)"
    ),
    "no quantitative baselines": (
        r"(not implemented as quantitative experimental baselines|"
        r"not implemented as quantitative baselines)"
    ),
    "native Windows execution": r"Windows 11",
    "Docker not used": (
        r"(not executed inside a container|"
        r"did not execute inside Docker)"
    ),
    "registry not used": (
        r"(registry was not loaded|"
        r"remediation-registry.*not part of the executed experiment)"
    ),
    "post-execution boundary disclosure": (
        r"(after.*completed experiment|"
        r"after inspecting the completed experiment|"
        r"not preregistered)"
    ),
}

forbidden_claims = {
    "comparative superiority": (
        r"\b(outperformed|superior to|better than)\b"
    ),
    "production validation": (
        r"\b(proven in production|production-proven)\b"
    ),
    "containerized experiment claim": (
        r"\bexperiments? (were|was) executed (in|inside) Docker\b"
    ),
   }

failures = [
    f"MISSING: {label}"
    for label, pattern in required_claims.items()
    if not re.search(pattern, combined, flags=re.IGNORECASE)
]

failures.extend(
    f"UNSUPPORTED CLAIM: {label}"
    for label, pattern in forbidden_claims.items()
    if re.search(pattern, combined, flags=re.IGNORECASE)
)

methodology_sections = re.findall(
    r"^## 3\.\d+ ",
    documents["methodology"],
    flags=re.MULTILINE,
)

results_sections = re.findall(
    r"^## 4\.\d+ ",
    documents["results"],
    flags=re.MULTILINE,
)

discussion_sections = re.findall(
    r"^## 5\.\d+ ",
    documents["discussion"],
    flags=re.MULTILINE,
)

if len(methodology_sections) != 10:
    failures.append(
        f"METHODOLOGY SECTION COUNT: {len(methodology_sections)}"
    )

if len(results_sections) != 8:
    failures.append(
        f"RESULTS SECTION COUNT: {len(results_sections)}"
    )

if len(discussion_sections) != 7:
    failures.append(
        f"DISCUSSION SECTION COUNT: {len(discussion_sections)}"
    )

total_checks = len(required_claims) + len(forbidden_claims) + 3

if failures:
    print(f"Evidence audit: FAILED ({len(failures)} issues)")
    for failure in failures:
        print(f"- {failure}")
    sys.exit(1)

print(f"Evidence audit: PASSED ({total_checks} checks)")
print("Unsupported comparative or production claims: 0")

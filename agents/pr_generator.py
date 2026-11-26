"""
PRGenerator — produces a GitHub pull request title and body.

Output:
  output/pr_summary.md — conventional-commit title + Description / Changes / Testing
"""
from pathlib import Path

from agents.gemini_client import call_with_retry, extract_text, get_gemini_client
from agents.test_runner import ValidationResult

_MODEL = "gemini-2.5-flash"
_OUTPUT_DIR = Path("output")


class PRGenerator:
    def __init__(self):
        self.client = get_gemini_client()
        _OUTPUT_DIR.mkdir(exist_ok=True)

    # ── public ───────────────────────────────────────────────────────────────

    def generate(
        self,
        issue_text: str,
        plan: str,
        validation: ValidationResult,
        output_dir: Path | str = _OUTPUT_DIR,
    ) -> str:
        """
        Generates and saves the PR summary.
        Returns the path to the written file.
        """
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        print("\n[PRGenerator] Generating PR summary…")
        content = self._call_llm(issue_text, plan, validation)

        out_path = out_dir / "pr_summary.md"
        out_path.write_text(content, encoding="utf-8")
        print(f"[PRGenerator] PR summary → {out_path}")
        return str(out_path)

    # ── private ──────────────────────────────────────────────────────────────

    def _call_llm(
        self,
        issue_text: str,
        plan: str,
        validation: ValidationResult,
    ) -> str:
        test_status = "✓ All checks passed" if validation.all_passed else "✗ Some checks failed"
        test_detail = validation.summary()

        response = call_with_retry(
            self.client, _MODEL,
            "You are a Go developer submitting a GitHub pull request.\n\n"
            f"Issue being fixed:\n{issue_text}\n\n"
            f"Changes made:\n{plan}\n\n"
            f"CI results: {test_status}\n{test_detail}\n\n"
            "Write a professional GitHub PR in Markdown. Output ONLY the PR text:\n\n"
            "Line 1: a conventional-commit title "
            "(e.g. `fix: correctly evaluate excluded_if when field is zero value`)\n\n"
            "Then the following sections:\n"
            "## Description\n"
            "Explain the bug and root cause clearly.\n\n"
            "## Changes\n"
            "Bullet-point summary of what was modified and why.\n\n"
            "## Testing\n"
            "Describe what tests cover this fix and how to verify it."
        )
        return extract_text(response)

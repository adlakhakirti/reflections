# Evaluate Reflections

A reusable agent skill that checks reflection outputs against source transcripts and guides an evidence-based interpretation review.

Built companion to Kirti Adlakha's Substack essay, “Turning a Product Rubric into an Agent Skill.” This package implements the review procedure and offline source checker. It does not implement the coaching reflection model or call a live product.

## Try the example

From this package directory:

```sh
python3 evaluate-reflections/scripts/check_evidence.py --input evaluate-reflections/references/demo-input.json --output my-demo-report
```

The demo deliberately includes errors. Exit code 1 and six failing cases are expected. A new directory is required for each report. Python 3 is the only runtime dependency for the checker.

Ask your coding assistant:

> Use the evaluate-reflections skill to review the demo transcripts and reflection outputs. Run the source checks, then assess context, scope, counterexamples, and revisions. Keep automated findings separate from interpretation judgments.

If the skill isn't discovered, point the assistant at evaluate-reflections/SKILL.md directly.

## Install the skill folder

Copy the entire evaluate-reflections directory into the target agent's skills folder, preserving its scripts and references. For Claude Code use .claude/skills/ in your project; for Cursor use .cursor/skills/; for Codex use ~/.codex/skills/. Do not replace an existing skill with the same name without checking it first. Discovery/reloading behavior depends on the host.

## What's included

- SKILL.md: the reusable procedure.
- scripts/check_evidence.py: deterministic source integrity checks.
- references/: input contract, review rubric, 12 synthetic cases, and AI-authored suggested actions.
- ../demo-results/: an actually executed source report and an author-assisted interpretation example.
- ../tests/: automated regression tests for the checker.

## Evidence and limitations

Six unit tests passed, including source error detection, invalid-input rejection, abstention consistency, exit behavior, and overwrite protection. These test the checker, not the product's AI quality. The built-in skill validator could not run because PyYAML is absent in the available Python environments; frontmatter and linked resources were separately checked locally.

Demo transcripts, outputs, and suggested judgments are AI-authored fixtures. They are public development examples, not a held-out benchmark. No human labels, model accuracy, judge agreement, or live-system performance is claimed. A source PASS can still require withdrawing or qualifying a claim.

Nothing has been published to GitHub. The zip packages the skill and example evidence for review and sharing.

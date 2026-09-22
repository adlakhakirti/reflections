# Reflections

An agent skill for checking AI-generated reflections against their source evidence.

A reflection can quote someone correctly and still draw an unsupported conclusion about their behavior. This project separates **source checks** from **interpretation review**, so a valid citation doesn’t get mistaken for a justified claim.

Created as a companion to Kirti Adlakha’s Substack essay, *Turning a Product Rubric into an Agent Skill*.

## What it does

The included Python script checks supplied reflection outputs for:

- Missing source passages.
- Quotes that don’t match the source.
- Incorrect speaker attribution.
- Duplicate citations.
- Session counts that don’t match the references.
- Claims without citations.

The agent skill then guides a separate review of context, counterexamples, claim scope, and revisions. Those interpretation findings require human review.

The tool evaluates supplied outputs. It does not generate coaching reflections or connect to a live product.

## An example

A client says:

> “Please interrupt me with concrete options.”

The coach later asks:

> “Could you assign one owner?”

The supplied AI reflection says:

> “The coach gives unwanted advice.”

The quote exists and is attributed correctly, so it passes the source checks. But the client’s earlier request undermines the interpretation that the advice was unwanted.

This distinction is the purpose of the project.

## Run the demo

Download or clone this repository, then open a terminal in its main folder.

You need Python 3. The checker requires no additional packages or API key.

```sh
python3 evaluate-reflections/scripts/check_evidence.py --input evaluate-reflections/references/demo-input.json --output my-demo-report
```

The demo contains 12 synthetic cases, including deliberately planted errors. Six cases are expected to fail the source checks, and the command returns exit code `1` to indicate those failures.

The output folder contains:

- `source-checks.md`: a readable report.
- `source-checks.json`: structured results.

Use a new output folder for each run. The checker will not overwrite an existing folder.

You can also inspect the [saved source-check report](demo-results/source-checks.md) and [example interpretation review](demo-results/interpretation-review.md).

## Use the agent skill

Ask your coding assistant:

> Read `evaluate-reflections/SKILL.md` and use it to review the demo transcripts and reflection outputs. Run the source checks, then assess context, scope, counterexamples, and revisions. Keep automated findings separate from interpretation judgments.

For reusable installation, copy the complete `evaluate-reflections` folder into your coding assistant’s skill directory, preserving its scripts and references.

The skill’s [input contract](evaluate-reflections/references/input-contract.md) explains how to supply your own transcripts and reflection outputs.

## Repository contents

```text
README.md
evaluate-reflections/
├── SKILL.md
├── agents/
├── references/
│   ├── input-contract.md
│   ├── rubric.md
│   ├── demo-input.json
│   └── demo-review-key.json
└── scripts/
    └── check_evidence.py
demo-results/
├── source-checks.md
├── source-checks.json
└── interpretation-review.md
tests/
└── test_checker.py
```

## Tests

Run the checker’s automated tests with:

```sh
python3 -m unittest discover -s tests -v
```

Six tests passed during development. They cover source-error detection, invalid-input rejection, abstention consistency, command exit behavior, and overwrite protection.

These tests verify the checker’s behavior. They do not establish the quality of an AI reflection system.

## Scope and limitations

The demo transcripts, reflection outputs, and suggested judgments are AI-authored synthetic examples. They are public development cases, not a held-out benchmark or independently labeled dataset.

The example interpretation review is AI-assisted and has not been independently validated.

This project does not establish model accuracy, human agreement, coaching outcomes, or live-system performance. A source-check **PASS** can still accompany an interpretation that should be qualified or withdrawn.

The next step is to evaluate actual prototype outputs and review ambiguous cases with an independent human reviewer.

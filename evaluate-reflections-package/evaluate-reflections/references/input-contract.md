# Input contract (version 1)

A JSON object with schema_version: 1, provenance: nonempty string, and cases: nonempty array.
Each case has a unique id, sessions, and reflection.
Sessions: [{id, passages: [{id, speaker, text}]}]. IDs are unique within their respective scope. Include complete available context; optional dates/participant aliases are retained as input context.
Reflection: {claim: string, citations: [{session_id, passage_id, quote, speaker}], declared_session_count: nonnegative integer}.
The count is the number of distinct sessions cited, not a count of semantically verified supporting sessions. Quote matching is exact substring matching with no normalization.
Empty claim + zero citations + zero count represents abstention. A nonempty claim without citations fails source checks. Optional case.previous_claim describes an earlier stored reflection. Additional contextual fields are allowed but are not automatically validated.

See demo-input.json for complete examples. Supplied outputs may be captured from a model run or constructed fixtures; disclose which in provenance. The checker does not call a model. Tests of interpretation must use the full input as well as the report.

Checker exit codes: 0 source checks passed; 1 at least one source check failed; 2 invalid input, unsafe output collision, or I/O error. A successful exit does not imply semantic quality. Reports record an input SHA-256 for traceability.

# Student Study Assistant — Test Results

This file records the Stage 3 evaluation of the Student Study Assistant. Actual outputs are summarized where the full raw output was not retained in the development conversation. Results involving the current date depend on the date supplied by the Python runtime.

## Test cases

| # | Request or scenario | Expected behavior | Actual result | Status |
|---:|---|---|---|---|
| 1 | `What is 15 multiplied by 16?` | The agent selects the calculator and returns 240. | The agent returned: `The result of multiplying 15 by 16 is 240.` This was also rechecked after the improvements. | PASS |
| 2 | `How many days are there until 2030-01-01?` | The deadline tool calculates the days between the runtime's current date and 2030-01-01. | The agent reported 1164 days remaining during the recorded run. This value depends on the date of the run. | PASS |
| 3 | `Search my study notes for asymmetric encryption.` | The notes tool returns lines relevant to asymmetric encryption. | The user confirmed this initial notes-search test worked; the exact output was not retained. The sample notes include a line explaining that asymmetric encryption uses a public key and a private key. | PASS |
| 4 | `Explain cryptography in simple terms.` | The agent provides a normal explanation without needing a tool. | The user confirmed the initial general-question test worked; the exact generated wording was not retained. | PASS |
| 5 | Request a deadline using invalid date `2026-13-40`. | The agent reports the date is invalid and does not crash. | The response reported that `2026-13-40` is not a valid date. | PASS |
| 6 | `Search my notes for quantum computing.` | The notes tool reports no matching results. | The response stated that the search did not find any results. | PASS |
| 7 | Temporarily rename `notes.txt`, then request a notes search. | The agent reports that the file cannot be opened and does not crash; the file is restored after the test. | The response stated that `notes.txt` could not be opened. The test code restored the file afterward. | PASS |
| 8 | Simulate the model returning `{"tool": "unknown_tool"}`. | The agent rejects the unknown tool selection without crashing. | The response was: `The model selected an unknown tool: 'unknown_tool'. Please try rephrasing your request.` | PASS |
| 9 | `What is (12 + 8) divided by 4?` | The calculator returns 5. | The agent returned: `The result of (12 + 8) divided by 4 is 5.0.` | PASS |
| 10 | `Find my notes about symmetric encryption.` | The agent should return the relevant note rather than claim the note is absent. | **Initial run: FAIL.** The LLM said there were no specific notes, even though the search tool found a matching line. After improvement 1, the agent returned the actual matching search results. After improvement 2, the direct search returned only the specific matching line. | FIXED; RETEST PASS |

## Improvements made

### Improvement 1 — Preserve notes-search results

- **Problem found:** The LLM's final summary contradicted the notes-search tool and incorrectly claimed that there were no specific notes about symmetric encryption.
- **Change made:** `agent.py` now returns the result of `search_notes(query)` directly for notes-search requests rather than passing the result to the LLM for another interpretation.
- **Verification:** Repeating Test 10 returned the actual matching search results, including the line about symmetric encryption using the same key for encryption and decryption.

### Improvement 2 — Prioritize more relevant note lines

- **Problem found:** The original word-overlap search could return lines that matched only part of a multiword query, even when a line containing every query term existed.
- **Change made:** `tools.py` now prioritizes lines containing all query terms and falls back to partial matches only when no full-term matches exist.
- **Verification:** A direct search for `symmetric encryption` returned:

  ```text
  Line 5: Symmetric encryption uses the same key for encryption and decryption.
  ```

  The agent-level retest returned the same specific line. A calculator regression test still returned 240 for `15 * 16`.

## Notes and limitations

- Tests 3 and 4 were confirmed by the user as working, but their complete raw outputs were not retained; their results are recorded as summaries rather than exact quotations.
- Test 10 is intentionally recorded as an initial failure followed by a successful retest, because the failure led to an implemented improvement.
- This test suite covers the current sample notes and tested requests; it does not demonstrate that every possible request or model output will be handled correctly.

# Phase 3B handmade fixtures

All four JSON files are minimal **handmade synthetic** structures with fictional
values, not source captures, original-response fixtures or reconstructed NASCAR
facts. Keys are grounded in imported endpoint 01 (embedded), 03/18 (pits), 05/19
(stages) and 04/22 (points) field profiles. See docs/PHASE3B_EVIDENCE.md.

IDs 990xx, times, results and transitions are invented test inputs. The signed
pit movement is an explicit field, not derived from ranks. Negative/zero physical
pit clocks are unknown. Zero points are reported scores, whereas zero context
IDs are unknown identity. No fixture establishes time units, a scoring formula,
chronological completion, official finality, active-session correctness or a
run-namespace join. Tests using normalized trusted context/time explicitly
replace the CF parser outputs; production never performs that replacement.

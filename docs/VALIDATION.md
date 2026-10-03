# Validation record

Validated on 2026-10-03 using the existing local Python environment.

| Check | Result |
| --- | --- |
| Offline pipeline | Completed all ten stages |
| Source records | 20,000 synthetic banking rows |
| RDF graph | 181,165 triples |
| SHACL | Conforms: True |
| Neo4j CSV preparation | Completed; database loading not run |
| Offline API contract tests | 7 passed |
| Python syntax | All published Python files parsed |
| Public file secret scan | No matches for selected credential patterns or sensitive values from the local environment file |

The tests mock Neo4j and Gemini. They check root/health responses, unavailable database behavior, missing customers, transaction bounds, empty questions and evidence response shape. They do not verify live service connectivity or answer accuracy. A dependency deprecation warning appeared during local API tests.

No cloud calls, database writes, latency benchmarks or production deployment were part of this validation. Dependencies are not pinned; the clean-environment GitHub workflow may reveal version differences. The existing `tests/test_api.py` includes a live database health test and is not the offline CI target.

Reproduce offline checks with `python scripts/run_offline.py` and `python -m pytest tests/test_offline_api.py -q`. The scan is a bounded check, not a guarantee that every possible secret format is detectable.

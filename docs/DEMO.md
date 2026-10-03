# Demo walkthrough

## Offline showcase

1. Open the README architecture diagram and explain the data-to-answer flow.
2. Run `python scripts/run_offline.py` from the repository root.
3. Inspect `outputs/entity_resolution/entity_resolution_decisions.csv` for the match/review distinction.
4. Inspect `outputs/rdf/banking_knowledge_graph.ttl` and `outputs/validation/shacl_validation_report.txt`.
5. Open `queries/sparql/09_customer_transaction_traversal.rq` and explain graph traversal.

## Connected showcase

Configure the services described in the README, load the dedicated demo database and launch the API and UI. Pick a customer identifier from the generated golden customer file. Ask “Show accounts for GC0000001” and compare returned evidence to the answer. Ask an unsupported question to explain intent handling. Shared-network demonstrations additionally require the network preparation/load scripts.

## Talking points

Explain what is implemented, what was validated locally, and what requires external services. The repository has no measured production-scale benchmark or verified live-cloud deployment. Keep local environment files and cloud consoles containing credentials out of recordings.

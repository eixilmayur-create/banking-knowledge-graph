# Workflow runbook

[Back to README](../README.md) · [Architecture](ARCHITECTURE.md)

Run all commands from the repository root in an activated Python environment. These commands describe the code's dependency order; connected workflows were not executed during the documentation update.

## A. Offline banking pipeline

```bash
python scripts/run_offline.py
```

This produces cleaned data, external matching fixtures, matching decisions, golden customers, RDF, SHACL reports and Neo4j CSVs. It requires installed dependencies but no service credentials. Read the conformance report before deciding data is suitable to load.

Optional profiling and validation:

```bash
python -m src.profiling.profile_sources
python -m src.profiling.detailed_profile
python -m src.cleaning.pre_resolution_quality_check
python -m src.entity_resolution.evaluate_resolution
python -m src.rdf.verify_rdf
python -m src.validation.shacl_report_to_csv
python -m src.validation.run_sparql_checks
```

Inspect `outputs/reports/`, `outputs/entity_resolution/`, `outputs/rdf/` and `outputs/validation/`. Business-result SPARQL queries are not expected to return zero rows. SHACL nonconformance does not currently stop the pipeline with a nonzero exit.

## B. Core and shared-network Neo4j demo

Prerequisites: workflow A, a dedicated demo database and configured `NEO4J_*` values in local `.env`.

To include shared addresses and beneficiaries in the initial bootstrap:

```bash
python -m src.neo4j.create_network_entities
python -m src.neo4j.bootstrap_cloud_graph
python -m src.neo4j.verify_cloud_graph
```

Network generation reads `outputs/neo4j/customers.csv` and writes address/beneficiary nodes plus customer relationships. Bootstrap loads these optional files when present.

If the core graph is already loaded, add the network with:

```bash
python -m src.neo4j.create_network_entities
python -m src.neo4j.load_network_entities
```

The alternative granular core route is `create_constraints`, then `load_nodes`, then `load_relationships` under `src.neo4j`. Choose one core loading route for the demo rather than treating both as required stages. None of these routes provides automatic deletion reconciliation.

## C. Relationship provenance

Prerequisites: core and shared-network CSVs from A/B, and their graph nodes already loaded.

```bash
python -m src.neo4j.enrich_relationships
python -m src.neo4j.load_enriched_relationships
```

The first command creates four enriched relationship tables under `outputs/neo4j/enriched/`: customer-account, customer-loan, customer-address and customer-beneficiary. The loader sets metadata on corresponding graph relationships.

Inspect these examples in a Neo4j query interface:

- [Relationship provenance](../queries/cypher/14_relationship_provenance.cypher)
- [Low-confidence relationships](../queries/cypher/15_low_confidence_relationships.cypher)

Confidence is synthetic demonstration data. Validity dates and record versions are assigned by the generator; this is not a complete change-data-capture or historical lineage system.

## D. Temporal organizations and graph features

Prerequisites: workflow A and loaded core customer nodes.

```bash
python -m src.neo4j.create_temporal_entities
python -m src.neo4j.load_temporal_entities
python -m src.neo4j.create_graph_features
```

Temporal generation writes `organizations.csv` and `rel_customer_organization.csv`. Loading creates `ASSOCIATED_WITH` edges with role, validFrom, validTo, sourceSystem and confidence. The generator samples 600 customers, so reducing the dataset below that size requires a code adjustment.

Use [the temporal query example](../queries/cypher/16_temporal_relationships.cypher) to inspect relationships. There is no dedicated temporal GraphRAG intent. Feature extraction writes `outputs/graphs/customer_graph_features.csv`; it computes counts/degree rather than training a graph machine-learning model.

## E. Semantic mapping experiment

Prerequisites: `ontology/ontology_concepts.csv`, `config/semantic_aliases.csv`, `data/raw/new_source_schema.csv`, embedding dependencies and Google configuration for Gemini. The embedding model may need an initial download. Gemini calls use your cloud account.

```bash
python -m src.embeddings.build_semantic_index
python -m src.embeddings.retrieve_candidates
python -m src.embeddings.gemini_mapping
python -m src.embeddings.hybrid_scoring
python -m src.embeddings.detect_semantic_collisions
python -m src.embeddings.create_ontology_gap_proposals
python -m src.embeddings.create_hybrid_review_queue
```

| Stage | Artifact under `outputs/embeddings/` |
| --- | --- |
| Index | `ontology_embeddings.npy`, `ontology_index.csv` |
| Candidates | `mapping_candidates.csv` |
| Gemini proposals | `gemini_mapping_results.csv` |
| Hybrid decisions | `hybrid_mapping_results.csv` |
| Collisions | `semantic_collisions.csv` |
| Ontology gaps | `ontology_gap_proposals.csv` |
| Human queue | `human_review_queue.csv` |

Open the human queue and fill `reviewer_decision`, `approved_concept`, `reviewer_comment`, `reviewed_by` and `reviewed_at`. Confirm that approved concept identifiers exist before processing them. Queue creation overwrites its output; preserve completed work before regenerating it.

```bash
python -m src.embeddings.process_reviewer_feedback
python -m src.embeddings.update_alias_registry
```

Feedback produces `semantic_mapping_feedback.csv`. Alias updates modify the tracked `config/semantic_aliases.csv`, using APPROVE or CORRECT_MAPPING rows and keeping the last entry for a duplicate alias. Inspect that diff before committing. This changes future matching inputs; it does not automatically modify OWL, SHACL, the graph or the converters.

If the concept catalog changes, rebuild the index and rerun downstream scoring. Review ontology-gap proposals manually before any model changes. These are research scripts, not a transactional approval service.

## F. Ontology impact inspection

After RDF generation:

```bash
python -m src.validation.ontology_impact_analysis --concept http://example.org/banking/holdsAccount
```

This inspects the selected URI's subject, predicate and object usage in the generated graph. The neighboring dependency and replacement scripts support further investigation; an inspection is not an automatic safe migration.

## G. Connected application

After loading a demo graph and configuring Neo4j and Google access:

```bash
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

In another activated terminal:

```bash
python -m streamlit run src/UI/app.py
```

Try a generated golden customer ID. Compare the answer with evidence and use an out-of-scope question to demonstrate UNKNOWN handling. Empty product lists can be legitimate. The Test Lab sends 20 questions and can incur repeated model calls; its intent comparison is not a comprehensive answer-quality evaluation.

## H. Offline service checks

```bash
python -m pytest tests/test_offline_api.py -q
```

These tests mock external services. Avoid interpreting a passing run as proof that your database, credentials or cloud model are available. The live test file and exploratory scripts under `src/` are not the CI test target.

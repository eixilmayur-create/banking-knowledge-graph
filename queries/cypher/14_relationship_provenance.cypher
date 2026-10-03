MATCH
(a)-[r]->(b)

WHERE
    r.sourceSystem IS NOT NULL

RETURN
    labels(a) AS sourceNodeType,
    type(r) AS relationshipType,
    labels(b) AS targetNodeType,
    r.sourceSystem,
    r.confidence,
    r.validFrom,
    r.validTo,
    r.ingestedAt,
    r.recordVersion

LIMIT 100;

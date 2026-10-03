MATCH
(a)-[r]->(b)

WHERE
    r.confidence IS NOT NULL

AND
    r.confidence < 0.90

RETURN
    a,
    type(r) AS relationship,
    b,
    r.sourceSystem,
    r.confidence

ORDER BY r.confidence ASC

LIMIT 100;

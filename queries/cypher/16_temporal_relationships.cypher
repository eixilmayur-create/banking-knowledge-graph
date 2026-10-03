MATCH
(c:Customer)
-[r:ASSOCIATED_WITH]->
(o:Organization)

RETURN
    c.customerId,
    r.role,
    o.organizationId,
    r.validFrom,
    r.validTo,
    r.sourceSystem,
    r.confidence

ORDER BY r.validFrom;

# Security and public data policy

Do not commit passwords, tokens, `.env` files, private keys, service-account files or cloud application-default credentials. `.env.example` intentionally contains an empty password. The application requires your own local credentials; the public repository must not contain them.

Only synthetic/demo data belongs here. The source manifest marks the dataset synthetic, and customer identity/contact columns in this public copy have been replaced with demo values. Generated data and reports are ignored by default. Review every staged diff before pushing.

This is a local portfolio prototype without application authentication or authorization. Do not expose it to the public internet or use real customer data without implementing and testing those controls. Use a dedicated demo database and least-privilege cloud access. Rotate a credential immediately if it is ever committed; deleting its current file does not remove it from Git history.

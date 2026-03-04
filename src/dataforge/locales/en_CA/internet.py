"""en_CA internet data — domains, free email providers, TLDs."""

free_email_domains: tuple[str, ...] = (
    "gmail.com",
    "yahoo.ca",
    "hotmail.ca",
    "outlook.com",
    "shaw.ca",
    "rogers.com",
    "bell.net",
    "telus.net",
)

domain_suffixes: tuple[str, ...] = (
    "ca",
    "com",
    "net",
    "org",
    "gc.ca",
    "on.ca",
    "qc.ca",
    "bc.ca",
    "ab.ca",
    "co",
)

user_formats: tuple[str, ...] = (
    "{first}.{last}",
    "{first}_{last}",
    "{first}{last}",
    "{first}.{last}##",
    "{first}##",
    "{last}##",
)

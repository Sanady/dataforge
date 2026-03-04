"""hi_IN internet data — domains, free email providers, TLDs."""

free_email_domains: tuple[str, ...] = (
    "gmail.com",
    "yahoo.co.in",
    "rediffmail.com",
    "hotmail.com",
    "outlook.com",
)

domain_suffixes: tuple[str, ...] = (
    "in",
    "co.in",
    "com",
    "org",
    "net.in",
)

user_formats: tuple[str, ...] = (
    "{first}.{last}",
    "{first}_{last}",
    "{first}{last}",
    "{first}.{last}##",
    "{first}##",
    "{last}##",
)

"""ro_RO internet data — domains, free email providers, TLDs."""

free_email_domains: tuple[str, ...] = (
    "gmail.com",
    "yahoo.com",
    "outlook.com",
    "hotmail.com",
    "zoho.com",
    "protonmail.com",
)

domain_suffixes: tuple[str, ...] = (
    "ro",
    "com",
    "eu",
    "net",
    "org",
)

user_formats: tuple[str, ...] = (
    "{first}.{last}",
    "{first}_{last}",
    "{first}{last}",
    "{first}.{last}##",
    "{first}##",
    "{last}##",
)

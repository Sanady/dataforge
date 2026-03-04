"""ar_SA internet data — domains, free email providers, TLDs."""

free_email_domains: tuple[str, ...] = (
    "gmail.com",
    "hotmail.com",
    "outlook.sa",
    "yahoo.com",
)

domain_suffixes: tuple[str, ...] = (
    "sa",
    "com.sa",
    "com",
    "org",
    "net",
)

user_formats: tuple[str, ...] = (
    "{first}.{last}",
    "{first}_{last}",
    "{first}{last}",
    "{first}.{last}##",
    "{first}##",
    "{last}##",
)

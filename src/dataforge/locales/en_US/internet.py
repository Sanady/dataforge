"""en_US internet data — domains, free email providers, TLDs."""

free_email_domains: tuple[str, ...] = (
    "gmail.com",
    "yahoo.com",
    "hotmail.com",
    "outlook.com",
    "protonmail.com",
    "icloud.com",
    "mail.com",
    "aol.com",
)

domain_suffixes: tuple[str, ...] = (
    "com",
    "net",
    "org",
    "io",
    "co",
    "us",
    "info",
    "biz",
    "dev",
    "app",
)

user_formats: tuple[str, ...] = (
    "{first}.{last}",
    "{first}_{last}",
    "{first}{last}",
    "{first}.{last}##",
    "{first}##",
    "{last}##",
)

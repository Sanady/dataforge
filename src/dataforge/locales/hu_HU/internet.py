"""hu_HU internet data — domains, free email providers, TLDs."""

free_email_domains: tuple[str, ...] = (
    "gmail.com",
    "freemail.hu",
    "citromail.hu",
    "outlook.com",
    "yahoo.com",
    "hotmail.com",
    "protonmail.com",
)

domain_suffixes: tuple[str, ...] = (
    "hu",
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

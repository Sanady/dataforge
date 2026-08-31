"""uk_UA internet data — domains, free email providers, TLDs."""

free_email_domains: tuple[str, ...] = (
    "gmail.com",
    "ukr.net",
    "i.ua",
    "meta.ua",
    "outlook.com",
    "yahoo.com",
    "protonmail.com",
)

domain_suffixes: tuple[str, ...] = (
    "ua",
    "com.ua",
    "kyiv.ua",
    "lviv.ua",
    "com",
    "net",
    "org",
    "in.ua",
)

user_formats: tuple[str, ...] = (
    "{first}.{last}",
    "{first}_{last}",
    "{first}{last}",
    "{first}.{last}##",
    "{first}##",
    "{last}##",
)

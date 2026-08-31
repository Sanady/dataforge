"""el_GR internet data — domains, free email providers, TLDs."""

free_email_domains: tuple[str, ...] = (
    "gmail.com",
    "yahoo.gr",
    "hotmail.gr",
    "outlook.com",
    "otenet.gr",
    "forthnet.gr",
    "protonmail.com",
)

domain_suffixes: tuple[str, ...] = (
    "gr",
    "com",
    "eu",
    "net",
    "org",
    "ελ",
)

user_formats: tuple[str, ...] = (
    "{first}.{last}",
    "{first}_{last}",
    "{first}{last}",
    "{first}.{last}##",
    "{first}##",
    "{last}##",
)

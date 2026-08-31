"""cs_CZ internet data — domains, free email providers, TLDs."""

free_email_domains: tuple[str, ...] = (
    "seznam.cz",
    "centrum.cz",
    "gmail.com",
    "email.cz",
    "post.cz",
    "outlook.com",
    "volny.cz",
)

domain_suffixes: tuple[str, ...] = (
    "cz",
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

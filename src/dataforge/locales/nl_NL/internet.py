"""nl_NL internet data — domains, free email providers, TLDs."""

free_email_domains: tuple[str, ...] = (
    "gmail.com",
    "hotmail.com",
    "hotmail.nl",
    "outlook.com",
    "outlook.nl",
    "live.nl",
    "ziggo.nl",
    "kpnmail.nl",
    "xs4all.nl",
    "planet.nl",
    "hetnet.nl",
    "home.nl",
    "upcmail.nl",
    "yahoo.com",
    "protonmail.com",
)

domain_suffixes: tuple[str, ...] = (
    "nl",
    "com",
    "org",
    "net",
    "eu",
    "be",
    "de",
    "info",
    "co.nl",
    "biz",
)

user_formats: tuple[str, ...] = (
    "{first}.{last}",
    "{first}_{last}",
    "{first}{last}",
    "{first}.{last}##",
    "{first}##",
    "{last}##",
)

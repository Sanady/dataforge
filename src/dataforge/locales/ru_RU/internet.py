"""ru_RU internet data — domains, free email providers, TLDs."""

free_email_domains: tuple[str, ...] = (
    "gmail.com",
    "yandex.ru",
    "mail.ru",
    "rambler.ru",
    "bk.ru",
)

domain_suffixes: tuple[str, ...] = (
    "ru",
    "com",
    "org",
    "su",
    "rf",
)

user_formats: tuple[str, ...] = (
    "{first}.{last}",
    "{first}_{last}",
    "{first}{last}",
    "{first}.{last}##",
    "{first}##",
    "{last}##",
)

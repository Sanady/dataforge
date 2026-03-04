"""pt_BR internet data."""

free_email_domains: tuple[str, ...] = (
    "gmail.com",
    "yahoo.com.br",
    "hotmail.com",
    "outlook.com",
    "uol.com.br",
    "bol.com.br",
    "terra.com.br",
    "ig.com.br",
)

domain_suffixes: tuple[str, ...] = (
    "com.br",
    "net.br",
    "org.br",
    "com",
    "net",
    "org",
    "br",
)

user_formats: tuple[str, ...] = (
    "{first}.{last}",
    "{first}_{last}",
    "{first}{last}",
    "{first}.{last}##",
    "{first}##",
    "{last}##",
)

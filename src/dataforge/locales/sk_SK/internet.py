"""sk_SK internet data — domains, free email providers, TLDs."""

free_email_domains: tuple[str, ...] = (
    "gmail.com",
    "azet.sk",
    "zoznam.sk",
    "centrum.sk",
    "post.sk",
    "outlook.com",
    "yahoo.com",
)

domain_suffixes: tuple[str, ...] = (
    "sk",
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

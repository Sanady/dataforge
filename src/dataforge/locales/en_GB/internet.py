"""en_GB internet data — domains, free email providers, TLDs."""

free_email_domains: tuple[str, ...] = (
    "gmail.com",
    "yahoo.co.uk",
    "hotmail.co.uk",
    "outlook.com",
    "btinternet.com",
    "sky.com",
    "talktalk.net",
    "virgin.net",
)

domain_suffixes: tuple[str, ...] = (
    "co.uk",
    "org.uk",
    "com",
    "net",
    "org",
    "me.uk",
    "uk",
    "gov.uk",
    "ac.uk",
    "nhs.uk",
)

user_formats: tuple[str, ...] = (
    "{first}.{last}",
    "{first}_{last}",
    "{first}{last}",
    "{first}.{last}##",
    "{first}##",
    "{last}##",
)

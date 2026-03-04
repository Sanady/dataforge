"""en_AU internet data — domains, free email providers, TLDs."""

free_email_domains: tuple[str, ...] = (
    "gmail.com",
    "yahoo.com.au",
    "hotmail.com.au",
    "outlook.com",
    "bigpond.com",
    "optusnet.com.au",
    "iinet.net.au",
    "internode.on.net",
)

domain_suffixes: tuple[str, ...] = (
    "com.au",
    "net.au",
    "org.au",
    "edu.au",
    "gov.au",
    "com",
    "net",
    "org",
    "id.au",
    "asn.au",
)

user_formats: tuple[str, ...] = (
    "{first}.{last}",
    "{first}_{last}",
    "{first}{last}",
    "{first}.{last}##",
    "{first}##",
    "{last}##",
)

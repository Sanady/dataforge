"""pl_PL internet data — domains, free email providers, TLDs."""

free_email_domains: tuple[str, ...] = (
    "gmail.com",
    "wp.pl",
    "onet.pl",
    "interia.pl",
    "o2.pl",
    "gazeta.pl",
    "poczta.fm",
    "tlen.pl",
    "outlook.com",
    "yahoo.com",
)

domain_suffixes: tuple[str, ...] = (
    "pl",
    "com",
    "org",
    "eu",
    "com.pl",
    "net.pl",
    "org.pl",
    "info.pl",
    "net",
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

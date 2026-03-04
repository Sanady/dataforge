"""ja_JP internet data."""

free_email_domains: tuple[str, ...] = (
    "gmail.com",
    "yahoo.co.jp",
    "outlook.jp",
    "icloud.com",
    "docomo.ne.jp",
    "ezweb.ne.jp",
    "softbank.ne.jp",
    "nifty.com",
)

domain_suffixes: tuple[str, ...] = (
    "jp",
    "co.jp",
    "ne.jp",
    "or.jp",
    "com",
    "net",
    "org",
)

user_formats: tuple[str, ...] = (
    "{first}.{last}",
    "{first}_{last}",
    "{first}{last}",
    "{first}.{last}##",
    "{first}##",
)

"""zh_CN internet data."""

free_email_domains: tuple[str, ...] = (
    "qq.com",
    "163.com",
    "126.com",
    "sina.com",
    "sohu.com",
    "gmail.com",
    "outlook.com",
    "yeah.net",
)

domain_suffixes: tuple[str, ...] = (
    "cn",
    "com.cn",
    "net.cn",
    "org.cn",
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

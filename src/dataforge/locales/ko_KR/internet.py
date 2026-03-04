"""ko_KR internet data."""

free_email_domains: tuple[str, ...] = (
    "gmail.com",
    "naver.com",
    "daum.net",
    "hanmail.net",
    "kakao.com",
    "outlook.com",
    "nate.com",
    "yahoo.co.kr",
)

domain_suffixes: tuple[str, ...] = (
    "kr",
    "co.kr",
    "or.kr",
    "ne.kr",
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

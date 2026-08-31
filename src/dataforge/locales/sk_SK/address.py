"""sk_SK address data — streets, cities, regions, zip formats."""

street_names: tuple[str, ...] = (
    "Hlavná",
    "Štúrova",
    "Moyzesova",
    "Hviezdoslavova",
    "Štefánikova",
    "Dlhá",
    "Záhradná",
    "Lipová",
    "Masarykova",
    "Tyršova",
    "Jiráskova",
    "Palackého",
    "Národná",
    "Školská",
    "Poštová",
    "Vajanského",
    "Kollárova",
    "Bernolákova",
    "Zochova",
    "Ventúrska",
)

street_suffixes: tuple[str, ...] = (
    "ulica",
    "námestie",
    "trieda",
    "nábrežie",
)

cities: tuple[str, ...] = (
    "Bratislava",
    "Košice",
    "Prešov",
    "Žilina",
    "Banská Bystrica",
    "Nitra",
    "Trnava",
    "Martin",
    "Trenčín",
    "Poprad",
    "Prievidza",
    "Zvolen",
    "Považská Bystrica",
    "Michalovce",
    "Spišská Nová Ves",
    "Komárno",
    "Levice",
    "Humenné",
    "Bardejov",
    "Liptovský Mikuláš",
)

states: tuple[str, ...] = (
    "Bratislavský",
    "Trnavský",
    "Trenčiansky",
    "Nitriansky",
    "Žilinský",
    "Banskobystrický",
    "Prešovský",
    "Košický",
)

zip_formats: tuple[str, ...] = ("### ##",)

building_number_formats: tuple[str, ...] = (
    "#",
    "##",
    "###",
    "##/##",
)

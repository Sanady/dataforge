"""cs_CZ address data — streets, cities, regions, zip formats."""

street_names: tuple[str, ...] = (
    "Hlavní",
    "Náměstí Míru",
    "Václavské náměstí",
    "Karlova",
    "Celetná",
    "Dlouhá",
    "Vinohradská",
    "Školská",
    "Zahradní",
    "Lipová",
    "Masarykova",
    "Tyršova",
    "Jiráskova",
    "Palackého",
    "Sokolovská",
    "Národní",
    "Revoluční",
    "Polská",
    "Řehořova",
    "Korunní",
)

street_suffixes: tuple[str, ...] = (
    "ulice",
    "náměstí",
    "třída",
    "nábřeží",
)

cities: tuple[str, ...] = (
    "Praha",
    "Brno",
    "Ostrava",
    "Plzeň",
    "Liberec",
    "Olomouc",
    "České Budějovice",
    "Hradec Králové",
    "Ústí nad Labem",
    "Pardubice",
    "Zlín",
    "Havlíčkův Brod",
    "Kladno",
    "Most",
    "Opava",
    "Frýdek-Místek",
    "Karviná",
    "Jihlava",
    "Teplice",
    "Karlovy Vary",
)

states: tuple[str, ...] = (
    "Praha",
    "Středočeský",
    "Jihočeský",
    "Plzeňský",
    "Karlovarský",
    "Ústecký",
    "Liberecký",
    "Královéhradecký",
    "Pardubický",
    "Vysočina",
    "Jihomoravský",
    "Olomoucký",
    "Zlínský",
    "Moravskoslezský",
)

zip_formats: tuple[str, ...] = ("### ##",)

building_number_formats: tuple[str, ...] = (
    "#",
    "##",
    "###",
    "##/##",
)

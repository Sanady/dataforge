"""hu_HU address data — streets, cities, counties, zip formats."""

street_names: tuple[str, ...] = (
    "Petőfi Sándor",
    "Kossuth Lajos",
    "Rákóczi Ferenc",
    "Széchenyi István",
    "Deák Ferenc",
    "József Attila",
    "Ady Endre",
    "Bartók Béla",
    "Kodály Zoltán",
    "Arany János",
    "Vörösmarty Mihály",
    "Móricz Zsigmond",
    "Hunyadi János",
    "Mátyás király",
    "Szent István",
    "Andrássy",
    "Váci",
    "Dózsa György",
    "Bajcsy-Zsilinszky",
    "Erzsébet",
)

street_suffixes: tuple[str, ...] = (
    "utca",
    "út",
    "tér",
    "körút",
    "sétány",
)

cities: tuple[str, ...] = (
    "Budapest",
    "Debrecen",
    "Szeged",
    "Miskolc",
    "Pécs",
    "Győr",
    "Nyíregyháza",
    "Kecskemét",
    "Székesfehérvár",
    "Szombathely",
    "Szolnok",
    "Tatabánya",
    "Kaposvár",
    "Érd",
    "Veszprém",
    "Békéscsaba",
    "Zalaegerszeg",
    "Sopron",
    "Eger",
    "Nagykanizsa",
)

states: tuple[str, ...] = (
    "Budapest",
    "Baranya",
    "Bács-Kiskun",
    "Békés",
    "Borsod-Abaúj-Zemplén",
    "Csongrád-Csanád",
    "Fejér",
    "Győr-Moson-Sopron",
    "Hajdú-Bihar",
    "Heves",
    "Jász-Nagykun-Szolnok",
    "Komárom-Esztergom",
    "Nógrád",
    "Pest",
    "Somogy",
    "Szabolcs-Szatmár-Bereg",
    "Tolna",
    "Vas",
    "Veszprém",
    "Zala",
)

zip_formats: tuple[str, ...] = ("####",)

building_number_formats: tuple[str, ...] = (
    "#",
    "##",
    "###",
    "#/A",
)

import time
import json
from pathlib import Path

import requests
import pandas as pd


# ==========================================================
# PATHS + CACHE
# ==========================================================
BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

OUT_CSV = BASE_DIR / "countries_master.csv"


# ==========================================================
# RESTCOUNTRIES v3.1
# IMPORTANTÍSIMO: fields tiene límite de 10 campos → split en 2 calls
# ==========================================================
RESTCOUNTRIES_BASE = "https://restcountries.com/v3.1/all"

FIELDS_CORE = ",".join([
    "name", "cca2", "cca3", "region", "subregion",
    "capital", "area", "population", "landlocked", "car"
])  # 10

FIELDS_EXTRA = ",".join([
    "cca3", "borders", "flags", "languages", "timezones"
])  # 5


# ==========================================================
# WORLDBANK (bulk)
# ==========================================================
WDI_ALL_BASE = (
    "https://api.worldbank.org/v2/country/all/indicator/{indicator}"
    "?format=json&per_page=20000"
)


# ==========================================================
# HTTP HELPERS
# ==========================================================
def get_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": "GeoGridHelper/1.0 (Matias)",
        "Accept": "application/json",
    })
    return s


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, obj):
    path.write_text(json.dumps(obj), encoding="utf-8")


def get_json_with_cache(url: str, cache_name: str, params=None, timeout=90, retries=4):
    cache_path = CACHE_DIR / cache_name
    if cache_path.exists():
        return _read_json(cache_path)

    session = get_session()
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            r = session.get(url, params=params, timeout=timeout)
            r.raise_for_status()
            js = r.json()
            _write_json(cache_path, js)
            return js
        except Exception as e:
            last_err = e
            time.sleep(2 * attempt)
    raise last_err


# ==========================================================
# RESTCOUNTRIES (v3.1 split + merge)
# ==========================================================
def fetch_restcountries_v3_split() -> pd.DataFrame:
    """
    Trae RESTCountries v3.1 con split (por límite 10 fields):
      - CORE: básicos + landlocked + car.side
      - EXTRA: borders + flags + languages + timezones
    Usa cache en disco.
    """

    core = get_json_with_cache(
        RESTCOUNTRIES_BASE,
        cache_name="restcountries_v3_core.json",
        params={"fields": FIELDS_CORE},
        timeout=120,
        retries=4,
    )

    extra = get_json_with_cache(
        RESTCOUNTRIES_BASE,
        cache_name="restcountries_v3_extra.json",
        params={"fields": FIELDS_EXTRA},
        timeout=120,
        retries=4,
    )

    # index EXTRA por iso3
    extra_by_iso3 = {}
    for c in (extra or []):
        iso3 = c.get("cca3")
        if iso3:
            extra_by_iso3[iso3] = c

    rows = []
    for c in (core or []):
        name = (c.get("name") or {}).get("common")
        iso2 = c.get("cca2")
        iso3 = c.get("cca3")
        if not name or not iso2 or not iso3:
            continue

        car = c.get("car") or {}
        driving_side_raw = car.get("side") if isinstance(car, dict) else None

        x = extra_by_iso3.get(iso3, {}) or {}
        borders = x.get("borders") or []
        flags = x.get("flags") or {}
        langs = x.get("languages") or {}     # dict: code -> language name
        timezones = x.get("timezones") or [] # list

        # languages → "English|French|..."
        lang_list = [v for v in langs.values() if isinstance(v, str)]
        lang_list = sorted(set(lang_list))
        official_languages_rc = "|".join(lang_list) if lang_list else ""

        tz_count = len([t for t in timezones if isinstance(t, str) and t.strip()])

        rows.append({
            "name": name,
            "iso2": iso2,
            "iso3": iso3,
            "region": c.get("region"),
            "subregion": c.get("subregion"),
            "capital": (c.get("capital") or [None])[0],
            "area_km2": c.get("area"),
            "population": c.get("population"),
            "borders_iso3": ",".join(borders),
            "borders_count": len(borders),
            "landlocked_raw": c.get("landlocked"),      # True/False/None
            "driving_side_raw": driving_side_raw,       # left/right/None
            "flag_png": flags.get("png"),
            "flag_svg": flags.get("svg"),
            "official_languages_rc": official_languages_rc,
            "timezones_count": tz_count,
        })

    df = pd.DataFrame(rows).drop_duplicates(subset=["iso3"]).reset_index(drop=True)

    # --- normalizaciones booleanas 0/1/NA (Int64) ---
    df["landlocked_01"] = pd.Series(pd.NA, index=df.index, dtype="Int64")

    df.loc[df["landlocked_raw"] == True, "landlocked_01"] = 1
    df.loc[df["landlocked_raw"] == False, "landlocked_01"] = 0

    df["drives_left"] = pd.Series(pd.NA, index=df.index, dtype="Int64")
    df.loc[df["driving_side_raw"] == "left", "drives_left"] = 1
    df.loc[df["driving_side_raw"] == "right", "drives_left"] = 0

    # Derivado (redundante, pero a veces lo querías para filtro rápido)
    df["has_coast"] = pd.Series(pd.NA, index=df.index, dtype="Int64")
    df.loc[df["landlocked_01"] == 1, "has_coast"] = 0
    df.loc[df["landlocked_01"] == 0, "has_coast"] = 1

    df["is_island_heuristic"] = pd.Series(pd.NA, index=df.index, dtype="Int64")
    df.loc[(df["borders_count"] == 0) & (df["landlocked_01"] == 0), "is_island_heuristic"] = 1
    df.loc[(df["borders_count"] > 0), "is_island_heuristic"] = 0

    df["has_more_than_1_time_zone"] = pd.Series(pd.NA, index=df.index, dtype="Int64")
    df.loc[df["timezones_count"].notna(), "has_more_than_1_time_zone"] = (
        df.loc[df["timezones_count"].notna(), "timezones_count"].astype(int) > 1
    ).astype(int)

    return df


# ==========================================================
# WORLDBANK (bulk, 1 request por indicador)
# ==========================================================
def latest_by_iso3_worldbank(indicator: str) -> dict:
    js = get_json_with_cache(
        WDI_ALL_BASE.format(indicator=indicator),
        cache_name=f"wdi_{indicator}.json",
        timeout=180,
        retries=4,
    )

    if not isinstance(js, list) or len(js) < 2 or not js[1]:
        return {}

    out = {}
    for obs in js[1]:
        iso3 = obs.get("countryiso3code")
        val = obs.get("value")
        year = obs.get("date")
        if not iso3 or val is None:
            continue
        if iso3 not in out:  # primer valor no nulo suele ser el más reciente
            out[iso3] = (year, val)
    return out


def add_world_bank(df: pd.DataFrame) -> pd.DataFrame:
    IND_GDP_PC = "NY.GDP.PCAP.CD"              # GDP per capita (current US$)
    IND_HOMICIDE = "VC.IHR.PSRC.P5"            # Intentional homicides per 100k
    IND_NUCLEAR_ELEC_SHARE = "EG.ELC.NUCL.ZS"  # Electricity from nuclear (%)

    print("   → World Bank: GDP per capita...")
    gdp = latest_by_iso3_worldbank(IND_GDP_PC)

    print("   → World Bank: Homicides/100k...")
    hom = latest_by_iso3_worldbank(IND_HOMICIDE)

    print("   → World Bank: Nuclear electricity share...")
    nuc = latest_by_iso3_worldbank(IND_NUCLEAR_ELEC_SHARE)

    df["gdp_pc_usd_year"] = df["iso3"].map(lambda k: gdp.get(k, (None, None))[0])
    df["gdp_pc_usd"] = df["iso3"].map(lambda k: gdp.get(k, (None, None))[1])

    df["homicides_year"] = df["iso3"].map(lambda k: hom.get(k, (None, None))[0])
    df["homicides_per_100k"] = df["iso3"].map(lambda k: hom.get(k, (None, None))[1])

    df["nuclear_elec_share_year"] = df["iso3"].map(lambda k: nuc.get(k, (None, None))[0])
    df["nuclear_elec_share_pct"] = df["iso3"].map(lambda k: nuc.get(k, (None, None))[1])

    # produces_nuclear_power: 1 / 0 / NA
    df["produces_nuclear_power"] = pd.Series(pd.NA, index=df.index, dtype="Int64")
    known = df["nuclear_elec_share_pct"].notna()
    df.loc[known & (df["nuclear_elec_share_pct"] > 0), "produces_nuclear_power"] = 1
    df.loc[known & (df["nuclear_elec_share_pct"] == 0), "produces_nuclear_power"] = 0

    # Top20 GDP per capita (ejemplo que ya tenías)
    df["gdp_pc_rank"] = df["gdp_pc_usd"].rank(ascending=False, method="min")
    df["top20_gdp_pc"] = df["gdp_pc_rank"].map(lambda r: 1 if pd.notna(r) and r <= 20 else 0)

    return df


# ==========================================================
# MAIN
# ==========================================================
def main():
    print("RUNNING FILE:", __file__)

    print("1) RESTCountries v3.1 (split core+extra)...")
    df = fetch_restcountries_v3_split()
    print(f"   OK: {len(df)} países")

    print("2) World Bank (bulk + cache)...")
    df = add_world_bank(df)
    print("   OK: World Bank agregado")

    df.sort_values("name", inplace=True)
    df.to_csv(OUT_CSV, index=False, encoding="utf-8")
    print(f"\nOK -> {OUT_CSV}")

    # sanity
    print("\nSANITY (5 filas):")
    cols = ["name", "landlocked_raw", "driving_side_raw", "flag_png", "official_languages_rc", "timezones_count"]
    print(df[cols].head(5).to_string(index=False))


if __name__ == "__main__":
    main()

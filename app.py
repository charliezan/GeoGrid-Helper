# app.py
import pandas as pd
import re
import streamlit as st
import plotly.express as px
from flag_color_sets import (
    FLAG_NCOLORS_ISO3,
    FLAG_ONLY_RED_WHITE_BLUE_ISO3,
    FLAG_WITHOUT_RED_WHITE_BLUE_ISO3,
    # opcional si querés filtros por color individual:
    FLAG_HAS_RED_ISO3, FLAG_HAS_WHITE_ISO3, FLAG_HAS_BLUE_ISO3,
    FLAG_HAS_GREEN_ISO3, FLAG_HAS_YELLOW_ISO3, FLAG_HAS_BLACK_ISO3,
)


# ==========================================================
# HARD-CODED TAGS (ISO3)
# ==========================================================
# NOTE: These lists are a "snapshot". Some categories change over time.
# We validate against ISO3 codes that exist in your CSV to avoid mismatches.

# -----------------------
# European Union (27)
# -----------------------
EU_ISO3 = {
    "AUT","BEL","BGR","HRV","CYP","CZE","DNK","EST","FIN","FRA","DEU","GRC","HUN",
    "IRL","ITA","LVA","LTU","LUX","MLT","NLD","POL","PRT","ROU","SVK","SVN","ESP","SWE"
}

# -----------------------
# Commonwealth (56)
# -----------------------
COMMONWEALTH_ISO3 = {
    "ATG","AUS","BHS","BGD","BRB","BLZ","BWA","BRN","CMR","CAN","CYP","DMA","FJI","GAB","GMB",
    "GHA","GRD","GUY","IND","JAM","KEN","KIR","LSO","MWI","MYS","MDV","MLT","MUS","MOZ","NAM",
    "NRU","NZL","NGA","PAK","PNG","RWA","KNA","LCA","VCT","WSM","SYC","SLE","SGP","SLB","ZAF",
    "LKA","SWZ","TZA","TON","TTO","TUV","UGA","GBR","VUT","ZMB"
}

# -----------------------
# Former USSR (15)
# -----------------------
USSR_FORMER_ISO3 = {
    "RUS","UKR","BLR","MDA","EST","LVA","LTU","GEO","ARM","AZE","KAZ","KGZ","TJK","TKM","UZB"
}

# -----------------------
# Monarchies (sovereign)
# -----------------------
MONARCHY_ISO3 = {
    "AND","BEL","DNK","LIE","LUX","MCO","NLD","NOR","ESP","SWE","GBR","VAT",
    "BHR","BRN","BTN","JPN","JOR","KHM","KWT","MYS","OMN","QAT","SAU","THA","ARE",
    "LSO","MAR","SWZ",
    "TON",
    # Commonwealth realms (also monarchies)
    "AUS","CAN","NZL","PNG","SLB","TUV","ATG","BHS","BLZ","GRD","JAM","KNA","LCA","VCT"
}

# -----------------------
# Dependencies / Territories
# -----------------------
DEPENDENCY_TERRITORY_ISO3 = {
    "ABW","AIA","ALA","ASM","BES","BMU","BVT","CCK","COK","CUW","CYM","FLK","FRO","GIB","GLP",
    "GRL","GUM","GUF","HKG","IOT","MAC","MAF","MNP","MSR","MTQ","MYT","NCL","NFK","NIU","PCN",
    "PRI","REU","SGS","SHN","SJM","SPM","TCA","VGB","VIR","WLF","PYF","ATA","ATF"
}

# -----------------------
# Nuclear weapons states
# -----------------------
NUCLEAR_WEAPONS_ISO3 = {"USA","RUS","CHN","FRA","GBR","IND","PAK","PRK","ISR"}

# -----------------------
# Same-sex marriage legal (snapshot)
# -----------------------
SAME_SEX_MARRIAGE_LEGAL_ISO3 = {
    # Americas
    "ARG","BRA","CAN","CHL","COL","CRI","CUB","ECU","MEX","USA","URY",
    # Europe
    "AND","AUT","BEL","DNK","EST","FIN","FRA","DEU","GRC","ISL","IRL","LUX","MLT","MNE",
    "NLD","NOR","PRT","SVN","ESP","SWE","CHE","GBR",
    # Oceania
    "AUS","NZL",
    # Africa
    "ZAF",
    # Asia
    "TWN","NPL"
}

# -----------------------
# Same-sex acts illegal (snapshot)
# -----------------------
SAME_SEX_ACTS_ILLEGAL_ISO3 = {
    "AFG","IRN","SAU","YEM","QAT","ARE","OMN","KWT",
    "NGA","UGA","GMB","SLE","SOM","SDN","TZA","CMR","SEN",
    "JAM","GUY"
}

# -----------------------
# Daylight Saving Time observed (snapshot)
# -----------------------
OBSERVES_DST_ISO3 = {
    "USA","CAN","MEX","CHL","PRY",
    "GBR","IRL","ESP","PRT","FRA","DEU","ITA","NLD","BEL","SWE","NOR","DNK","FIN","CHE",
    "AUS","NZL"
}

# ==========================================================
# SPORTS / EVENTS (hardcoded snapshots)
# ==========================================================
CAPITAL_NOT_LARGEST_ISO3 = {
    "AUS","BLZ","BEN","BOL","BRA","BDI","CMR","CAN","CHN","CIV","ECU","GNQ","SWZ",
    "GMB","IND","KAZ","LIE","MWI","MAR","MMR","NZL","NGA","PAK","PLW","PHL","SMR",
    "ZAF","LKA","TZA","TUR","ARE","USA","VNM"
}

HOSTED_F1_GP_ISO3 = {
    "ARG","AUS","AUT","AZE","BHR","BEL","BRA","CAN","CHN","DEU","ESP","FRA","GBR",
    "HUN","IND","ITA","JPN","KOR","MAR","MCO","MEX","MYS","NLD","PRT","QAT","RUS",
    "SAU","SGP","SWE","CHE","TUR","ARE","USA","ZAF"
}

NEVER_WON_OLYMPIC_MEDAL_ISO3 = {
    "ASM","AND","AGO","ATG","ABW","BGD","BLZ","BEN","BTN","BOL","BIH","VGB","BRN",
    "KHM","CYM","CAF","TCD","COM","COG","COD","COK","SLV","SWZ","GNQ","GMB","GUM",
    "GIN","GNB","HND","KIR","LAO","LSO","LBR","LBY","MDG","MWI","MDV","MLI","MLT",
    "MHL","MRT","FSM","MCO","MMR","NRU","NPL","NIC",
    "NER","OMN","PLW","PSE","PNG","WSM","SMR","STP","SLE","SLB","SOM","SSD",
    "TLS","TGO","TON","TUV","VUT","YEM"
}

HOSTED_OLYMPICS_ISO3 = {
    "GRC","FRA","USA","GBR","SWE","BEL","NLD","DEU","FIN","AUS","ITA","JPN","MEX",
    "CAN","RUS","KOR","ESP","CHN","BRA","CHE","NOR","AUT","BIH"
}

HOSTED_MENS_FIFA_WC_ISO3 = {
    "URY","ITA","FRA","BRA","CHE","SWE","CHL","GBR","MEX","DEU","ARG","ESP","USA",
    "KOR","JPN","ZAF","RUS","QAT","CAN",
    # future awarded hosts (snapshot)
    "MAR","PRT","PRY","SAU"
}

PLAYED_MENS_FIFA_WC_ISO3 = {
    # Europe
    "ALB","AND","AUT","BEL","BGR","BIH","BLR","CHE","CZE","DEU","DNK","ESP","EST","FIN","FRA","GBR",
    "GRC","HRV","HUN","IRL","ISL","ITA","LVA","LTU","LUX","MDA","MKD","MNE","NLD","NOR","POL","PRT",
    "ROU","RUS","SRB","SVK","SVN","SWE","TUR","UKR","WAL","SCO",
    # Americas
    "ARG","BOL","BRA","CAN","CHL","COL","CRI","CUB","DOM","ECU","GTM","HND","HTI","JAM","MEX","NIC",
    "PAN","PAR","PER","SLV","TTO","URY","USA","VEN",
    # Africa
    "AGO","ALG","CMR","CIV","COD","CPV","EGY","GHA","GIN","GMB","KEN","MAR","MLI","MOZ","NGA","SEN",
    "RSA","TUN","UGA","ZAF","ZMB","ZWE",
    # Asia/Oceania
    "AUS","CHN","IRN","IRQ","JPN","KOR","KSA","KWT","QAT","ARE","OMN","UZB","TJK","TKM",
    "IND","IDN","MYS","SGP","THA","VNM",
    "NZL","PNG"
}

WON_MENS_FIFA_WC_ISO3 = {"ARG","BRA","DEU","ESP","FRA","GBR","ITA","URY"}

# ==========================================================
# GEO / PRODUCTION / SKYLINE (hardcoded snapshots)
# ==========================================================
TOUCHES_EQUATOR_ISO3 = {"ECU","COL","BRA","STP","GAB","COG","COD","UGA","KEN","SOM","IDN","KIR","MDV"}
TOUCHES_SAHARA_ISO3 = {"DZA","TCD","EGY","LBY","MLI","MRT","MAR","NER","SDN","TUN","ESH"}

TOUCHES_EURASIAN_STEPPE_ISO3 = {
    "HUN","ROU","SVK","AUT",
    "UKR","MDA","RUS",
    "KAZ","MNG","CHN",
    "UZB","TKM","KGZ","TJK","AFG"
}

TOP20_WHEAT_PRODUCTION_ISO3 = {
    "CHN","IND","RUS","USA","FRA","CAN","PAK","DEU","TUR","UKR",
    "AUS","KAZ","GBR","POL","BRA","IRN","EGY","ITA","ESP","BGR"
}

TOP20_OIL_PRODUCTION_ISO3 = {
    "USA","SAU","RUS","CAN","CHN","BRA","IRQ","IRN","ARE","KWT",
    "NOR","KAZ","MEX","QAT","NGA","DZA","LBY","VEN","AGO","OMN"
}

HAS_50PLUS_SKYSCRAPERS_ISO3 = {
    "CHN","USA","IND","ARE","MYS","JPN","KOR","CAN","AUS","THA",
    "IDN","PHL","SGP","TUR","TWN","BRA","PAN","RUS","QAT","MEX","GBR"
}

# ==========================================================
# LIFESTYLE / TRANSPORT / TOURISM (hardcoded snapshots)
# ==========================================================
ALCOHOL_PROHIBITION_ISO3 = {"AFG","BRN","IRN","KWT","LBY","MRT","SAU","SOM","YEM"}

TOP20_ALCOHOL_CONSUMPTION_ISO3 = {
    "EST","LTU","CZE","SYC","DEU","NGA","IRL","MDA","LVA","BGR",
    "FRA","ROU","SVN","PRT","LUX","BEL","RUS","AUT","POL","GAB"
}

TOP20_RAIL_NETWORK_ISO3 = {
    "USA","CHN","RUS","IND","CAN","DEU","AUS","BRA","FRA","JPN",
    "ITA","MEX","ZAF","ROU","UKR","POL","ARG","IRN","ESP","GBR"
}

TOP20_TOURIST_ARRIVALS_2024_ISO3 = {
    "USA","MEX","CAN","DOM","BRA","ARG","COL","PRI","CHL","PER",
    "FRA","ESP","TUR","ITA","GBR","DEU","GRC","AUT","PRT","NLD"
}

TOP20_CHOCOLATE_CONSUMPTION_ISO3 = {
    "USA","GBR","FRA","JPN","SAU","DEU","IRQ","ROU","RUS","KAZ",
    "UKR","PHL","TUR","PRT","CHN","ISR","CHL","DNK","TWN","SRB"
}

TOP20_WORLD_HERITAGE_SITES_ISO3 = {
    "ITA","CHN","DEU","FRA","ESP","IND","MEX","GBR","RUS","IRN",
    "USA","JPN","BRA","AUS","CAN","TUR","GRC","CZE","PRT","POL"
}

TOP10_LAKES_COUNT_ISO3 = {"CAN","RUS","FIN","DNK","USA","GBR","CHN","SWE","BRA","NOR"}

# ==========================================================
# RIVER SYSTEMS (filter-only)
# ==========================================================
RIVER_SYSTEMS_ISO3 = {
    "Nile": {"EGY","SDN","SSD","ETH","UGA","KEN","TZA","RWA","BDI","COD","ERI"},
    "Amazon": {"BRA","PER","COL","BOL","ECU","VEN","GUY","SUR"},
    "Yangtze (Chang Jiang)": {"CHN"},
    "Yellow River (Huang He)": {"CHN"},
    "Mississippi–Missouri": {"USA"},
    "Congo": {"COD","COG","CAF","CMR","AGO","ZMB","TZA","RWA","BDI"},
    "Niger": {"GIN","MLI","NER","NGA","BEN","BFA","CIV","CMR","TCD"},
    "Mekong": {"CHN","MMR","LAO","THA","KHM","VNM"},
    "Ganges–Brahmaputra–Meghna": {"IND","BGD","NPL","BTN","CHN"},
    "Indus": {"PAK","IND","AFG","CHN"},
    "Danube": {"DEU","AUT","SVK","HUN","HRV","SRB","ROU","BGR","MDA","UKR","SVN","BIH"},
    "Volga": {"RUS"},
    "Ob–Irtysh": {"RUS","KAZ","CHN"},
    "Yenisei–Angara": {"RUS","MNG"},
    "Lena": {"RUS"},
    "Amur (Heilong Jiang)": {"RUS","CHN","MNG"},
    "Paraná–Paraguay–La Plata": {"BRA","PRY","ARG","URY","BOL"},
    "Orinoco": {"VEN","COL"},
    "Murray–Darling": {"AUS"},
    "Zambezi": {"ZMB","AGO","NAM","BWA","ZWE","MOZ","MWI","TZA"},
    "Orange": {"ZAF","LSO","NAM","BWA"},
    "Colorado": {"USA","MEX"},
    "Rio Grande": {"USA","MEX"},
}

# ==========================================================
# COASTLINES (hardcoded snapshots)
# ==========================================================
COAST_MEDITERRANEAN_ISO3 = {
    "ESP","FRA","MCO","ITA","MLT","SVN","HRV","BIH","MNE","ALB","GRC","TUR","CYP",
    "MAR","DZA","TUN","LBY","EGY","ISR","LBN","SYR","PSE"
}
COAST_INDIAN_OCEAN_ISO3 = {
    "ZAF","MOZ","TZA","KEN","SOM","MDG","COM","MUS","SYC","DJI",
    "OMN","YEM","ARE","IRN","PAK","IND","BGD","LKA","MDV",
    "MMR","THA","MYS","IDN","TLS","AUS"
}
COAST_PACIFIC_OCEAN_ISO3 = {
    "CAN","USA","MEX","GTM","SLV","HND","NIC","CRI","PAN","COL","ECU","PER","CHL",
    "RUS","JPN","PRK","KOR","CHN","TWN","PHL","VNM",
    "AUS","NZL","PNG","FJI","SLB","VUT","WSM","TON","KIR","TUV","NRU","MHL","FSM","PLW"
}
COAST_ATLANTIC_OCEAN_ISO3 = {
    "CAN","USA","MEX","BLZ","GTM","HND","NIC","CRI","PAN","CUB","JAM","HTI","DOM",
    "BHS","TTO","BRB","ATG","DMA","GRD","KNA","LCA","VCT",
    "COL","VEN","GUY","SUR","BRA","URY","ARG",
    "ISL","IRL","GBR","PRT","ESP","FRA","BEL","NLD","DEU","DNK","NOR",
    "MAR","ESH","MRT","SEN","GMB","GNB","GIN","SLE","LBR","CIV","GHA","TGO","BEN",
    "NGA","CMR","GNQ","GAB","COG","COD","AGO","NAM","ZAF",
}
COAST_NORTH_ATLANTIC_ISO3 = {
    "CAN","USA","ISL","IRL","GBR","PRT","ESP","FRA","BEL","NLD","DEU","DNK","NOR",
    "MAR","ESH","MRT","SEN","GMB","GNB","GIN"
}
COAST_SOUTH_ATLANTIC_ISO3 = {"BRA","URY","ARG","AGO","NAM","ZAF","COD","COG","GAB","GNQ"}
COAST_CARIBBEAN_SEA_ISO3 = {
    "MEX","BLZ","GTM","HND","NIC","CRI","PAN","COL","VEN","CUB","JAM","HTI","DOM","TTO",
    "ATG","BRB","DMA","GRD","KNA","LCA","VCT","BHS"
}
COAST_BLACK_SEA_ISO3 = {"TUR","BGR","ROU","UKR","RUS","GEO"}
COAST_BALTIC_SEA_ISO3 = {"DNK","DEU","POL","RUS","LTU","LVA","EST","FIN","SWE"}
COAST_EAST_CHINA_SEA_ISO3 = {"CHN","JPN","KOR","TWN"}
COAST_SOUTH_CHINA_SEA_ISO3 = {"CHN","TWN","PHL","VNM","MYS","BRN","IDN","SGP","THA","KHM"}

# ==========================================================
# FLAG-BASED (hardcoded snapshots) — star / coat of arms / animal
# ==========================================================
# Source:
# https://en.wikipedia.org/wiki/List_of_national_flags_by_design#Star
# Only sovereign states (current national flags)

FLAG_HAS_SUN_ISO3 = {
    # Americas
    "ATG", ## Antigua and Barbuda
    "ARG",  ## Argentina
    "BRA",  ## Brazil
    "CRI",  ## Costa Rica
    "ECU",  ## Ecuador
    "GRL",  ## Greenland
    "GLP",  ## Guadeloupe
    "SLV",  ## El Salvador
    "MAF",  ## Saint Martin
    "SXM",  ## Sint Maarten
    "URY",  ## Uruguay

    # Asia
    "BGD", ## Bangladesh
    "JPN",  ## Japan
    "KZA",  ## Kazakhstan
    "KGZ",  ## Kyrgyzstan
    "MNG",  ## Mongolia
    "NPL",  ## Nepal
    "PHL",  ## Philippines
    "REU",  ## Réunion
    "TWN",  ## Taiwan

    # Africa
    "MWI",  ## Malawi
    "NAM",  ## Namibia
    "RWA",  ## Rwanda
    "NER",  ## Niger

    # Europe
    "MKD",  ## North Macedonia

    # Oceania
    "KIR"   ## Kiribati
    "NCL"   ## New Caledonia
}


FLAG_HAS_STAR_ISO3 = {
    # Americas
    "USA",  ## United States
    "CHL",  ## Chile
    "CUB",  ## Cuba
    "PAN",  ## Panama
    "VEN",  ## Venezuela
    "BRA",  ## Brazil
    "HND",  ## Honduras
    "PRY",  ## Paraguay
    "SUR",  ## Suriname
    "GUF",  ## French Guiana
    "PRI",  ## Puerto Rico
    "BOL",  ## Bolivia
    "CRI",  ## Costa Rica
    "KNA",  ## Saint Kitts and Nevis
    "DMA",  ## Dominica
    "CUW",  ## Curaçao
    "GRD",  ## Grenada
    "FLK",  ## Falkland Islands
    "ABW",  ## Aruba

    # Europe
    "BIH",  ## Bosnia and Herzegovina
    "MKD",  ## North Macedonia
    "TUR",  ## Turkey
    "KOS",  ## Kosovo
    "CRO",  ## Croatia
    "SLV",  ## Slovenia

    # Africa
    "DZA",  ## Algeria
    "BFA",  ## Burkina Faso
    "TUN",  ## Tunisia
    "MAR",  ## Morocco
    "SEN",  ## Senegal
    "GHA",  ## Ghana
    "CMR",  ## Cameroon
    "COD",  ## Democratic Republic of the Congo
    "AGO",  ## Angola
    "SOM",  ## Somalia
    "CPV",  ## Cape Verde
    "TGO",  ## Togo
    "GNQ",  ## Equatorial Guinea
    "LBY",  ## Libya
    "ETH",  ## Ethiopia
    "SSD",  ## South Sudan
    "DJI",  ## Djibouti
    "TLS",  ## Timor-Leste
    "GNB",  ## Guinea-Bissau
    "MOZ",  ## Mozambique
    "ZBE",  ## Zimbabwe
    "CAF",  ## Central African Republic
    "LBR",  ## Liberia
    "STP",  ## São Tomé and Príncipe
    "BDI",  ## Burundi

    # Asia
    "CHN",  ## China
    "VNM",  ## Vietnam
    "PRK",  ## North Korea
    "MYS",  ## Malaysia
    "SGP",  ## Singapore
    "PHL",  ## Philippines
    "PAK",  ## Pakistan
    "ISR",  ## Israel
    "JOR",  ## Jordan
    "SYR",  ## Syria
    "UZB",  ## Uzbekistan
    "AZE",  ## Azerbaijan
    "TKM",  ## Turkmenistan
    "NPL",  ## Nepal
    "MMR",  ## Myanmar
    "HKG",  ## Hong Kong
    "TJK",  ## Tajikistan
    "MAC",  ## Macau

    # Oceania
    "AUS",  ## Australia
    "NZL",  ## New Zealand
    "PNG",  ## Papua New Guinea
    "SLB",  ## Solomon Islands
    "WSM",  ## Samoa
    "TON",  ## Tonga
    "KIR",  ## Kiribati
    "TUV",  ## Tuvalu
    "NRU",  ## Nauru
    "MHL",  ## Marshall Islands
    "FSM",  ## Micronesia
    "MNP",  ## Northern Mariana Islands
    "ATF",  ## French Southern and Antarctic Lands
    "COK",  ## Cook Islands
    "NIU",  ## Niue
    "CXR",  ## Christmas Island
}

FLAG_HAS_COAT_OF_ARMS_ISO3_WIKI = {
    "AFG",  ## Afghanistan
    "AND",  ## Andorra
    "ALB",  ## Albania
    "AIA",  ## Anguilla
    "BLZ",  ## Belize
    "BMU",  ## Bermuda
    "BRA",  ## Brazil
    "VGB",  ## British Virgin Islands
    "BOL",  ## Bolivia
    "BRN",  ## Brunei
    "CYM",  ## Cayman Islands
    "CRI",  ## Costa Rica
    "HRV",  ## Croatia
    "DOM",  ## Dominican Republic
    "ECU",  ## Ecuador
    "EGY",  ## Egypt
    "ETH",  ## Ethiopia
    "SLV",  ## El Salvador
    "GNQ",  ## Equatorial Guinea
    "FLK",  ## Falkland Islands
    "FJI",  ## Fiji
    "GTM",  ## Guatemala
    "GIB",  ## Gibraltar
    "HTI",  ## Haiti
    "IMN",  ## Isle of Man
    "JEY",  ## Jersey
    "MYT",  ## Mayotte
    "MDA",  ## Moldova
    "MNE",  ## Montenegro
    "MEX",  ## Mexico
    "MSR",  ## Montserrat
    "NIC",  ## Nicaragua
    "PRY",  ## Paraguay
    "PCN",  ## Pitcairn Islands
    "PRT",  ## Portugal
    "PER",  ## Peru
    "BLM",  ## Saint Barthélemy
    "SHN",  ## Saint Helena
    "MAF",  ## Saint Martin
    "SXM",  ## Sint Maarten
    "SPM",  ## Saint Pierre and Miquelon
    "SMR",  ## San Marino
    "SRB",  ## Serbia
    "SVK",  ## Slovakia
    "SVN",  ## Slovenia
    "SGS",  ## South Georgia and the South Sandwich Islands
    "TCA",  ## Turks and Caicos Islands
    "ESP",  ## Spain
    "VIR",  ## U.S. Virgin Islands
    "VAT",  ## Vatican City
}

FLAG_HAS_ANIMAL_ISO3 = {

    # Europa
    "ALB",  # Albania – águila bicéfala
    "MNE",  # Montenegro – águila
    "SRB",  # Serbia – águila
    "MDA",  # Moldavia – águila
    "AND",  # Andorra – vaca en escudo
    "ESP",  # España – león en escudo

    # América
    "MEX",  # México – águila y serpiente
    "GTM",  # Guatemala – quetzal
    "ECU",  # Ecuador – cóndor
    "BOL",  # Bolivia – llama / cóndor en escudo
    "VEN",  # Venezuela – caballo
    "DOM",  # República Dominicana – escudo con fauna simbólica
    "PER",  # Perú – vicuña
    "BLZ",  # Belice – leones
    "CRI",  # Costa Rica – fauna en escudo
    "NIC",  # Nicaragua – escudo con fauna simbólica

    # África
    "UGA",  # Uganda – grulla
    "ZWE",  # Zimbabue – ave Zimbabwe
    "KEN",  # Kenia – leones
    "MWI",  # Malawi – león
    "ZMB",  # Zambia – águila
    "SWZ",  # Esuatini – león
    "NAM",  # Namibia – águila en escudo
    "ZAF",  # Sudáfrica – animales en escudo
    "LSO",  # Lesoto – cocodrilo en escudo

    # Asia
    "KAZ",  # Kazajistán – águila
    "KGZ",  # Kirguistán – águila
    "TJK",  # Tayikistán – fauna heráldica
    "BTN",  # Bután – dragón
    "LKA",  # Sri Lanka – león
    "TLS",  # Timor-Leste – ave
    "ARM",  # Armenia – león y águila
    "IRN",  # Irán – león histórico en escudo
    "MYS",  # Malasia – tigres en escudo

    # Oceanía
    "PNG",  # Papúa Nueva Guinea – ave del paraíso
    "FJI",  # Fiyi – león en escudo

    # Territorios / dependencias
    "TCA",  # Turks and Caicos – iguana
    "VGB",  # British Virgin Islands – santa + lámparas (símbolos)
    "CYM",  # Cayman Islands – tortuga
    "GIB",  # Gibraltar – castillo + animal heráldico
    "BMU",  # Bermuda – león
    "GRL",  # Groenlandia – oso polar
}

# ==========================================================
# Tags DF builder
# ==========================================================
def tags_dataframe(valid_iso3: set) -> pd.DataFrame:
    def normalize_set(s):
        return {str(x).strip().upper() for x in s if isinstance(x, str) and str(x).strip()}

    def mk(tag_set, col):
        tag_set = normalize_set(tag_set)
        tag_set = sorted(tag_set.intersection(valid_iso3))  # only ISO3 present in the CSV
        return pd.DataFrame({"iso3": tag_set, col: 1})

    dfs = [
        # Political
        mk(EU_ISO3, "is_eu_member"),
        mk(COMMONWEALTH_ISO3, "is_commonwealth_member"),
        mk(USSR_FORMER_ISO3, "was_part_of_ussr"),
        mk(MONARCHY_ISO3, "is_monarchy"),
        mk(DEPENDENCY_TERRITORY_ISO3, "is_dependency_or_territory"),
        mk(NUCLEAR_WEAPONS_ISO3, "has_nuclear_weapons"),
        mk(SAME_SEX_MARRIAGE_LEGAL_ISO3, "same_sex_marriage_legal"),
        mk(SAME_SEX_ACTS_ILLEGAL_ISO3, "same_sex_acts_illegal"),
        mk(OBSERVES_DST_ISO3, "observes_dst"),

        # Sports/events
        mk(CAPITAL_NOT_LARGEST_ISO3, "capital_not_largest_city"),
        mk(HOSTED_F1_GP_ISO3, "hosted_f1_grand_prix"),
        mk(NEVER_WON_OLYMPIC_MEDAL_ISO3, "never_won_olympic_medal"),
        mk(HOSTED_OLYMPICS_ISO3, "hosted_olympics"),
        mk(HOSTED_MENS_FIFA_WC_ISO3, "hosted_mens_fifa_world_cup"),
        mk(PLAYED_MENS_FIFA_WC_ISO3, "played_mens_fifa_world_cup"),
        mk(WON_MENS_FIFA_WC_ISO3, "won_mens_fifa_world_cup"),

        # Geo / production / skyline
        mk(TOUCHES_EQUATOR_ISO3, "touches_equator"),
        mk(TOUCHES_SAHARA_ISO3, "touches_sahara"),
        mk(TOUCHES_EURASIAN_STEPPE_ISO3, "touches_eurasian_steppe"),
        mk(TOP20_WHEAT_PRODUCTION_ISO3, "top20_wheat_production"),
        mk(TOP20_OIL_PRODUCTION_ISO3, "top20_oil_production"),
        mk(HAS_50PLUS_SKYSCRAPERS_ISO3, "has_50plus_skyscrapers"),

        # Lifestyle / transport / tourism
        mk(ALCOHOL_PROHIBITION_ISO3, "alcohol_prohibition"),
        mk(TOP20_ALCOHOL_CONSUMPTION_ISO3, "top20_alcohol_consumption"),
        mk(TOP20_CHOCOLATE_CONSUMPTION_ISO3, "top20_chocolate_consumption"),
        mk(TOP20_RAIL_NETWORK_ISO3, "top20_rail_network_size"),
        mk(TOP20_TOURIST_ARRIVALS_2024_ISO3, "top20_tourist_arrivals_2024"),
        mk(TOP20_WORLD_HERITAGE_SITES_ISO3, "top20_world_heritage_sites"),
        mk(TOP10_LAKES_COUNT_ISO3, "top10_number_of_lakes"),

        # Coastlines
        mk(COAST_MEDITERRANEAN_ISO3, "coast_mediterranean"),
        mk(COAST_INDIAN_OCEAN_ISO3, "coast_indian_ocean"),
        mk(COAST_PACIFIC_OCEAN_ISO3, "coast_pacific_ocean"),
        mk(COAST_ATLANTIC_OCEAN_ISO3, "coast_atlantic_ocean"),
        mk(COAST_NORTH_ATLANTIC_ISO3, "coast_north_atlantic"),
        mk(COAST_SOUTH_ATLANTIC_ISO3, "coast_south_atlantic"),
        mk(COAST_CARIBBEAN_SEA_ISO3, "coast_caribbean_sea"),
        mk(COAST_BLACK_SEA_ISO3, "coast_black_sea"),
        mk(COAST_BALTIC_SEA_ISO3, "coast_baltic_sea"),
        mk(COAST_EAST_CHINA_SEA_ISO3, "coast_east_china_sea"),
        mk(COAST_SOUTH_CHINA_SEA_ISO3, "coast_south_china_sea"),

        # Flags (hardcoded)
        mk(FLAG_HAS_STAR_ISO3, "flag_has_star"),
        mk(FLAG_HAS_SUN_ISO3, "flag_has_sun"),
        mk(FLAG_HAS_COAT_OF_ARMS_ISO3_WIKI, "flag_has_coat_of_arms"),
        mk(FLAG_HAS_ANIMAL_ISO3, "flag_has_animal"),

        # Flags (colors — auto-generated)
        mk(FLAG_NCOLORS_ISO3.get(1, set()), "flag_n_colors_1"),
        mk(FLAG_NCOLORS_ISO3.get(2, set()), "flag_n_colors_2"),
        mk(FLAG_NCOLORS_ISO3.get(3, set()), "flag_n_colors_3"),
        mk(FLAG_NCOLORS_ISO3.get(4, set()), "flag_n_colors_4"),
        mk(FLAG_NCOLORS_ISO3.get(5, set()), "flag_n_colors_5"),
        mk(FLAG_NCOLORS_ISO3.get(6, set()), "flag_n_colors_6"),
        mk(FLAG_NCOLORS_ISO3.get(7, set()), "flag_n_colors_7"),
        mk(FLAG_NCOLORS_ISO3.get(8, set()), "flag_n_colors_8"),
        mk(FLAG_NCOLORS_ISO3.get(9, set()), "flag_n_colors_9"),
        mk(FLAG_NCOLORS_ISO3.get(10, set()), "flag_n_colors_10"),
        mk(FLAG_NCOLORS_ISO3.get(11, set()), "flag_n_colors_11"),
        mk(FLAG_NCOLORS_ISO3.get(12, set()), "flag_n_colors_12"),

        mk(FLAG_ONLY_RED_WHITE_BLUE_ISO3, "flag_only_red_white_blue"),
        mk(FLAG_WITHOUT_RED_WHITE_BLUE_ISO3, "flag_without_red_white_blue"),
        mk(FLAG_HAS_RED_ISO3, "flag_has_red"),
        mk(FLAG_HAS_WHITE_ISO3, "flag_has_white"),
        mk(FLAG_HAS_BLUE_ISO3, "flag_has_blue"),
        mk(FLAG_HAS_GREEN_ISO3, "flag_has_green"),
        mk(FLAG_HAS_YELLOW_ISO3, "flag_has_yellow"),
        mk(FLAG_HAS_BLACK_ISO3, "flag_has_black"),

    ]

    out = None
    for d in dfs:
        out = d if out is None else out.merge(d, on="iso3", how="outer")

    out = out.fillna(0)
    for c in out.columns:
        if c != "iso3":
            out[c] = out[c].astype("Int64")
    return out

# ==========================================================
# Utils
# ==========================================================
def name_letters_only(name: str) -> str:
    if pd.isna(name):
        return ""
    return "".join(ch for ch in str(name) if ch.isalpha())

def apply_name_filters(df, ends=None, starts=None, length=None, contains=None, multiword="(ANY)"):
    x = df.copy()
    x["name"] = x["name"].astype(str)

    if ends:
        x = x[x["name"].str.lower().str.endswith(str(ends).lower())]
    if starts:
        x = x[x["name"].str.lower().str.startswith(str(starts).lower())]
    if length and int(length) > 0:
        x = x[x["name"].apply(lambda s: len(name_letters_only(s)) == int(length))]
    if contains:
        x = x[x["name"].str.lower().str.contains(str(contains).lower(), regex=False)]

    if multiword != "(ANY)":
        want = (multiword == "Yes")
        x = x[x["name"].apply(has_multiple_words) == want]

    return x


def has_multiple_words(name: str) -> bool:
    """True si el nombre tiene 2+ palabras (ignorando espacios dobles, tabs, etc.)."""
    if pd.isna(name):
        return False
    parts = [p for p in re.split(r"\s+", str(name).strip()) if p]
    return len(parts) >= 2

def filter_01(series, choice):
    if choice == "(ANY)":
        return series.index
    if choice == "Yes":
        return series[series == 1].index
    if choice == "No":
        return series[series == 0].index
    if choice == "No data":
        return series[series.isna()].index
    return series.index

def nice_step(max_value: float) -> float:
    if max_value <= 100:
        return 1.0
    if max_value <= 1_000:
        return 5.0
    if max_value <= 10_000:
        return 50.0
    if max_value <= 100_000:
        return 500.0
    if max_value <= 1_000_000:
        return 5_000.0
    if max_value <= 10_000_000:
        return 50_000.0
    if max_value <= 100_000_000:
        return 500_000.0
    return 5_000_000.0

def split_languages(lang_str: str):
    if not isinstance(lang_str, str) or not lang_str:
        return []
    return [x.strip() for x in lang_str.split("|") if x.strip()]

def apply_yesno_filter(df_in, col, choice):
    if col not in df_in.columns or choice == "(ANY)":
        return df_in
    if choice == "Yes":
        return df_in[df_in[col] == 1]
    return df_in[df_in[col] == 0]

def normalize_iso3_set(s):
    return {str(x).strip().upper() for x in s if isinstance(x, str) and str(x).strip()}

# ==========================================================
# App
# ==========================================================
st.set_page_config(page_title="GeoGrid Helper", layout="wide")
st.title("GeoGrid Helper — Filters + Map + Flags")
st.link_button("🌍 Play GeoGrid Game", "https://www.geogridgame.com/")

@st.cache_data
def load_data():
    df = pd.read_csv("countries_master.csv")

    # Drop duplicated columns (keep first)
    if df.columns.duplicated().any():
        df = df.loc[:, ~df.columns.duplicated()]

    # Normalize iso3
    if "iso3" in df.columns:
        df["iso3"] = df["iso3"].astype(str).str.strip().str.upper()

    # Strings
    for col in [
        "name", "region", "subregion", "capital", "borders_iso3", "driving_side_raw",
        "official_languages_rc", "flag_png", "iso2", "iso3"
    ]:
        if col in df.columns:
            df[col] = df[col].astype("string")

    # Numerics
    for col in ["area_km2", "population", "borders_count", "gdp_pc_usd", "homicides_per_100k", "timezones_count"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 0/1/NA columns from dataset build (if present)
    for col in [
        "landlocked_01", "drives_left", "is_island_heuristic", "produces_nuclear_power",
        "top20_gdp_pc", "has_more_than_1_time_zone", "top20_domestic_renewable_share"
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    if "official_languages_rc" in df.columns:
        df["official_languages_rc"] = df["official_languages_rc"].fillna("").astype("string")

    if "iso3" in df.columns:
        df = df.drop_duplicates(subset=["iso3"]).reset_index(drop=True)

    # Merge hardcoded tags
    valid_iso3 = set(df["iso3"].dropna().astype(str).str.strip().str.upper().tolist())
    tags = tags_dataframe(valid_iso3)
    df = df.merge(tags, on="iso3", how="left")

    # Fill missing hardcoded columns with 0
    hard_cols = [c for c in tags.columns if c != "iso3"]
    for col in hard_cols:
        df[col] = df[col].fillna(0).astype("Int64")

    # ----------------------------------------------------------
    # Population density (computed from CSV): population / area_km2
    # Top/Bottom 20 flags (no hardcode)
    # ----------------------------------------------------------
    df["pop_density_per_km2"] = pd.NA
    df["top20_pop_density"] = 0
    df["bottom20_pop_density"] = 0

    if "population" in df.columns and "area_km2" in df.columns:
        dens = df[["iso3", "population", "area_km2"]].copy()
        dens = dens.dropna(subset=["population", "area_km2"])
        dens = dens[dens["area_km2"] > 0]
        if not dens.empty:
            dens["pop_density_per_km2"] = dens["population"] / dens["area_km2"]
            df = df.merge(dens[["iso3", "pop_density_per_km2"]], on="iso3", how="left", suffixes=("", "_tmp"))
            if "pop_density_per_km2_tmp" in df.columns:
                df["pop_density_per_km2"] = df["pop_density_per_km2_tmp"]
                df = df.drop(columns=["pop_density_per_km2_tmp"])

            dens_sorted = dens.sort_values("pop_density_per_km2", ascending=False)
            top20_iso3 = set(dens_sorted.head(20)["iso3"].tolist())
            bot20_iso3 = set(dens_sorted.tail(20)["iso3"].tolist())
            df.loc[df["iso3"].isin(top20_iso3), "top20_pop_density"] = 1
            df.loc[df["iso3"].isin(bot20_iso3), "bottom20_pop_density"] = 1

    df["top20_pop_density"] = df["top20_pop_density"].astype("Int64")
    df["bottom20_pop_density"] = df["bottom20_pop_density"].astype("Int64")
    df["pop_density_per_km2"] = pd.to_numeric(df["pop_density_per_km2"], errors="coerce")

    # Derive numeric flag_n_colors_approx from one-hot columns if present
    color_cols = [f"flag_n_colors_{i}" for i in range(1, 13)]
    if all(c in df.columns for c in color_cols):
        df["flag_n_colors_approx"] = pd.NA
        for i in range(1, 13):
            df.loc[df[f"flag_n_colors_{i}"] == 1, "flag_n_colors_approx"] = i
        df["flag_n_colors_approx"] = pd.to_numeric(df["flag_n_colors_approx"], errors="coerce")

    return df

df = load_data()
VALID_ISO3 = set(df["iso3"].dropna().astype(str).str.strip().str.upper().tolist())

# ==========================================================
# Sidebar helpers (QoL)
#   - FIX: widgets inside expanders must be created with the expander container
#   - FIX: dividers should not appear during search
# ==========================================================
st.sidebar.header("Filters")
filter_q = st.sidebar.text_input("Search filters (type to narrow sidebar)", "").strip().lower()

def matches(text: str) -> bool:
    return (not filter_q) or (filter_q in str(text).lower())

def section_visible(title: str, labels: list[str]) -> bool:
    if not filter_q:
        return True
    if matches(title):
        return True
    return any(matches(lbl) for lbl in labels)

def hard_filter(container, label, col_name, default="(ANY)"):
    # Search-aware: hide if not matching; keep previous/default value
    if not matches(label):
        return default
    if col_name not in df.columns:
        container.caption(f"{label}: (missing column)")
        return default
    return container.selectbox(label, ["(ANY)", "Yes", "No"], index=0)

# ==========================================================
# Sidebar: defaults so app is stable when widgets hidden
# ==========================================================
starts = ""
ends = ""
length = 0
contains = ""
region = "(ANY)"

landlocked = "(ANY)"
drive_side = "(ANY)"
is_island = "(ANY)"

top20_gdp = False
min_gdp = 0

use_size_filters = True
area_min = area_max = None
pop_min = pop_max = None
bmin = bmax = None

# Languages defaults
lang_mode = "No filter"
lang_selected = []

# River defaults
river_choice = "(No filter)"
river_systems_clean = {}

# Collapsible section defaults
f_eu = f_cw = f_ussr = f_mon = f_dep = f_nukes = f_ssm = f_ss_illegal = f_dst = "(ANY)"
f_top20_renew = "(ANY)"

f_cap_not_largest = f_f1 = f_never_medal = f_host_olym = f_host_wc = f_played_wc = f_won_wc = "(ANY)"
f_equator = f_sahara = f_steppe = f_wheat = f_oil = f_skyscrapers = "(ANY)"
f_alcohol_ban = f_top_alcohol = f_top_chocolate = f_top_rail = f_top_tourism = f_top_whs = f_top_lakes = "(ANY)"
f_top_density = f_bottom_density = "(ANY)"
f_tz = "(ANY)"
f_med = f_ind = f_pac = f_atl = f_nat = f_sat = f_car = f_blk = f_bal = f_ecs = f_scs = "(ANY)"
f_star = f_coa = f_anm = "(ANY)"
f_sun = f_coa = f_anm = "(ANY)"

# Flags colors defaults
color_mode = "(ANY)"
color_n = 3
f_only_rwb = "(ANY)"
f_no_rwb = "(ANY)"

# ==========================================================
# Sidebar: basics (search-aware)
# ==========================================================
if matches("Starts with (e.g. an)") or not filter_q:
    starts = st.sidebar.text_input("Starts with (e.g. an)", "")
if matches("Ends with (e.g. n)") or not filter_q:
    ends = st.sidebar.text_input("Ends with (e.g. n)", "")
if matches("Name length (letters only)") or matches("Name length") or not filter_q:
    length = st.sidebar.number_input("Name length (letters only)", min_value=0, max_value=30, value=0, step=1)
if matches("Contains (e.g. land)") or matches("Contains") or not filter_q:
    contains = st.sidebar.text_input("Contains (e.g. land)", "")
name_multiword = "(ANY)"
if matches("Name has multiple words") or matches("multiple words") or matches("multiword") or not filter_q:
    name_multiword = st.sidebar.selectbox("Name has multiple words", ["(ANY)", "Yes", "No"], index=0)


regions = ["(ANY)"]
if "region" in df.columns:
    regions += sorted([r for r in df["region"].dropna().unique().tolist()])
if matches("Region") or not filter_q:
    region = st.sidebar.selectbox("Region", regions)

if matches("Landlocked") or not filter_q:
    landlocked = st.sidebar.selectbox("Landlocked", ["(ANY)", "Yes", "No", "No data"])
if matches("Driving side") or not filter_q:
    drive_side = st.sidebar.selectbox("Driving side", ["(ANY)", "left", "right", "No data"])
if matches("Island (heuristic)") or matches("Island") or not filter_q:
    is_island = st.sidebar.selectbox("Island (heuristic)", ["(ANY)", "Yes", "No", "No data"])

if not filter_q:
    st.sidebar.divider()

if matches("Enable area/population/borders filters") or matches("Area") or matches("Population") or matches("borders") or not filter_q:
    use_size_filters = st.sidebar.checkbox("Enable area/population/borders filters", value=True)

if use_size_filters and "area_km2" in df.columns and df["area_km2"].notna().any():
    amax = float(df["area_km2"].max())
    if matches("Area (km²)") or matches("Area") or not filter_q:
        area_min, area_max = st.sidebar.slider(
            "Area (km²)",
            min_value=0.0,
            max_value=max(1.0, amax),
            value=(0.0, amax),
            step=100_000.0,
            format="%.0f",
        )

if use_size_filters and "population" in df.columns and df["population"].notna().any():
    pmax = float(df["population"].max())
    if matches("Population") or not filter_q:
        pop_min, pop_max = st.sidebar.slider(
            "Population",
            min_value=0.0,
            max_value=max(1.0, pmax),
            value=(0.0, pmax),
            step=100_000.0,
            format="%.0f",
        )

if use_size_filters and "borders_count" in df.columns and df["borders_count"].notna().any():
    b0 = int(df["borders_count"].min())
    b1 = int(df["borders_count"].max())
    if matches("Number of borders") or matches("borders") or not filter_q:
        bmin, bmax = st.sidebar.slider(
            "Number of borders",
            min_value=b0,
            max_value=b1,
            value=(b0, b1),
            step=1,
        )

if not filter_q:
    st.sidebar.divider()

# ==========================================================
# Languages (FIXED: use expander container)
# ==========================================================
all_langs = []
if "official_languages_rc" in df.columns:
    lang_set = set()
    for v in df["official_languages_rc"].fillna("").tolist():
        for lg in split_languages(str(v)):
            lang_set.add(lg)
    all_langs = sorted(lang_set)

_LANG_LABELS = ["Languages filter mode", "Official languages", "Languages"]
if section_visible("Languages", _LANG_LABELS):
    exp_lang = st.sidebar.expander("Languages", expanded=False)
    with exp_lang:
        if matches("Languages filter mode") or matches("Languages") or matches("language") or not filter_q:
            lang_mode = exp_lang.selectbox("Languages filter mode", ["No filter", "Any (OR)", "All (AND)"])
        if all_langs and lang_mode != "No filter":
            if matches("Official languages") or matches("languages") or matches("language") or not filter_q:
                lang_selected = exp_lang.multiselect("Official languages", all_langs, default=[])


# ==========================================================
# River systems (FIXED: use expander container)
# ==========================================================
river_options = ["(No filter)"]
river_systems_clean = {}
for sys_name, iso3s in RIVER_SYSTEMS_ISO3.items():
    cleaned = normalize_iso3_set(iso3s).intersection(VALID_ISO3)
    if cleaned:
        river_systems_clean[sys_name] = cleaned
        river_options.append(sys_name)

# ==========================================================
# Collapsible sections (expanders) — FIXED: pass container + use container widgets
# ==========================================================

_DENS_LABELS = ["Top 20 population density", "Bottom 20 population density", "Capital is not the most populated city",]
if section_visible("Population density", _DENS_LABELS):
    exp_pol = st.sidebar.expander("Population density", expanded=False)
    with exp_pol:
        f_cap_not_largest = hard_filter(exp_pol, "Capital is not the most populated city", "capital_not_largest_city", f_cap_not_largest)
        f_top_density = hard_filter(exp_pol, "Top 20 population density", "top20_pop_density", f_top_density)
        f_bottom_density = hard_filter(exp_pol, "Bottom 20 population density", "bottom20_pop_density", f_bottom_density)


#---------------------- Geography / production / skyline ----------------------
_GEO_LABELS = [
    "Touches the Equator",
    "Touches the Sahara Desert",
    "Touches the Eurasian Steppe",
    "Top 10 number of lakes",
    
]
if section_visible("Geography", _GEO_LABELS):
    exp_geo = st.sidebar.expander("Geography / production", expanded=False)
    with exp_geo:
        f_equator = hard_filter(exp_geo, "Touches the Equator", "touches_equator", f_equator)
        f_sahara = hard_filter(exp_geo, "Touches the Sahara Desert", "touches_sahara", f_sahara)
        f_steppe = hard_filter(exp_geo, "Touches the Eurasian Steppe", "touches_eurasian_steppe", f_steppe)
        f_top_lakes = hard_filter(exp_geo, "Top 10 number of lakes", "top10_number_of_lakes", f_top_lakes)
    
#---------------------- Coastlines/ Rivers ----------------------
_COAST_LABELS = [
    "Coastline: Mediterranean Sea",
    "Coastline: Indian Ocean",
    "Coastline: Pacific Ocean",
    "Coastline: Atlantic Ocean",
    "Coastline: North Atlantic (snapshot)",
    "Coastline: South Atlantic (snapshot)",
    "Coastline: Caribbean Sea",
    "Coastline: Black Sea",
    "Coastline: Baltic Sea",
    "Coastline: East China Sea",
    "Coastline: South China Sea",
]
if section_visible("Coastlines / Seas", _COAST_LABELS):
    exp_coast = st.sidebar.expander("Coastlines / Seas", expanded=False)
    with exp_coast:
        f_med = hard_filter(exp_coast, "Coastline: Mediterranean Sea", "coast_mediterranean", f_med)
        f_ind = hard_filter(exp_coast, "Coastline: Indian Ocean", "coast_indian_ocean", f_ind)
        f_pac = hard_filter(exp_coast, "Coastline: Pacific Ocean", "coast_pacific_ocean", f_pac)
        f_atl = hard_filter(exp_coast, "Coastline: Atlantic Ocean", "coast_atlantic_ocean", f_atl)
        f_nat = hard_filter(exp_coast, "Coastline: North Atlantic (snapshot)", "coast_north_atlantic", f_nat)
        f_sat = hard_filter(exp_coast, "Coastline: South Atlantic (snapshot)", "coast_south_atlantic", f_sat)
        f_car = hard_filter(exp_coast, "Coastline: Caribbean Sea", "coast_caribbean_sea", f_car)
        f_blk = hard_filter(exp_coast, "Coastline: Black Sea", "coast_black_sea", f_blk)
        f_bal = hard_filter(exp_coast, "Coastline: Baltic Sea", "coast_baltic_sea", f_bal)
        f_ecs = hard_filter(exp_coast, "Coastline: East China Sea", "coast_east_china_sea", f_ecs)
        f_scs = hard_filter(exp_coast, "Coastline: South China Sea", "coast_south_china_sea", f_scs)

_RIVER_LABELS = ["River system (basin touch)", "River system", "River", "basin"]
if section_visible("River systems", _RIVER_LABELS):
    exp_riv = st.sidebar.expander("River systems", expanded=False)
    with exp_riv:
        if matches("River system (basin touch)") or matches("River system") or matches("River") or matches("basin") or not filter_q:
            river_choice = exp_riv.selectbox("River system (basin touch)", river_options)


#-------------------- Political / historical categories --------------------    
_POL_LABELS = [
    "Member of the European Union",
    "Member of the Commonwealth",
    "Was part of the USSR",
    "Is a monarchy",
    "Is a dependency/territory",
    "Has nuclear weapons",
    "Same-sex marriage legalized",
    "Same-sex activities are illegal",
    "Observes Daylight Saving Time",
    "Top 20 domestic renewable energy share",
]
if section_visible("Political", _POL_LABELS):
    exp_pol = st.sidebar.expander("Political", expanded=False)
    with exp_pol:
        f_eu = hard_filter(exp_pol, "Member of the European Union", "is_eu_member", f_eu)
        f_cw = hard_filter(exp_pol, "Member of the Commonwealth", "is_commonwealth_member", f_cw)
        f_ussr = hard_filter(exp_pol, "Was part of the USSR", "was_part_of_ussr", f_ussr)
        f_mon = hard_filter(exp_pol, "Is a monarchy", "is_monarchy", f_mon)
        f_dep = hard_filter(exp_pol, "Is a dependency/territory", "is_dependency_or_territory", f_dep)
        f_nukes = hard_filter(exp_pol, "Has nuclear weapons", "has_nuclear_weapons", f_nukes)
        f_ssm = hard_filter(exp_pol, "Same-sex marriage legalized", "same_sex_marriage_legal", f_ssm)
        f_ss_illegal = hard_filter(exp_pol, "Same-sex activities are illegal", "same_sex_acts_illegal", f_ss_illegal)
        f_dst = hard_filter(exp_pol, "Observes Daylight Saving Time", "observes_dst", f_dst)

        if "top20_domestic_renewable_share" in df.columns and (matches("Top 20 domestic renewable energy share") or not filter_q):
            f_top20_renew = exp_pol.selectbox(
                "Top 20 domestic renewable energy share",
                ["(ANY)", "Yes", "No"],
                index=0
            )


#---------------------- Sports & events ----------------------
_SPORTS_LABELS = [
    "Has hosted a Formula 1 Grand Prix",
    "Has never won an Olympic medal",
    "Has hosted the Olympics",
    "Has hosted the Men's FIFA World Cup",
    "Has played in the Men's FIFA World Cup",
    "Has won the Men's FIFA World Cup",
]
if section_visible("Sports & events", _SPORTS_LABELS):
    exp_sports = st.sidebar.expander("Sports & events", expanded=False)
    with exp_sports:
        f_f1 = hard_filter(exp_sports, "Has hosted a Formula 1 Grand Prix", "hosted_f1_grand_prix", f_f1)
        f_never_medal = hard_filter(exp_sports, "Has never won an Olympic medal", "never_won_olympic_medal", f_never_medal)
        f_host_olym = hard_filter(exp_sports, "Has hosted the Olympics", "hosted_olympics", f_host_olym)
        f_host_wc = hard_filter(exp_sports, "Has hosted the Men's FIFA World Cup", "hosted_mens_fifa_world_cup", f_host_wc)
        f_played_wc = hard_filter(exp_sports, "Has played in the Men's FIFA World Cup", "played_mens_fifa_world_cup", f_played_wc)
        f_won_wc = hard_filter(exp_sports, "Has won the Men's FIFA World Cup", "won_mens_fifa_world_cup", f_won_wc)


#---------------------- Lifestyle / transport / tourism / production ----------------------
_LIFE_LABELS = [
    "Alcohol prohibition",
    "Top 20 alcohol consumption per capita",
    "Top 20 chocolate consumption",
    "Top 20 rail network size",
    "Top 20 tourist arrivals (2024)",
    "Top 20 UNESCO World Heritage sites",
    "Top 20 wheat production",
    "Top 20 oil production",
    "Has 50+ skyscrapers",
]
if section_visible("Economy", _LIFE_LABELS):
    exp_life = st.sidebar.expander("Economy", expanded=False)
    with exp_life:
        f_alcohol_ban = hard_filter(exp_life, "Alcohol prohibition", "alcohol_prohibition", f_alcohol_ban)
        f_top_alcohol = hard_filter(exp_life, "Top 20 alcohol consumption per capita", "top20_alcohol_consumption", f_top_alcohol)
        f_top_chocolate = hard_filter(exp_life, "Top 20 chocolate consumption", "top20_chocolate_consumption", f_top_chocolate)
        f_top_rail = hard_filter(exp_life, "Top 20 rail network size", "top20_rail_network_size", f_top_rail)
        f_top_tourism = hard_filter(exp_life, "Top 20 tourist arrivals (2024)", "top20_tourist_arrivals_2024", f_top_tourism)
        f_top_whs = hard_filter(exp_life, "Top 20 UNESCO World Heritage sites", "top20_world_heritage_sites", f_top_whs)
        f_wheat = hard_filter(exp_life, "Top 20 wheat production", "top20_wheat_production", f_wheat)
        f_oil = hard_filter(exp_life, "Top 20 oil production", "top20_oil_production", f_oil)
        f_skyscrapers = hard_filter(exp_life, "Has 50+ skyscrapers", "has_50plus_skyscrapers", f_skyscrapers)
        
        if matches("Top 20 GDP per capita") or matches("GDP") or not filter_q:
            top20_gdp = st.sidebar.checkbox("Top 20 GDP per capita", value=False)
        if matches("Min GDP per capita (USD)") or matches("Min GDP") or matches("GDP") or not filter_q:
            min_gdp = st.sidebar.number_input("Min GDP per capita (USD)", min_value=0, value=0, step=1000)


_TZ_LABELS = ["Has more than 1 time zone", "time zone"]
if section_visible("Time zones", _TZ_LABELS):
    exp_tz = st.sidebar.expander("Time zones", expanded=False)
    with exp_tz:
        if matches("Has more than 1 time zone") or matches("time zone") or not filter_q:
            f_tz = exp_tz.selectbox("Has more than 1 time zone", ["(ANY)", "Yes", "No", "No data"])


#----------------------- Flags ------------------------------------
_FLAG_LABELS = ["Flag: has a star", "Flag: has a coat of arms", "Flag: has an animal", "Flag colors: filter mode", "N colors", "Flag uses ONLY red/white/blue",
    "Flag WITHOUT red/white/blue", "colors",]
if section_visible("Flags", _FLAG_LABELS):
    exp_flag = st.sidebar.expander("Flags", expanded=False)
    with exp_flag:
        f_star = hard_filter(exp_flag, "Flag: has a star", "flag_has_star", f_star)
        f_sun = hard_filter(exp_flag, "Flag: has a sun", "flag_has_sun", f_sun)
        f_coa  = hard_filter(exp_flag, "Flag: has a coat of arms", "flag_has_coat_of_arms", f_coa)
        f_anm  = hard_filter(exp_flag, "Flag: has an animal", "flag_has_animal", f_anm)
        if matches("Flag colors: filter mode") or matches("colors") or not filter_q:
            color_mode = exp_flag.selectbox(
                "Flag colors: filter mode",
                ["(ANY)", "Exactly", "At most", "At least"],
                index=0
            )

        if matches("N colors") or matches("colors") or not filter_q:
            color_n = exp_flag.number_input("N colors", min_value=1, max_value=12, value=3, step=1)

        f_only_rwb = hard_filter(exp_flag, "Flag uses ONLY red/white/blue", "flag_only_red_white_blue", f_only_rwb)
        f_no_rwb = hard_filter(exp_flag, "Flag WITHOUT red/white/blue", "flag_without_red_white_blue", f_no_rwb)



# ==========================================================
# Apply filters
# ==========================================================
x = df.copy()

x = apply_name_filters(
    df,
    starts=starts if str(starts).strip() else None,
    ends=ends if str(ends).strip() else None,
    length=int(length) if int(length) > 0 else None,
    contains=contains if str(contains).strip() else None,
    multiword=name_multiword,
)


if "region" in x.columns and region != "(ANY)":
    x = x[x["region"] == region]

if use_size_filters and area_min is not None and "area_km2" in x.columns:
    x = x[x["area_km2"].fillna(-1).between(area_min, area_max)]

if use_size_filters and pop_min is not None and "population" in x.columns:
    x = x[x["population"].fillna(-1).between(pop_min, pop_max)]

if use_size_filters and bmin is not None and "borders_count" in x.columns:
    x = x[x["borders_count"].fillna(-1).between(bmin, bmax)]

if min_gdp and "gdp_pc_usd" in x.columns:
    x = x[(x["gdp_pc_usd"].fillna(0)) >= float(min_gdp)]

if "landlocked_01" in x.columns and landlocked != "(ANY)":
    x = x.loc[filter_01(x["landlocked_01"], landlocked)]

if "driving_side_raw" in x.columns and drive_side != "(ANY)":
    if drive_side == "No data":
        x = x[x["driving_side_raw"].isna()]
    else:
        x = x[x["driving_side_raw"] == drive_side]

if "is_island_heuristic" in x.columns and is_island != "(ANY)":
    x = x.loc[filter_01(x["is_island_heuristic"], is_island)]

if top20_gdp and "top20_gdp_pc" in x.columns:
    x = x[x["top20_gdp_pc"] == 1]

# Languages filter
if lang_mode != "No filter" and lang_selected and "official_languages_rc" in x.columns:
    if lang_mode == "Any (OR)":
        mask = pd.Series(False, index=x.index)
        for lg in lang_selected:
            mask = mask | x["official_languages_rc"].str.contains(lg, case=False, na=False, regex=False)
        x = x[mask]
    else:  # All (AND)
        for lg in lang_selected:
            x = x[x["official_languages_rc"].str.contains(lg, case=False, na=False, regex=False)]

# River system filter (direct)
if river_choice != "(No filter)":
    allowed = river_systems_clean.get(river_choice, set())
    x = x[x["iso3"].isin(allowed)]

# Political
x = apply_yesno_filter(x, "is_eu_member", f_eu)
x = apply_yesno_filter(x, "is_commonwealth_member", f_cw)
x = apply_yesno_filter(x, "was_part_of_ussr", f_ussr)
x = apply_yesno_filter(x, "is_monarchy", f_mon)
x = apply_yesno_filter(x, "is_dependency_or_territory", f_dep)
x = apply_yesno_filter(x, "has_nuclear_weapons", f_nukes)
x = apply_yesno_filter(x, "same_sex_marriage_legal", f_ssm)
x = apply_yesno_filter(x, "same_sex_acts_illegal", f_ss_illegal)
x = apply_yesno_filter(x, "observes_dst", f_dst)

if "top20_domestic_renewable_share" in x.columns and f_top20_renew != "(ANY)":
    want = 1 if f_top20_renew == "Yes" else 0
    x = x[x["top20_domestic_renewable_share"] == want]

# Sports/events
x = apply_yesno_filter(x, "capital_not_largest_city", f_cap_not_largest)
x = apply_yesno_filter(x, "hosted_f1_grand_prix", f_f1)
x = apply_yesno_filter(x, "never_won_olympic_medal", f_never_medal)
x = apply_yesno_filter(x, "hosted_olympics", f_host_olym)
x = apply_yesno_filter(x, "hosted_mens_fifa_world_cup", f_host_wc)
x = apply_yesno_filter(x, "played_mens_fifa_world_cup", f_played_wc)
x = apply_yesno_filter(x, "won_mens_fifa_world_cup", f_won_wc)

# Geography/production/skyscrapers
x = apply_yesno_filter(x, "touches_equator", f_equator)
x = apply_yesno_filter(x, "touches_sahara", f_sahara)
x = apply_yesno_filter(x, "touches_eurasian_steppe", f_steppe)
x = apply_yesno_filter(x, "top20_wheat_production", f_wheat)
x = apply_yesno_filter(x, "top20_oil_production", f_oil)
x = apply_yesno_filter(x, "has_50plus_skyscrapers", f_skyscrapers)

# Lifestyle/transport/tourism
x = apply_yesno_filter(x, "alcohol_prohibition", f_alcohol_ban)
x = apply_yesno_filter(x, "top20_alcohol_consumption", f_top_alcohol)
x = apply_yesno_filter(x, "top20_chocolate_consumption", f_top_chocolate)
x = apply_yesno_filter(x, "top20_rail_network_size", f_top_rail)
x = apply_yesno_filter(x, "top20_tourist_arrivals_2024", f_top_tourism)
x = apply_yesno_filter(x, "top20_world_heritage_sites", f_top_whs)
x = apply_yesno_filter(x, "top10_number_of_lakes", f_top_lakes)

# Density
x = apply_yesno_filter(x, "top20_pop_density", f_top_density)
x = apply_yesno_filter(x, "bottom20_pop_density", f_bottom_density)

# Time zones
if "has_more_than_1_time_zone" in x.columns and f_tz != "(ANY)":
    if f_tz == "Yes":
        x = x[x["has_more_than_1_time_zone"] == 1]
    elif f_tz == "No":
        x = x[x["has_more_than_1_time_zone"] == 0]
    else:
        x = x[x["has_more_than_1_time_zone"].isna()]

# Coastlines
x = apply_yesno_filter(x, "coast_mediterranean", f_med)
x = apply_yesno_filter(x, "coast_indian_ocean", f_ind)
x = apply_yesno_filter(x, "coast_pacific_ocean", f_pac)
x = apply_yesno_filter(x, "coast_atlantic_ocean", f_atl)
x = apply_yesno_filter(x, "coast_north_atlantic", f_nat)
x = apply_yesno_filter(x, "coast_south_atlantic", f_sat)
x = apply_yesno_filter(x, "coast_caribbean_sea", f_car)
x = apply_yesno_filter(x, "coast_black_sea", f_blk)
x = apply_yesno_filter(x, "coast_baltic_sea", f_bal)
x = apply_yesno_filter(x, "coast_east_china_sea", f_ecs)
x = apply_yesno_filter(x, "coast_south_china_sea", f_scs)

# Flags (hardcoded)
x = apply_yesno_filter(x, "flag_has_star", f_star)
x = apply_yesno_filter(x, "flag_has_sun", f_sun)
x = apply_yesno_filter(x, "flag_has_coat_of_arms", f_coa)
x = apply_yesno_filter(x, "flag_has_animal", f_anm)

# Flags (colors — hardcoded)
x = apply_yesno_filter(x, "flag_only_red_white_blue", f_only_rwb)
x = apply_yesno_filter(x, "flag_without_red_white_blue", f_no_rwb)

if color_mode != "(ANY)" and "flag_n_colors_approx" in x.columns:
    x = x.dropna(subset=["flag_n_colors_approx"])
    if color_mode == "Exactly":
        x = x[x["flag_n_colors_approx"] == int(color_n)]
    elif color_mode == "At most":
        x = x[x["flag_n_colors_approx"] <= int(color_n)]
    elif color_mode == "At least":
        x = x[x["flag_n_colors_approx"] >= int(color_n)]

st.subheader(f"Results: {len(x)} countries match your filters")

# ==========================================================
# Map
# ==========================================================
selected_iso3 = set(x["iso3"].dropna().astype(str).str.strip().str.upper().tolist())
if len(x) == len(df):
    selected_iso3 = set(df["iso3"].dropna().astype(str).str.strip().str.upper().tolist())

hover_cols = [c for c in [
    "capital", "region", "subregion", "area_km2", "population", "borders_count",
    "official_languages_rc", "gdp_pc_usd",
] if c in df.columns]

base = df[["iso3", "name"] + hover_cols].copy()
base["selected_label"] = base["iso3"].astype(str).str.strip().str.upper().apply(
    lambda z: "Yes" if z in selected_iso3 else "No"
)

fig = px.choropleth(
    base,
    locations="iso3",
    color="selected_label",
    hover_name="name",
    hover_data={c: True for c in hover_cols},
    category_orders={"selected_label": ["No", "Yes"]},
    color_discrete_map={"No": "#ffffff", "Yes": "#77b7ff"},
)

fig.update_traces(marker_line_width=1.2, marker_line_color="#000000")
fig.update_geos(
    showcoastlines=False,
    showland=True,
    landcolor="#ffffff",
    showcountries=True,
    countrycolor="#000000",
    showframe=False,
    bgcolor="#0b0f14",
)
fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# Table + flag
# ==========================================================
st.subheader("Countries matching filters")

cols = [
    "name", "iso3", "region", "subregion",
    "area_km2", "population", "pop_density_per_km2", "top20_pop_density", "bottom20_pop_density",
    "borders_count", "driving_side_raw", "landlocked_01",
    "timezones_count","has_more_than_1_time_zone",
    "gdp_pc_usd", "homicides_per_100k",
    "official_languages_rc",
    "top20_domestic_renewable_share",
    "is_eu_member","is_commonwealth_member","was_part_of_ussr",
    "is_monarchy","is_dependency_or_territory","has_nuclear_weapons",
    "same_sex_marriage_legal","same_sex_acts_illegal","observes_dst",
    "capital_not_largest_city","hosted_f1_grand_prix","never_won_olympic_medal",
    "hosted_olympics","hosted_mens_fifa_world_cup","played_mens_fifa_world_cup","won_mens_fifa_world_cup",
    "touches_equator","touches_sahara","touches_eurasian_steppe",
    "top20_wheat_production","top20_oil_production","has_50plus_skyscrapers",
    "alcohol_prohibition","top20_alcohol_consumption","top20_chocolate_consumption",
    "top20_rail_network_size","top20_tourist_arrivals_2024","top20_world_heritage_sites",
    "top10_number_of_lakes",
    "flag_png",
    "coast_mediterranean","coast_indian_ocean","coast_pacific_ocean","coast_atlantic_ocean",
    "coast_north_atlantic","coast_south_atlantic","coast_caribbean_sea",
    "coast_black_sea","coast_baltic_sea","coast_east_china_sea","coast_south_china_sea",
    "flag_has_star","flag_has_sun","flag_has_coat_of_arms","flag_has_animal",
    "flag_n_colors_approx","flag_only_red_white_blue","flag_without_red_white_blue",
]
cols = [c for c in cols if c in x.columns]
st.dataframe(x[cols], use_container_width=True, height=380)

st.subheader("Flag selector")
names = x["name"].dropna().tolist()
sel = st.selectbox("Select a country", ["(NONE)"] + names)

if sel != "(NONE)":
    row = x[x["name"] == sel].iloc[0]
    st.write(f"**{row['name']} ({row['iso3']})**")
    if pd.notna(row.get("flag_png")) and str(row.get("flag_png")).startswith("http"):
        st.image(str(row["flag_png"]), width=240)
    else:
        st.info("No flag image available for this country.")

st.caption(
    "GeoGrid Helper: RESTCountries + World Bank + hardcoded categories (no Wikidata). "
    "River systems are filter-only snapshots. Population density Top/Bottom 20 is computed from your CSV."
)

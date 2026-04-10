# validate_dataset.py
import pandas as pd

CSV_PATH = "countries_master.csv"


def pct_na(s: pd.Series) -> float:
    return float(s.isna().mean() * 100.0)


def main():
    df = pd.read_csv(CSV_PATH)

    print("\n=== BASIC INFO ===")
    print("rows:", len(df), "cols:", len(df.columns))
    print("columns:", ", ".join(df.columns))

    # % NA por columna
    na_report = (
        pd.DataFrame({
            "na_%": df.apply(pct_na),
            "dtype": df.dtypes.astype(str)
        })
        .sort_values("na_%", ascending=False)
    )

    print("\n=== NA% BY COLUMN (top 25) ===")
    print(na_report.head(25).to_string())

    # columnas boolean 0/1/NA esperadas (si existen)
    expected_bool01 = [
        "landlocked_01", "drives_left", "has_coast", "is_island_heuristic",
        "produces_nuclear_power", "top20_gdp_pc", "top20_domestic_renewable_share"
    ]
    print("\n=== BOOL 0/1/NA CHECK ===")
    for c in expected_bool01:
        if c not in df.columns:
            continue
        s = pd.to_numeric(df[c], errors="coerce")
        vals = sorted(set(s.dropna().astype(int).unique().tolist()))
        bad = [v for v in vals if v not in (0, 1)]
        print(f"- {c}: values={vals}  bad={bad}  NA%={pct_na(s):.1f}%")

    # coherencias básicas
    print("\n=== COHERENCE CHECKS ===")

    def show_problem(mask, title, cols=None, n=10):
        if mask.sum() == 0:
            print(f"- OK: {title}")
            return
        print(f"- PROBLEM: {title} -> {int(mask.sum())} rows")
        view_cols = cols or ["name", "iso3"]
        view_cols = [c for c in view_cols if c in df.columns]
        print(df.loc[mask, view_cols].head(n).to_string(index=False))

    if "landlocked_01" in df.columns and "has_coast" in df.columns:
        ll = pd.to_numeric(df["landlocked_01"], errors="coerce")
        coast = pd.to_numeric(df["has_coast"], errors="coerce")
        mask = (ll == 1) & (coast == 1)
        show_problem(mask, "landlocked_01==1 AND has_coast==1 (imposible)", cols=["name","iso3","landlocked_01","has_coast"])

        mask = (ll == 0) & (coast == 0)
        show_problem(mask, "landlocked_01==0 AND has_coast==0 (imposible)", cols=["name","iso3","landlocked_01","has_coast"])

    if "flag_png" in df.columns:
        mask = df["flag_png"].notna() & ~df["flag_png"].astype(str).str.startswith("http")
        show_problem(mask, "flag_png no parece URL http", cols=["name","iso3","flag_png"])

    # sanity: ejemplo de columnas clave
    print("\n=== SAMPLE ROWS (key cols) ===")
    key_cols = ["name","iso3","landlocked_raw","landlocked_01","driving_side_raw","drives_left","flag_png","official_languages_rc","gdp_pc_usd","rail_km_route"]
    key_cols = [c for c in key_cols if c in df.columns]
    print(df[key_cols].head(12).to_string(index=False))

    print("\nDONE.")


if __name__ == "__main__":
    main()

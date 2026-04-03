from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABLES_DIR = PROJECT_ROOT / "results" / "tables"

UNAPS_FILE = PROCESSED_DIR / "unaps_clean.csv"
SUBCOHORT_FILE = TABLES_DIR / "linked_subcohort_preview.csv"


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    if not UNAPS_FILE.exists():
        raise FileNotFoundError(f"Missing file: {UNAPS_FILE}")

    if not SUBCOHORT_FILE.exists():
        raise FileNotFoundError(f"Missing file: {SUBCOHORT_FILE}")

    unaps = pd.read_csv(UNAPS_FILE)
    subcohort = pd.read_csv(SUBCOHORT_FILE)

    # =====================
    # QUALITY CONTROL FOR SUBCOHORT
    # =====================
    required_sub_cols = ["edad_clinical", "edad_social"]
    for col in required_sub_cols:
        if col not in subcohort.columns:
            raise KeyError(f"Column '{col}' not found in linked subcohort file.")

    subcohort["age_diff"] = subcohort["edad_clinical"] - subcohort["edad_social"]
    subcohort["age_inconsistent_flag"] = subcohort["age_diff"].abs() > 5

    subcohort.to_csv(TABLES_DIR / "subcohort_with_quality_flags.csv", index=False)

    qc_summary = {
        "total_subcohort": len(subcohort),
        "inconsistent_age_n": int(subcohort["age_inconsistent_flag"].sum()),
        "inconsistent_age_pct": float(subcohort["age_inconsistent_flag"].mean() * 100)
    }
    pd.DataFrame([qc_summary]).to_csv(
        TABLES_DIR / "subcohort_quality_summary.csv",
        index=False
    )

    sub_clean = subcohort.loc[~subcohort["age_inconsistent_flag"]].copy()

    # =====================
    # MAIN CLINICAL COHORT SUMMARY
    # =====================
    required_unaps_cols = ["edad", "sexo", "localidad", "hta", "diabetes_mellitus", "anemia"]
    for col in required_unaps_cols:
        if col not in unaps.columns:
            raise KeyError(f"Column '{col}' not found in UNAPS cleaned dataset.")

    clinical_summary = {
        "total_patients": len(unaps),
        "mean_age": float(unaps["edad"].mean()),
        "female_pct": float((unaps["sexo"] == "female").mean() * 100),
        "hta_prevalence": float(pd.to_numeric(unaps["hta"], errors="coerce").mean() * 100),
        "dm_prevalence": float(pd.to_numeric(unaps["diabetes_mellitus"], errors="coerce").mean() * 100),
        "anemia_prevalence": float(pd.to_numeric(unaps["anemia"], errors="coerce").mean() * 100)
    }
    pd.DataFrame([clinical_summary]).to_csv(
        TABLES_DIR / "clinical_summary.csv",
        index=False
    )

    # =====================
    # DISTRIBUTIONS
    # =====================
    if "erc_calsificacion" in unaps.columns:
        (
            unaps["erc_calsificacion"]
            .value_counts(dropna=False)
            .rename_axis("erc_calsificacion")
            .reset_index(name="count")
            .to_csv(TABLES_DIR / "ckd_distribution.csv", index=False)
        )

    (
        unaps["sexo"]
        .value_counts(dropna=False)
        .rename_axis("sexo")
        .reset_index(name="count")
        .to_csv(TABLES_DIR / "sex_distribution.csv", index=False)
    )

    (
        unaps["localidad"]
        .value_counts(dropna=False)
        .rename_axis("localidad")
        .reset_index(name="count")
        .to_csv(TABLES_DIR / "locality_distribution.csv", index=False)
    )

    # =====================
    # CLEAN SUBCOHORT SUMMARY
    # =====================
    sub_summary = {"subcohort_clean_n": len(sub_clean)}

    if "acceso_a_seguro_medico_de_salud" in sub_clean.columns:
        sub_summary["insurance_access_pct"] = float(
            pd.to_numeric(sub_clean["acceso_a_seguro_medico_de_salud"], errors="coerce").mean() * 100
        )

    if "barreras_economicas" in sub_clean.columns:
        sub_summary["economic_barriers_pct"] = float(
            pd.to_numeric(sub_clean["barreras_economicas"], errors="coerce").mean() * 100
        )

    if "consultas_de_nefrologia_en_el_ultimo_ano" in sub_clean.columns:
        sub_summary["nephrology_visits_mean"] = float(
            pd.to_numeric(sub_clean["consultas_de_nefrologia_en_el_ultimo_ano"], errors="coerce").mean()
        )

    pd.DataFrame([sub_summary]).to_csv(
        TABLES_DIR / "subcohort_summary_clean.csv",
        index=False
    )

    print("Analysis completed with quality control.")
    print(f"Clinical summary saved to: {TABLES_DIR / 'clinical_summary.csv'}")
    print(f"Subcohort QC summary saved to: {TABLES_DIR / 'subcohort_quality_summary.csv'}")
    print(f"Clean subcohort summary saved to: {TABLES_DIR / 'subcohort_summary_clean.csv'}")
    print(f"CKD distribution saved to: {TABLES_DIR / 'ckd_distribution.csv'}")
    print(f"Sex distribution saved to: {TABLES_DIR / 'sex_distribution.csv'}")
    print(f"Locality distribution saved to: {TABLES_DIR / 'locality_distribution.csv'}")


if __name__ == "__main__":
    main()
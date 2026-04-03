from pathlib import Path
import pandas as pd
import re


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABLES_DIR = PROJECT_ROOT / "results" / "tables"
REPORTS_DIR = PROJECT_ROOT / "results" / "reports"

UNAPS_CLEAN = PROCESSED_DIR / "unaps_clean_v2.csv"
SOCIO_CLEAN = PROCESSED_DIR / "socio_clean_v2.csv"


def extract_numeric_id(value):
    if pd.isna(value):
        return pd.NA
    text = str(value).strip().lower()
    match = re.search(r"(\d+)", text)
    if match:
        return int(match.group(1))
    return pd.NA


def write_subcohort_report(summary: dict, matched_df: pd.DataFrame) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / "subcohort_build_report.txt"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("PERAVIA CKD EPIDEMIOLOGY - SUBCOHORT BUILD REPORT\n")
        f.write("=" * 60 + "\n\n")

        f.write("1. ID PATTERN SUMMARY\n")
        f.write("-" * 60 + "\n")
        for key, value in summary.items():
            f.write(f"{key}: {value}\n")

        f.write("\n2. PRELIMINARY MATCH RESULTS\n")
        f.write("-" * 60 + "\n")
        f.write(f"Matched rows: {len(matched_df)}\n")

        if len(matched_df) > 0:
            preview_cols = [
                col for col in [
                    "id",
                    "unaps_numeric_id",
                    "paciente_id",
                    "localidad_clinical",
                    "localidad_social",
                    "edad_clinical",
                    "edad_social"
                ] if col in matched_df.columns
            ]
            f.write("\nPreview of matched records:\n")
            f.write(matched_df[preview_cols].head(10).to_string(index=False))
            f.write("\n")


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    unaps_df = pd.read_csv(UNAPS_CLEAN)
    socio_df = pd.read_csv(SOCIO_CLEAN)

    if "id" not in unaps_df.columns:
        raise KeyError("Column 'id' not found in UNAPS cleaned dataset.")

    if "paciente_id" not in socio_df.columns:
        raise KeyError("Column 'paciente_id' not found in sociodemographic cleaned dataset.")

    unaps_df["unaps_numeric_id"] = unaps_df["id"].apply(extract_numeric_id)
    socio_df["paciente_id"] = pd.to_numeric(socio_df["paciente_id"], errors="coerce")

    matched_df = unaps_df.merge(
        socio_df,
        left_on="unaps_numeric_id",
        right_on="paciente_id",
        how="inner",
        suffixes=("_clinical", "_social")
    )

    summary = {
        "unaps_total_rows": len(unaps_df),
        "socio_total_rows": len(socio_df),
        "unaps_numeric_id_non_null": int(unaps_df["unaps_numeric_id"].notna().sum()),
        "unaps_numeric_id_unique": int(unaps_df["unaps_numeric_id"].nunique(dropna=True)),
        "socio_paciente_id_non_null": int(socio_df["paciente_id"].notna().sum()),
        "socio_paciente_id_unique": int(socio_df["paciente_id"].nunique(dropna=True)),
        "matched_rows": len(matched_df)
    }

    matched_df.to_csv(TABLES_DIR / "linked_subcohort_preview.csv", index=False)
    pd.DataFrame([summary]).to_csv(TABLES_DIR / "subcohort_id_summary.csv", index=False)
    write_subcohort_report(summary, matched_df)

    print("Subcohort build step completed.")
    print(f"Matched rows: {len(matched_df)}")
    print(f"Linked preview saved to: {TABLES_DIR / 'linked_subcohort_preview.csv'}")
    print(f"ID summary saved to: {TABLES_DIR / 'subcohort_id_summary.csv'}")
    print(f"Report saved to: {REPORTS_DIR / 'subcohort_build_report.txt'}")


if __name__ == "__main__":
    main()
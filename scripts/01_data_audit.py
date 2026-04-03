from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
REPORTS_DIR = PROJECT_ROOT / "results" / "reports"
TABLES_DIR = PROJECT_ROOT / "results" / "tables"

UNAPS_FILE = RAW_DIR / "DATASET_CONSULTA_UNAPS_PERAVIA_2024.xlsx"
SOCIO_FILE = RAW_DIR / "MATRIZ_SOCIODEMOGRAFICA_ERC_PERAVIA_2024.xlsx"


def safe_sheet_names(excel_path: Path) -> list[str]:
    """Return sheet names from an Excel file."""
    xls = pd.ExcelFile(excel_path)
    return xls.sheet_names


def read_first_sheet(excel_path: Path) -> pd.DataFrame:
    """Read the first sheet of an Excel file as DataFrame."""
    xls = pd.ExcelFile(excel_path)
    first_sheet = xls.sheet_names[0]
    df = pd.read_excel(excel_path, sheet_name=first_sheet)
    return df


def clean_column_preview(columns: list) -> list[str]:
    """Convert columns to readable strings for reporting."""
    return [str(col).strip() for col in columns]


def build_dataset_summary(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    """Generate column-level audit summary for a dataset."""
    summary = pd.DataFrame({
        "dataset": dataset_name,
        "column_name": [str(col) for col in df.columns],
        "dtype": [str(dtype) for dtype in df.dtypes],
        "non_null_count": df.notna().sum().values,
        "null_count": df.isna().sum().values,
        "n_unique": df.nunique(dropna=True).values,
    })

    summary["sample_values"] = [
        "; ".join(map(str, df[col].dropna().astype(str).head(5).tolist()))
        for col in df.columns
    ]

    return summary


def standardize_for_id_check(series: pd.Series) -> pd.Series:
    """Standardize ID-like fields for exploratory overlap checks."""
    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "", regex=False)
    )


def exploratory_id_overlap(unaps_df: pd.DataFrame, socio_df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform a basic exploratory overlap check between likely ID columns.
    This is only exploratory, not a final merge decision.
    """
    possible_results = []

    unaps_candidates = [col for col in unaps_df.columns if "id" in str(col).lower()]
    socio_candidates = [col for col in socio_df.columns if "id" in str(col).lower()]

    for ucol in unaps_candidates:
        for scol in socio_candidates:
            uvals = set(standardize_for_id_check(unaps_df[ucol].dropna()))
            svals = set(standardize_for_id_check(socio_df[scol].dropna()))
            overlap = len(uvals.intersection(svals))

            possible_results.append({
                "unaps_id_column": ucol,
                "socio_id_column": scol,
                "unaps_unique_ids": len(uvals),
                "socio_unique_ids": len(svals),
                "exact_overlap_count": overlap
            })

    if possible_results:
        return pd.DataFrame(possible_results).sort_values(
            by="exact_overlap_count", ascending=False
        )

    return pd.DataFrame(columns=[
        "unaps_id_column",
        "socio_id_column",
        "unaps_unique_ids",
        "socio_unique_ids",
        "exact_overlap_count"
    ])


def write_text_report(
    unaps_df: pd.DataFrame,
    socio_df: pd.DataFrame,
    unaps_sheets: list[str],
    socio_sheets: list[str],
    id_overlap_df: pd.DataFrame
) -> None:
    """Write a human-readable audit report."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    report_path = REPORTS_DIR / "data_audit_report.txt"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("PERAVIA CKD EPIDEMIOLOGY - DATA AUDIT REPORT\n")
        f.write("=" * 60 + "\n\n")

        f.write("1. FILE OVERVIEW\n")
        f.write("-" * 60 + "\n")
        f.write(f"UNAPS file: {UNAPS_FILE.name}\n")
        f.write(f"Sociodemographic file: {SOCIO_FILE.name}\n\n")

        f.write("2. SHEETS DETECTED\n")
        f.write("-" * 60 + "\n")
        f.write(f"UNAPS sheets: {', '.join(unaps_sheets)}\n")
        f.write(f"Sociodemographic sheets: {', '.join(socio_sheets)}\n\n")

        f.write("3. DATASET SHAPES\n")
        f.write("-" * 60 + "\n")
        f.write(f"UNAPS shape: {unaps_df.shape[0]} rows x {unaps_df.shape[1]} columns\n")
        f.write(f"Sociodemographic shape: {socio_df.shape[0]} rows x {socio_df.shape[1]} columns\n\n")

        f.write("4. COLUMN PREVIEW\n")
        f.write("-" * 60 + "\n")
        f.write("UNAPS columns:\n")
        for col in clean_column_preview(unaps_df.columns.tolist()):
            f.write(f"  - {col}\n")

        f.write("\nSociodemographic columns:\n")
        for col in clean_column_preview(socio_df.columns.tolist()):
            f.write(f"  - {col}\n")

        f.write("\n5. PRELIMINARY ID OVERLAP CHECK\n")
        f.write("-" * 60 + "\n")
        if id_overlap_df.empty:
            f.write("No obvious ID columns detected for overlap assessment.\n")
        else:
            f.write(id_overlap_df.to_string(index=False))
            f.write("\n")

        f.write("\n6. INITIAL NOTES\n")
        f.write("-" * 60 + "\n")
        f.write(
            "This report is exploratory only. No merge decisions should be made until "
            "IDs, column names, categories, and data quality issues are cleaned.\n"
        )


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    if not UNAPS_FILE.exists():
        raise FileNotFoundError(f"Missing file: {UNAPS_FILE}")

    if not SOCIO_FILE.exists():
        raise FileNotFoundError(f"Missing file: {SOCIO_FILE}")

    unaps_sheets = safe_sheet_names(UNAPS_FILE)
    socio_sheets = safe_sheet_names(SOCIO_FILE)

    unaps_df = read_first_sheet(UNAPS_FILE)
    socio_df = read_first_sheet(SOCIO_FILE)

    unaps_summary = build_dataset_summary(unaps_df, "UNAPS")
    socio_summary = build_dataset_summary(socio_df, "SOCIODEMOGRAPHIC")

    full_summary = pd.concat([unaps_summary, socio_summary], ignore_index=True)
    full_summary.to_csv(TABLES_DIR / "data_audit_summary.csv", index=False)

    id_overlap_df = exploratory_id_overlap(unaps_df, socio_df)
    id_overlap_df.to_csv(TABLES_DIR / "id_overlap_check.csv", index=False)

    write_text_report(
        unaps_df=unaps_df,
        socio_df=socio_df,
        unaps_sheets=unaps_sheets,
        socio_sheets=socio_sheets,
        id_overlap_df=id_overlap_df
    )

    print("Data audit completed successfully.")
    print(f"Audit summary saved to: {TABLES_DIR / 'data_audit_summary.csv'}")
    print(f"ID overlap check saved to: {TABLES_DIR / 'id_overlap_check.csv'}")
    print(f"Text report saved to: {REPORTS_DIR / 'data_audit_report.txt'}")


if __name__ == "__main__":
    main()
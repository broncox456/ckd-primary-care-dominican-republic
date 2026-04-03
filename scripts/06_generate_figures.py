from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABLES_DIR = PROJECT_ROOT / "results" / "tables"
FIGURES_DIR = PROJECT_ROOT / "results" / "figures"

UNAPS_FILE = PROCESSED_DIR / "unaps_clean.csv"
SUBCOHORT_QC_FILE = TABLES_DIR / "subcohort_with_quality_flags.csv"


def save_barplot(series, title, xlabel, ylabel, output_path, rotation=0):
    plt.figure(figsize=(10, 6))
    series.plot(kind="bar")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=rotation, ha="right" if rotation else "center")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def save_histogram(data, title, xlabel, ylabel, output_path, bins=15):
    plt.figure(figsize=(10, 6))
    plt.hist(data.dropna(), bins=bins)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def main():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    unaps = pd.read_csv(UNAPS_FILE)
    subcohort = pd.read_csv(SUBCOHORT_QC_FILE)

    sub_clean = subcohort[~subcohort["age_inconsistent_flag"]].copy()

    # 1. Age distribution
    if "edad" in unaps.columns:
        save_histogram(
            data=unaps["edad"],
            title="Age Distribution in Main Clinical Cohort",
            xlabel="Age (years)",
            ylabel="Frequency",
            output_path=FIGURES_DIR / "age_distribution_main_cohort.png",
            bins=15
        )

    # 2. Sex distribution
    if "sexo" in unaps.columns:
        sex_counts = unaps["sexo"].value_counts(dropna=False)
        save_barplot(
            series=sex_counts,
            title="Sex Distribution in Main Clinical Cohort",
            xlabel="Sex",
            ylabel="Number of patients",
            output_path=FIGURES_DIR / "sex_distribution_main_cohort.png"
        )

    # 3. CKD classification distribution
    if "erc_calsificacion" in unaps.columns:
        ckd_counts = unaps["erc_calsificacion"].value_counts(dropna=False)
        save_barplot(
            series=ckd_counts,
            title="CKD Classification Distribution",
            xlabel="CKD classification",
            ylabel="Number of patients",
            output_path=FIGURES_DIR / "ckd_classification_distribution.png",
            rotation=45
        )

    # 4. Top localities
    if "localidad" in unaps.columns:
        locality_counts = unaps["localidad"].value_counts(dropna=False).head(10)
        save_barplot(
            series=locality_counts,
            title="Top 10 Localities in Main Clinical Cohort",
            xlabel="Locality",
            ylabel="Number of patients",
            output_path=FIGURES_DIR / "top_localities_main_cohort.png",
            rotation=45
        )

    # 5. Hypertension prevalence
    if "hta" in unaps.columns:
        hta_counts = unaps["hta"].value_counts(dropna=False).sort_index()
        save_barplot(
            series=hta_counts,
            title="Hypertension Status in Main Clinical Cohort",
            xlabel="HTA",
            ylabel="Number of patients",
            output_path=FIGURES_DIR / "hypertension_status_main_cohort.png"
        )

    # 6. Diabetes prevalence
    if "diabetes_mellitus" in unaps.columns:
        dm_counts = unaps["diabetes_mellitus"].value_counts(dropna=False).sort_index()
        save_barplot(
            series=dm_counts,
            title="Diabetes Status in Main Clinical Cohort",
            xlabel="Diabetes mellitus",
            ylabel="Number of patients",
            output_path=FIGURES_DIR / "diabetes_status_main_cohort.png"
        )

    # 7. Insurance access in clean subcohort
    if "acceso_a_seguro_medico_de_salud" in sub_clean.columns:
        insurance_counts = sub_clean["acceso_a_seguro_medico_de_salud"].value_counts(dropna=False).sort_index()
        save_barplot(
            series=insurance_counts,
            title="Insurance Access in Clean Sociodemographic Subcohort",
            xlabel="Insurance access",
            ylabel="Number of patients",
            output_path=FIGURES_DIR / "insurance_access_subcohort.png"
        )

    # 8. Economic barriers in clean subcohort
    if "barreras_economicas" in sub_clean.columns:
        economic_counts = sub_clean["barreras_economicas"].value_counts(dropna=False).sort_index()
        save_barplot(
            series=economic_counts,
            title="Economic Barriers in Clean Sociodemographic Subcohort",
            xlabel="Economic barriers",
            ylabel="Number of patients",
            output_path=FIGURES_DIR / "economic_barriers_subcohort.png"
        )

    # 9. Educational level in clean subcohort
    if "nivel_educativo" in sub_clean.columns:
        edu_counts = sub_clean["nivel_educativo"].value_counts(dropna=False)
        save_barplot(
            series=edu_counts,
            title="Educational Level in Clean Sociodemographic Subcohort",
            xlabel="Educational level",
            ylabel="Number of patients",
            output_path=FIGURES_DIR / "educational_level_subcohort.png",
            rotation=45
        )

    print("Figure generation completed successfully.")
    print(f"Figures saved to: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
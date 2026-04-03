from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

FILE = RAW_DIR / "DATASET_CONSULTA_UNAPS_PERAVIA_2024.xlsx"


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("+", "plus", regex=False)
        .str.replace("%", "pct", regex=False)
    )
    return df


def clean_id(df: pd.DataFrame) -> pd.DataFrame:
    if "id" in df.columns:
        df["id"] = (
            df["id"]
            .astype("string")
            .str.strip()
            .str.lower()
        )
    return df


def clean_text(df: pd.DataFrame) -> pd.DataFrame:
    text_cols = df.select_dtypes(include=["object", "string"]).columns
    for col in text_cols:
        df[col] = df[col].where(df[col].notna(), pd.NA)
        df[col] = df[col].astype("string").str.strip().str.lower()
    return df


def fix_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    if "sexo" in df.columns:
        df["sexo"] = df["sexo"].replace({
            "masculino": "male",
            "femenino": "female"
        })

    binary_map = {
        "si": 1, "sí": 1,
        "no": 0,
        "anemia": 1,
        "not anemia": 0
    }

    for col in ["hta", "diabetes_mellitus", "anemia", "enfermedad_coronaria", "edema_ext_inferior"]:
        if col in df.columns:
            df[col] = df[col].replace(binary_map)

    if "erc_calsificacion" in df.columns:
        df["erc_calsificacion"] = (
            df["erc_calsificacion"]
            .astype("string")
            .str.replace("erc kdigo ", "", regex=False)
            .str.replace("normal  funcion", "normal", regex=False)
            .str.replace("normal funcion", "normal", regex=False)
            .str.strip()
        )

    if "localidad" in df.columns:
        df["localidad"] = (
            df["localidad"]
            .astype("string")
            .str.strip()
            .str.lower()
        )

    return df


def numeric_conversion(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = [
        "edad",
        "presion_arterial_diastolica",
        "gravedad_urinaria_especifica",
        "glucosa_serica_random",
        "urea",
        "creatinina_serica",
        "sodio",
        "potasio",
        "hemoglobina",
        "hto_pct",
        "conteo_gb_blancos"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_excel(FILE)

    df = clean_columns(df)
    df = clean_id(df)
    df = clean_text(df)
    df = fix_categoricals(df)
    df = numeric_conversion(df)

    output_file = PROCESSED_DIR / "unaps_clean_v2.csv"
    df.to_csv(output_file, index=False)

    print(f"UNAPS V2 clean done: {output_file}")


if __name__ == "__main__":
    main()
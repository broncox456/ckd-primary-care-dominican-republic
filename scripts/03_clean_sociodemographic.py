from pathlib import Path
import pandas as pd
import unicodedata


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

FILE = RAW_DIR / "MATRIZ_SOCIODEMOGRAFICA_ERC_PERAVIA_2024.xlsx"


def strip_accents(text: str) -> str:
    text = str(text)
    text = unicodedata.normalize("NFKD", text)
    return "".join(char for char in text if not unicodedata.combining(char))


def fix_mojibake(text):
    """
    Fix common mojibake patterns such as:
    difÃ­cil -> difícil
    desinformaciÃ³n -> desinformación
    tabÃº -> tabú
    """
    if pd.isna(text):
        return pd.NA

    text = str(text)

    replacements = {
        "Ã¡": "á",
        "Ã©": "é",
        "Ã­": "í",
        "Ã³": "ó",
        "Ãº": "ú",
        "Ã": "Á",
        "Ã‰": "É",
        "Ã": "Í",
        "Ã“": "Ó",
        "Ãš": "Ú",
        "Ã±": "ñ",
        "Ã‘": "Ñ",
        "Ã¼": "ü",
        "Ãœ": "Ü",
        "â€™": "'",
        "â€“": "-",
        "â€”": "-",
        "â€œ": '"',
        "â€": '"',
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    try:
        text = text.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

    return text


def clean_column_name(col: str) -> str:
    col = fix_mojibake(col)
    col = strip_accents(col)
    col = col.strip().lower()
    col = col.replace("/", "_")
    col = col.replace(".", "")
    col = col.replace("%", "pct")
    col = col.replace("+", "plus")
    col = col.replace("(", "")
    col = col.replace(")", "")
    col = col.replace("-", "_")
    col = "_".join(col.split())
    return col


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [clean_column_name(col) for col in df.columns]

    if "id" in df.columns:
        df = df.rename(columns={"id": "paciente_id"})

    if "gastos__medicamentos_mensual_dop" in df.columns:
        df = df.rename(
            columns={"gastos__medicamentos_mensual_dop": "gastos_medicamentos_mensual_dop"}
        )

    return df


def clean_text(df: pd.DataFrame) -> pd.DataFrame:
    text_cols = df.select_dtypes(include=["object", "string"]).columns

    for col in text_cols:
        df[col] = df[col].where(df[col].notna(), pd.NA)
        df[col] = df[col].map(fix_mojibake)
        df[col] = df[col].map(fix_mojibake)
        df[col] = df[col].astype("string").str.strip().str.lower()

    return df


def fix_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    if "sexo" in df.columns:
        df["sexo"] = df["sexo"].replace({
            "masculino": "male",
            "femenino": "female"
        })

    binary_map = {
        "si": 1,
        "sí": 1,
        "no": 0
    }

    binary_cols = [
        "acceso_a_seguro_medico_de_salud",
        "dependencia_de_remesas",
        "uso_de_medicinas_tradicionales",
        "recibe_ayuda_gubernamental_economica",
        "ha_recibido_info_preventiva_sobre_erc",
    ]

    for col in binary_cols:
        if col in df.columns:
            df[col] = df[col].replace(binary_map)

    if "localidad" in df.columns:
        df["localidad"] = df["localidad"].astype("string").str.strip().str.lower()

    return df


def convert_paciente_id(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert:
    unap01 -> 1
    unap02 -> 2
    """
    if "paciente_id" in df.columns:
        df["paciente_id"] = (
            df["paciente_id"]
            .astype("string")
            .str.extract(r"(\d+)", expand=False)
        )
        df["paciente_id"] = pd.to_numeric(df["paciente_id"], errors="coerce")

    return df


def numeric_conversion(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = [
        "edad",
        "tiempo_en_meses_diagnosticado_erc",
        "creatinina_serica_mg_dl",
        "filtracion_glomerular_ml_min_173m2",
        "proteinuria_g_24h",
        "visitas_a_emergencias_o_internamientos",
        "consultas_de_nefrologia_en_el_ultimo_ano",
        "gastos_medicamentos_mensual_dop",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_excel(FILE)

    df = clean_column_names(df)
    df = clean_text(df)
    df = fix_categoricals(df)
    df = convert_paciente_id(df)
    df = numeric_conversion(df)

    output_file = PROCESSED_DIR / "socio_clean_v2.csv"
    df.to_csv(output_file, index=False)

    print(f"SOCIO V2 clean done: {output_file}")
    print("Columns:")
    for col in df.columns:
        print(f" - {col}")


if __name__ == "__main__":
    main()
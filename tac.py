import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(
    page_title="Cruce de RUT",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Cruce de archivos Excel por RUT")

st.write(
    "Carga dos archivos Excel y obtén las filas cuyos RUT aparecen "
    "en ambos archivos, conservando las columnas del archivo principal."
)

# ----------------------------------------------------------
# Función para normalizar RUT
# ---------------------------------------------------------

def normalizar_rut(rut):
    if pd.isna(rut):
        return ""

    rut = str(rut).strip().upper()

    # Eliminar puntos, guiones y espacios
    rut = rut.replace(".", "")
    rut = rut.replace("-", "")
    rut = rut.replace(" ", "")

    return rut


# ---------------------------------------------------------
# Cargar archivos
# ---------------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    archivo_principal = st.file_uploader(
        "📁 Archivo principal",
        type=["xlsx", "xls"]
    )

with col2:
    archivo_comparar = st.file_uploader(
        "📁 Archivo para comparar",
        type=["xlsx", "xls"]
    )


if archivo_principal and archivo_comparar:

    # Leer Excel
    df_principal = pd.read_excel(archivo_principal)
    df_comparar = pd.read_excel(archivo_comparar)

    st.success("Archivos cargados correctamente.")

    # ---------------------------------------------------------
    # Seleccionar columnas RUT
    # ---------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Archivo principal")

        columna_rut_1 = st.selectbox(
            "Selecciona la columna que contiene el RUT:",
            df_principal.columns,
            key="rut_1"
        )

    with col2:
        st.subheader("Archivo para comparar")

        columna_rut_2 = st.selectbox(
            "Selecciona la columna que contiene el RUT:",
            df_comparar.columns,
            key="rut_2"
        )

    # ---------------------------------------------------------
    # Procesar
    # ---------------------------------------------------------

    if st.button("🔎 Comparar RUT", type="primary"):

        # Crear columnas temporales normalizadas
        df_principal["_RUT_NORMALIZADO"] = (
            df_principal[columna_rut_1]
            .apply(normalizar_rut)
        )

        df_comparar["_RUT_NORMALIZADO"] = (
            df_comparar[columna_rut_2]
            .apply(normalizar_rut)
        )

        # Obtener RUT que existen en ambos archivos
        ruts_principal = set(
            df_principal["_RUT_NORMALIZADO"]
        )

        ruts_comparar = set(
            df_comparar["_RUT_NORMALIZADO"]
        )

        ruts_coincidentes = (
            ruts_principal.intersection(ruts_comparar)
        )

        # Eliminar valores vacíos
        ruts_coincidentes.discard("")

        # Filtrar archivo principal
        resultado = df_principal[
            df_principal["_RUT_NORMALIZADO"].isin(
                ruts_coincidentes
            )
        ].copy()

        # Eliminar columna auxiliar
        resultado.drop(
            columns=["_RUT_NORMALIZADO"],
            inplace=True
        )

        # ---------------------------------------------------------
        # Mostrar estadísticas
        # ---------------------------------------------------------

        st.subheader("📊 Resultado")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Filas archivo principal",
                len(df_principal)
            )

        with c2:
            st.metric(
                "RUT coincidentes",
                len(ruts_coincidentes)
            )

        with c3:
            st.metric(
                "Filas resultado",
                len(resultado)
            )

        st.dataframe(
            resultado,
            use_container_width=True
        )

        # ---------------------------------------------------------
        # Descargar Excel
        # ---------------------------------------------------------

        output = BytesIO()

        with pd.ExcelWriter(
            output,
            engine="openpyxl"
        ) as writer:

            resultado.to_excel(
                writer,
                index=False,
                sheet_name="Resultado"
            )

        output.seek(0)

        st.download_button(
            label="⬇️ Descargar resultado en Excel",
            data=output,
            file_name="resultado_cruce_rut.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

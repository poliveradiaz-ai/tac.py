import streamlit as st
import pandas as pd
from io import BytesIO

# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="Cruce de RUT",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Cruce de archivos Excel por RUT")

st.write(
    "Carga dos archivos Excel y la aplicación buscará los RUT "
    "que existen en ambos archivos."
)

# =========================================================
# FUNCIÓN PARA NORMALIZAR RUT
# =========================================================

def normalizar_rut(valor):

    if pd.isna(valor):
        return ""

    rut = str(valor).strip().upper()

    # Eliminar puntos
    rut = rut.replace(".", "")

    # Eliminar guión
    rut = rut.replace("-", "")

    # Eliminar espacios
    rut = rut.replace(" ", "")

    return rut


# =========================================================
# CARGA DE ARCHIVOS
# =========================================================

archivo_principal = st.file_uploader(
    "📁 Archivo PRINCIPAL",
    type=["xlsx"]
)

archivo_comparar = st.file_uploader(
    "📁 Archivo para COMPARAR",
    type=["xlsx"]
)


# =========================================================
# PROCESAMIENTO
# =========================================================

if archivo_principal is not None and archivo_comparar is not None:

    # -----------------------------------------------------
    # LEER ARCHIVOS
    # -----------------------------------------------------

    try:

        df_principal = pd.read_excel(
            archivo_principal,
            engine="openpyxl"
        )

        df_comparar = pd.read_excel(
            archivo_comparar,
            engine="openpyxl"
        )

    except Exception as e:

        st.error("❌ No se pudieron leer los archivos Excel.")

        st.exception(e)

        st.stop()


    # -----------------------------------------------------
    # VERIFICAR QUE TENGAN COLUMNAS
    # -----------------------------------------------------

    if len(df_principal.columns) == 0:

        st.error("❌ El archivo principal no contiene columnas.")

        st.stop()


    if len(df_comparar.columns) == 0:

        st.error("❌ El archivo para comparar no contiene columnas.")

        st.stop()


    st.success("✅ Los dos archivos fueron cargados correctamente.")


    # -----------------------------------------------------
    # MOSTRAR INFORMACIÓN
    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Filas archivo principal",
            len(df_principal)
        )

    with col2:

        st.metric(
            "Filas archivo comparar",
            len(df_comparar)
        )


    # -----------------------------------------------------
    # SELECCIONAR COLUMNAS RUT
    # -----------------------------------------------------

    st.subheader("🔑 Seleccionar columnas RUT")

    col1, col2 = st.columns(2)

    with col1:

        columna_rut_principal = st.selectbox(
            "RUT del archivo principal:",
            df_principal.columns,
            key="rut_principal"
        )

    with col2:

        columna_rut_comparar = st.selectbox(
            "RUT del archivo para comparar:",
            df_comparar.columns,
            key="rut_comparar"
        )


    # -----------------------------------------------------
    # BOTÓN DE COMPARACIÓN
    # -----------------------------------------------------

    if st.button(
        "🔎 Buscar coincidencias",
        type="primary"
    ):

        # ---------------------------------------------
        # NORMALIZAR RUT
        # ---------------------------------------------

        rut_principal = (
            df_principal[columna_rut_principal]
            .apply(normalizar_rut)
        )

        rut_comparar = (
            df_comparar[columna_rut_comparar]
            .apply(normalizar_rut)
        )


        # ---------------------------------------------
        # ELIMINAR RUT VACÍOS
        # ---------------------------------------------

        ruts_comparar = set(rut_comparar)

        ruts_comparar.discard("")


        # ---------------------------------------------
        # BUSCAR COINCIDENCIAS
        # ---------------------------------------------

        resultado = df_principal[
            rut_principal.isin(ruts_comparar)
        ].copy()


        # ---------------------------------------------
        # MOSTRAR RESULTADOS
        # ---------------------------------------------

        st.subheader("📊 Resultado")


        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "RUT archivo comparar",
                len(ruts_comparar)
            )


        with col2:

            st.metric(
                "Filas coincidentes",
                len(resultado)
            )


        with col3:

            st.metric(
                "Columnas resultado",
                len(resultado.columns)
            )


        # ---------------------------------------------
        # SI NO HAY COINCIDENCIAS
        # ---------------------------------------------

        if resultado.empty:

            st.warning(
                "⚠️ No se encontraron RUT coincidentes."
            )

            st.stop()


        # ---------------------------------------------
        # MOSTRAR TABLA
        # ---------------------------------------------

        st.success(
            f"✅ Se encontraron {len(resultado)} "
            f"filas coincidentes."
        )


        st.dataframe(
            resultado,
            use_container_width=True,
            hide_index=True
        )


        # ---------------------------------------------
        # CREAR EXCEL
        # ---------------------------------------------

        try:

            archivo_salida = BytesIO()


            # Crear Excel
            with pd.ExcelWriter(
                archivo_salida,
                engine="openpyxl"
            ) as writer:

                resultado.to_excel(
                    writer,
                    index=False,
                    sheet_name="Coincidencias"
                )


            # Volver al inicio del archivo
            archivo_salida.seek(0)


            # -----------------------------------------
            # BOTÓN DESCARGA
            # -----------------------------------------

            st.download_button(
                label="⬇️ Descargar Excel",
                data=archivo_salida.getvalue(),
                file_name="coincidencias_rut.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                )
            )


        except Exception as e:

            st.error(
                "❌ Se produjo un error al crear el Excel."
            )

            st.exception(e)

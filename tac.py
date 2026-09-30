import streamlit as st
import pandas as pd
from io import BytesIO

# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="Cruce de RUT y Fecha",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Cruce de archivos por RUT y Fecha")

st.write(
    "La aplicación buscará coincidencias cuando el RUT y la Fecha "
    "sean iguales en ambos archivos."
)


# =========================================================
# FUNCIONES
# =========================================================

def normalizar_rut(valor):

    if pd.isna(valor):
        return ""

    rut = str(valor).strip().upper()

    rut = rut.replace(".", "")
    rut = rut.replace("-", "")
    rut = rut.replace(" ", "")

    return rut


def normalizar_fecha(valor):

    if pd.isna(valor):
        return pd.NaT

    try:
        return pd.to_datetime(
            valor,
            errors="coerce"
        ).normalize()

    except Exception:
        return pd.NaT


# =========================================================
# CARGAR ARCHIVOS
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

        st.error(
            "❌ No se pudieron leer los archivos Excel."
        )

        st.exception(e)

        st.stop()


    # -----------------------------------------------------
    # VERIFICAR COLUMNAS
    # -----------------------------------------------------

    if df_principal.empty:

        st.error(
            "❌ El archivo principal está vacío."
        )

        st.stop()


    if df_comparar.empty:

        st.error(
            "❌ El archivo para comparar está vacío."
        )

        st.stop()


    st.success(
        "✅ Los dos archivos fueron cargados correctamente."
    )


    # -----------------------------------------------------
    # INFORMACIÓN
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


    # =====================================================
    # SELECCIÓN DE COLUMNAS
    # =====================================================

    st.subheader("🔑 Seleccionar RUT y Fecha")


    col1, col2 = st.columns(2)


    # -----------------------------------------------------
    # ARCHIVO PRINCIPAL
    # -----------------------------------------------------

    with col1:

        st.markdown("### 📁 Archivo principal")

        columna_rut_principal = st.selectbox(
            "Columna RUT:",
            df_principal.columns,
            key="rut_principal"
        )

        columna_fecha_principal = st.selectbox(
            "Columna Fecha:",
            df_principal.columns,
            key="fecha_principal"
        )


    # -----------------------------------------------------
    # ARCHIVO COMPARAR
    # -----------------------------------------------------

    with col2:

        st.markdown("### 📁 Archivo para comparar")

        columna_rut_comparar = st.selectbox(
            "Columna RUT:",
            df_comparar.columns,
            key="rut_comparar"
        )

        columna_fecha_comparar = st.selectbox(
            "Columna Fecha:",
            df_comparar.columns,
            key="fecha_comparar"
        )


    # =====================================================
    # BOTÓN COMPARAR
    # =====================================================

    if st.button(
        "🔎 Comparar RUT + Fecha",
        type="primary"
    ):

        # -------------------------------------------------
        # CREAR COPIAS
        # -------------------------------------------------

        principal = df_principal.copy()
        comparar = df_comparar.copy()


        # -------------------------------------------------
        # NORMALIZAR RUT
        # -------------------------------------------------

        principal["_RUT"] = (
            principal[columna_rut_principal]
            .apply(normalizar_rut)
        )

        comparar["_RUT"] = (
            comparar[columna_rut_comparar]
            .apply(normalizar_rut)
        )


        # -------------------------------------------------
        # NORMALIZAR FECHAS
        # -------------------------------------------------

        principal["_FECHA"] = (
            principal[columna_fecha_principal]
            .apply(normalizar_fecha)
        )

        comparar["_FECHA"] = (
            comparar[columna_fecha_comparar]
            .apply(normalizar_fecha)
        )


        # -------------------------------------------------
        # ELIMINAR REGISTROS SIN RUT O FECHA
        # -------------------------------------------------

        principal_validos = principal[
            (principal["_RUT"] != "") &
            (principal["_FECHA"].notna())
        ].copy()


        comparar_validos = comparar[
            (comparar["_RUT"] != "") &
            (comparar["_FECHA"].notna())
        ].copy()


        # -------------------------------------------------
        # CREAR LLAVE RUT + FECHA
        # -------------------------------------------------

        principal_validos["_LLAVE"] = (
            principal_validos["_RUT"]
            + "_"
            + principal_validos["_FECHA"].astype(str)
        )


        comparar_validos["_LLAVE"] = (
            comparar_validos["_RUT"]
            + "_"
            + comparar_validos["_FECHA"].astype(str)
        )


        # -------------------------------------------------
        # OBTENER LLAVES COINCIDENTES
        # -------------------------------------------------

        llaves_comparar = set(
            comparar_validos["_LLAVE"]
        )

        llaves_comparar.discard("")


        # -------------------------------------------------
        # FILTRAR ARCHIVO PRINCIPAL
        # -------------------------------------------------

        resultado = principal_validos[
            principal_validos["_LLAVE"].isin(
                llaves_comparar
            )
        ].copy()


        # -------------------------------------------------
        # ELIMINAR COLUMNAS AUXILIARES
        # -------------------------------------------------

        columnas_auxiliares = [
            "_RUT",
            "_FECHA",
            "_LLAVE"
        ]

        resultado.drop(
            columns=columnas_auxiliares,
            inplace=True,
            errors="ignore"
        )


        # =================================================
        # RESULTADOS
        # =================================================

        st.subheader("📊 Resultado")


        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "Registros válidos principal",
                len(principal_validos)
            )


        with col2:

            st.metric(
                "RUT + Fecha coincidentes",
                len(set(
                    principal_validos[
                        principal_validos["_LLAVE"].isin(
                            llaves_comparar
                        )
                    ]["_LLAVE"]
                ))
            )


        with col3:

            st.metric(
                "Filas resultado",
                len(resultado)
            )


        # -------------------------------------------------
        # SIN RESULTADOS
        # -------------------------------------------------

        if resultado.empty:

            st.warning(
                "⚠️ No se encontraron coincidencias "
                "de RUT y Fecha."
            )

            st.stop()


        # -------------------------------------------------
        # MOSTRAR RESULTADO
        # -------------------------------------------------

        st.success(
            f"✅ Se encontraron {len(resultado)} "
            f"filas coincidentes."
        )


        st.dataframe(
            resultado,
            use_container_width=True,
            hide_index=True
        )


        # =================================================
        # GENERAR EXCEL
        # =================================================

        try:

            archivo_salida = BytesIO()


            with pd.ExcelWriter(
                archivo_salida,
                engine="openpyxl"
            ) as writer:

                resultado.to_excel(
                    writer,
                    index=False,
                    sheet_name="Coincidencias"
                )


            archivo_salida.seek(0)


            # -------------------------------------------------
            # DESCARGAR
            # -------------------------------------------------

            st.download_button(
                label="⬇️ Descargar Excel con coincidencias",
                data=archivo_salida.getvalue(),
                file_name="coincidencias_rut_fecha.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                )
            )


        except Exception as e:

            st.error(
                "❌ Error al generar el archivo Excel."
            )

            st.exception(e)

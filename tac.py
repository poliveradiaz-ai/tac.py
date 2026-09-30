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
    "Sube dos archivos Excel. La aplicación buscará los RUT que "
    "aparecen en ambos y conservará las columnas del archivo principal."
)

# ---------------------------------------------------------
# FUNCIÓN PARA NORMALIZAR RUT
# ---------------------------------------------------------

def normalizar_rut(valor):
    if pd.isna(valor):
        return ""

    rut = str(valor).strip().upper()

    # Eliminar puntos, guiones y espacios
    rut = rut.replace(".", "")
    rut = rut.replace("-", "")
    rut = rut.replace(" ", "")

    return rut


# ---------------------------------------------------------
# CARGAR ARCHIVOS
# ---------------------------------------------------------

archivo_principal = st.file_uploader(
    "📁 Selecciona el archivo PRINCIPAL",
    type=["xlsx"]
)

archivo_comparar = st.file_uploader(
    "📁 Selecciona el archivo para COMPARAR",
    type=["xlsx"]
)


# ---------------------------------------------------------
# PROCESAR
# ---------------------------------------------------------

if archivo_principal is not None and archivo_comparar is not None:

    try:
        df_principal = pd.read_excel(
            archivo_principal,
            engine="openpyxl"
        )

        df_comparar = pd.read_excel(
            archivo_comparar,
            engine="openpyxl"
        )

        st.success("✅ Archivos cargados correctamente.")

        # -------------------------------------------------
        # SELECCIÓN DE COLUMNAS RUT
        # -------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Archivo principal")

            columna_rut_principal = st.selectbox(
                "Selecciona la columna RUT:",
                df_principal.columns,
                key="principal"
            )

        with col2:
            st.subheader("Archivo para comparar")

            columna_rut_comparar = st.selectbox(
                "Selecciona la columna RUT:",
                df_comparar.columns,
                key="comparar"
            )

        # -------------------------------------------------
        # BOTÓN DE CRUCE
        # -------------------------------------------------

        if st.button("🔎 Buscar coincidencias", type="primary"):

            # Crear RUT normalizados
            rut_principal = (
                df_principal[columna_rut_principal]
                .apply(normalizar_rut)
            )

            rut_comparar = (
                df_comparar[columna_rut_comparar]
                .apply(normalizar_rut)
            )

            # Crear conjunto de RUT del segundo archivo
            ruts_comparar = set(rut_comparar)

            # Eliminar vacíos
            ruts_comparar.discard("")

            # Filtrar el archivo principal
            resultado = df_principal[
                rut_principal.isin(ruts_comparar)
            ].copy()

            # -------------------------------------------------
            # RESULTADOS
            # -------------------------------------------------

            st.subheader("📊 Resultado")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Filas archivo principal",
                    len(df_principal)
                )

            with col2:
                st.metric(
                    "RUT en archivo comparado",
                    len(ruts_comparar)
                )

            with col3:
                st.metric(
                    "Filas coincidentes",
                    len(resultado)
                )

            if len(resultado) == 0:

                st.warning(
                    "⚠️ No se encontraron RUT coincidentes."
                )

            else:

                st.success(
                    f"✅ Se encontraron {len(resultado)} "
                    f"filas coincidentes."
                )

                # Mostrar resultado
                st.dataframe(
                    resultado,
                    use_container_width=True,
                    hide_index=True
                )
# -------------------------------------------------
# CREAR EXCEL PARA DESCARGAR
# -------------------------------------------------

        archivo_salida = BytesIO()
        
        try:
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
        
            st.download_button(
                label="⬇️ Descargar Excel con coincidencias",
                data=archivo_salida.getvalue(),
                file_name="coincidencias_rut.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        except Exception as e:
            st.error("❌ No se pudo generar el archivo Excel.")
            st.exception(e)
    
                  

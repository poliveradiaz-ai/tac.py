import streamlit as st
import pandas as pd
from io import BytesIO

# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="Cruce RUT y Sexo",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Cruce automático de RUT y Sexo")

st.write(
    "El sistema compara automáticamente el RUT del archivo principal "
    "con el RUN paciente del archivo secundario y agrega el Sexo."
)


# =========================================================
# FUNCIÓN NORMALIZAR RUT
# =========================================================

def normalizar_rut(valor):

    if pd.isna(valor):
        return ""

    valor = str(valor).strip().upper()

    # Eliminar puntos
    valor = valor.replace(".", "")

    # Eliminar guiones
    valor = valor.replace("-", "")

    # Eliminar espacios
    valor = valor.replace(" ", "")

    return valor


# =========================================================
# BUSCAR COLUMNA POR NOMBRE
# =========================================================

def encontrar_columna(df, nombres):

    columnas_normalizadas = {
        str(col).strip().lower(): col
        for col in df.columns
    }

    for nombre in nombres:

        nombre_normalizado = (
            nombre.strip().lower()
        )

        if nombre_normalizado in columnas_normalizadas:

            return columnas_normalizadas[
                nombre_normalizado
            ]

    return None


# =========================================================
# CARGAR ARCHIVOS
# =========================================================

st.subheader("📁 Cargar archivos")

archivo_principal = st.file_uploader(
    "Archivo PRINCIPAL",
    type=["xlsx"],
    key="principal"
)

archivo_secundario = st.file_uploader(
    "Archivo SECUNDARIO",
    type=["xlsx"],
    key="secundario"
)


# =========================================================
# PROCESAR ARCHIVOS
# =========================================================

if archivo_principal and archivo_secundario:

    # -----------------------------------------------------
    # LEER ARCHIVOS
    # -----------------------------------------------------

    try:

        df_principal = pd.read_excel(
            archivo_principal,
            engine="openpyxl"
        )

        df_secundario = pd.read_excel(
            archivo_secundario,
            engine="openpyxl"
        )

    except Exception as e:

        st.error(
            "❌ No se pudieron leer los archivos Excel."
        )

        st.exception(e)

        st.stop()


    # -----------------------------------------------------
    # BUSCAR COLUMNAS AUTOMÁTICAMENTE
    # -----------------------------------------------------

    columna_rut_principal = encontrar_columna(
        df_principal,
        [
            "RUT",
            "Rut",
            "rut"
        ]
    )


    columna_run_secundario = encontrar_columna(
        df_secundario,
        [
            "RUN paciente",
            "RUN PACIENTE",
            "RUN_PACIENTE",
            "RUN del paciente",
            "RUN DEL PACIENTE",
            "RUN"
        ]
    )


    columna_sexo = encontrar_columna(
        df_secundario,
        [
            "Sexo",
            "SEXO",
            "sexo"
        ]
    )


    # -----------------------------------------------------
    # VERIFICAR COLUMNAS
    # -----------------------------------------------------

    if columna_rut_principal is None:

        st.error(
            "❌ No encontré una columna llamada 'RUT' "
            "en el archivo principal."
        )

        st.write(
            "Columnas encontradas:",
            list(df_principal.columns)
        )

        st.stop()


    if columna_run_secundario is None:

        st.error(
            "❌ No encontré la columna 'RUN paciente' "
            "en el archivo secundario."
        )

        st.write(
            "Columnas encontradas:",
            list(df_secundario.columns)
        )

        st.stop()


    if columna_sexo is None:

        st.error(
            "❌ No encontré una columna 'Sexo' "
            "en el archivo secundario."
        )

        st.write(
            "Columnas encontradas:",
            list(df_secundario.columns)
        )

        st.stop()


    # -----------------------------------------------------
    # INFORMACIÓN
    # -----------------------------------------------------

    st.success(
        "✅ Columnas encontradas automáticamente."
    )

    st.write(
        f"**Archivo principal:** `{columna_rut_principal}`"
    )

    st.write(
        f"**Archivo secundario:** "
        f"`{columna_run_secundario}` → `{columna_sexo}`"
    )


    # =====================================================
    # NORMALIZAR RUT
    # =====================================================

    df_principal["_RUT_BUSQUEDA"] = (
        df_principal[columna_rut_principal]
        .apply(normalizar_rut)
    )


    df_secundario["_RUN_BUSQUEDA"] = (
        df_secundario[columna_run_secundario]
        .apply(normalizar_rut)
    )


    # =====================================================
    # CREAR TABLA RUN → SEXO
    # =====================================================

    tabla_sexo = df_secundario[
        [
            "_RUN_BUSQUEDA",
            columna_sexo
        ]
    ].copy()


    # Eliminar RUN vacíos
    tabla_sexo = tabla_sexo[
        tabla_sexo["_RUN_BUSQUEDA"] != ""
    ]


    # Eliminar duplicados
    tabla_sexo = tabla_sexo.drop_duplicates(
        subset="_RUN_BUSQUEDA",
        keep="first"
    )


    # =====================================================
    # CREAR DICCIONARIO
    # =====================================================

    diccionario_sexo = dict(
        zip(
            tabla_sexo["_RUN_BUSQUEDA"],
            tabla_sexo[columna_sexo]
        )
    )


    # =====================================================
    # AGREGAR SEXO AL ARCHIVO PRINCIPAL
    # =====================================================

    df_principal["Sexo"] = (
        df_principal["_RUT_BUSQUEDA"]
        .map(diccionario_sexo)
    )


    # =====================================================
    # NORMALIZAR SEXO
    # =====================================================

    df_principal["Sexo"] = (
        df_principal["Sexo"]
        .fillna("No encontrado")
        .astype(str)
        .str.strip()
    )


    # =====================================================
    # ELIMINAR COLUMNA AUXILIAR
    # =====================================================

    df_principal.drop(
        columns=["_RUT_BUSQUEDA"],
        inplace=True
    )


    # =====================================================
    # RESULTADO
    # =====================================================

    total = len(df_principal)

    encontrados = (
        df_principal["Sexo"] != "No encontrado"
    ).sum()

    no_encontrados = (
        df_principal["Sexo"] == "No encontrado"
    ).sum()


    st.subheader("📊 Resultado")


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Registros principales",
            total
        )


    with col2:

        st.metric(
            "Sexo encontrado",
            encontrados
        )


    with col3:

        st.metric(
            "No encontrado",
            no_encontrados
        )


    # =====================================================
    # MOSTRAR RESULTADO
    # =====================================================

    st.dataframe(
        df_principal,
        use_container_width=True,
        hide_index=True
    )


    # =====================================================
    # GENERAR EXCEL
    # =====================================================

    try:

        archivo_salida = BytesIO()


        with pd.ExcelWriter(
            archivo_salida,
            engine="openpyxl"
        ) as writer:

            df_principal.to_excel(
                writer,
                index=False,
                sheet_name="Resultado"
            )


        archivo_salida.seek(0)


        # =================================================
        # DESCARGA
        # =================================================

        st.download_button(
            label="⬇️ Descargar Excel resultado",
            data=archivo_salida.getvalue(),
            file_name="resultado_con_sexo.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )


    except Exception as e:

        st.error(
            "❌ No se pudo generar el Excel."
        )

        st.exception(e)

import streamlit as st
import pandas as pd
from io import BytesIO

# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="Cruce RUT, Fecha, Sexo y Atención",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Cruce automático de RUT, Fecha, Sexo y Atención")

st.write(
    "El sistema compara el RUT y la fecha de atención entre ambos "
    "archivos y agrega Sexo, Previsión y Modalidad de Atención "
    "al archivo principal."
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
# FUNCIÓN NORMALIZAR FECHA
# =========================================================

def normalizar_fecha(valor):

    if pd.isna(valor):
        return pd.NaT

    try:
        fecha = pd.to_datetime(
            valor,
            errors="coerce",
            dayfirst=True
        )

        if pd.isna(fecha):
            return pd.NaT

        # Eliminar hora y dejar solamente la fecha
        return fecha.normalize()

    except Exception:
        return pd.NaT


# =========================================================
# BUSCAR COLUMNA POR NOMBRE
# =========================================================

def encontrar_columna(df, nombres):

    columnas_normalizadas = {
        str(col).strip().lower(): col
        for col in df.columns
    }

    for nombre in nombres:

        nombre_normalizado = nombre.strip().lower()

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


    # =====================================================
    # BUSCAR COLUMNAS DEL ARCHIVO PRINCIPAL
    # =====================================================

    columna_rut_principal = encontrar_columna(
        df_principal,
        [
            "RUT",
            "Rut",
            "rut"
        ]
    )

    columna_fecha_principal = encontrar_columna(
        df_principal,
        [
            "FECHA",
            "Fecha",
            "fecha"
        ]
    )


    # =====================================================
    # BUSCAR COLUMNAS DEL ARCHIVO SECUNDARIO
    # =====================================================

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

    columna_fecha_atencion = encontrar_columna(
        df_secundario,
        [
            "FECHA DE ATENCION",
            "Fecha de Atencion",
            "FECHA DE ATENCIÓN",
            "Fecha de Atención",
            "fecha de atencion",
            "fecha de atención"
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

    columna_prevision = encontrar_columna(
        df_secundario,
        [
            "PREVISIÓN",
            "PREVISION",
            "Previsión",
            "Prevision"
        ]
    )

    columna_modalidad = encontrar_columna(
        df_secundario,
        [
            "MODALIDAD DE ATENCIÓN",
            "MODALIDAD DE ATENCION",
            "Modalidad de Atención",
            "Modalidad de Atencion",
            "modalidad de atención",
            "modalidad de atencion"
        ]
    )


    # =====================================================
    # VERIFICAR COLUMNAS PRINCIPALES
    # =====================================================

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


    if columna_fecha_principal is None:

        st.error(
            "❌ No encontré una columna llamada 'FECHA' "
            "en el archivo principal."
        )

        st.write(
            "Columnas encontradas:",
            list(df_principal.columns)
        )

        st.stop()


    # =====================================================
    # VERIFICAR COLUMNAS SECUNDARIAS
    # =====================================================

    columnas_faltantes = []

    if columna_run_secundario is None:
        columnas_faltantes.append("RUN paciente")

    if columna_fecha_atencion is None:
        columnas_faltantes.append("FECHA DE ATENCION")

    if columna_sexo is None:
        columnas_faltantes.append("Sexo")

    if columna_prevision is None:
        columnas_faltantes.append("PREVISIÓN")

    if columna_modalidad is None:
        columnas_faltantes.append("MODALIDAD DE ATENCIÓN")


    if columnas_faltantes:

        st.error(
            "❌ No encontré las siguientes columnas "
            "en el archivo secundario:"
        )

        for columna in columnas_faltantes:
            st.write(f"- {columna}")

        st.write(
            "Columnas encontradas en el archivo secundario:",
            list(df_secundario.columns)
        )

        st.stop()


    # =====================================================
    # INFORMACIÓN
    # =====================================================

    st.success(
        "✅ Todas las columnas necesarias fueron encontradas."
    )

    st.write(
        f"**Archivo principal:** "
        f"`{columna_rut_principal}` + `{columna_fecha_principal}`"
    )

    st.write(
        f"**Archivo secundario:** "
        f"`{columna_run_secundario}` + "
        f"`{columna_fecha_atencion}`"
    )

    st.write(
        f"**Datos que se agregarán:** "
        f"`{columna_sexo}`, "
        f"`{columna_prevision}`, "
        f"`{columna_modalidad}`"
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
    # NORMALIZAR FECHAS
    # =====================================================

    df_principal["_FECHA_BUSQUEDA"] = (
        df_principal[columna_fecha_principal]
        .apply(normalizar_fecha)
    )

    df_secundario["_FECHA_BUSQUEDA"] = (
        df_secundario[columna_fecha_atencion]
        .apply(normalizar_fecha)
    )


    # =====================================================
    # MOSTRAR INFORMACIÓN DE FECHAS
    # =====================================================

    fechas_principal_invalidas = (
        df_principal["_FECHA_BUSQUEDA"].isna().sum()
    )

    fechas_secundario_invalidas = (
        df_secundario["_FECHA_BUSQUEDA"].isna().sum()
    )

    if fechas_principal_invalidas > 0:

        st.warning(
            f"⚠️ Hay {fechas_principal_invalidas} registros "
            "del archivo principal con FECHA inválida o vacía."
        )

    if fechas_secundario_invalidas > 0:

        st.warning(
            f"⚠️ Hay {fechas_secundario_invalidas} registros "
            "del archivo secundario con FECHA DE ATENCION "
            "inválida o vacía."
        )


    # =====================================================
    # CREAR TABLA DE CRUCE
    # =====================================================

    tabla_cruce = df_secundario[
        [
            "_RUN_BUSQUEDA",
            "_FECHA_BUSQUEDA",
            columna_sexo,
            columna_prevision,
            columna_modalidad
        ]
    ].copy()


    # =====================================================
    # ELIMINAR RUT O FECHA VACÍOS
    # =====================================================

    tabla_cruce = tabla_cruce[
        (tabla_cruce["_RUN_BUSQUEDA"] != "") &
        (tabla_cruce["_FECHA_BUSQUEDA"].notna())
    ]


    # =====================================================
    # ELIMINAR DUPLICADOS
    # =====================================================

    tabla_cruce = tabla_cruce.drop_duplicates(
        subset=[
            "_RUN_BUSQUEDA",
            "_FECHA_BUSQUEDA"
        ],
        keep="first"
    )


    # =====================================================
    # CREAR DICCIONARIOS
    # =====================================================

    diccionario_sexo = dict(
        zip(
            zip(
                tabla_cruce["_RUN_BUSQUEDA"],
                tabla_cruce["_FECHA_BUSQUEDA"]
            ),
            tabla_cruce[columna_sexo]
        )
    )

    diccionario_prevision = dict(
        zip(
            zip(
                tabla_cruce["_RUN_BUSQUEDA"],
                tabla_cruce["_FECHA_BUSQUEDA"]
            ),
            tabla_cruce[columna_prevision]
        )
    )

    diccionario_modalidad = dict(
        zip(
            zip(
                tabla_cruce["_RUN_BUSQUEDA"],
                tabla_cruce["_FECHA_BUSQUEDA"]
            ),
            tabla_cruce[columna_modalidad]
        )
    )


    # =====================================================
    # CREAR CLAVE DE CRUCE EN PRINCIPAL
    # =====================================================

    claves_principal = list(
        zip(
            df_principal["_RUT_BUSQUEDA"],
            df_principal["_FECHA_BUSQUEDA"]
        )
    )


    # =====================================================
    # AGREGAR SEXO
    # =====================================================

    df_principal["Sexo"] = [
        diccionario_sexo.get(clave, "No encontrado")
        for clave in claves_principal
    ]


    # =====================================================
    # AGREGAR PREVISIÓN
    # =====================================================

    df_principal["PREVISIÓN"] = [
        diccionario_prevision.get(clave, "No encontrado")
        for clave in claves_principal
    ]


    # =====================================================
    # AGREGAR MODALIDAD DE ATENCIÓN
    # =====================================================

    df_principal["MODALIDAD DE ATENCIÓN"] = [
        diccionario_modalidad.get(clave, "No encontrado")
        for clave in claves_principal
    ]


    # =====================================================
    # NORMALIZAR RESULTADOS
    # =====================================================

    df_principal["Sexo"] = (
        df_principal["Sexo"]
        .fillna("No encontrado")
        .astype(str)
        .str.strip()
    )

    df_principal["PREVISIÓN"] = (
        df_principal["PREVISIÓN"]
        .fillna("No encontrado")
        .astype(str)
        .str.strip()
    )

    df_principal["MODALIDAD DE ATENCIÓN"] = (
        df_principal["MODALIDAD DE ATENCIÓN"]
        .fillna("No encontrado")
        .astype(str)
        .str.strip()
    )


    # =====================================================
    # ELIMINAR COLUMNAS AUXILIARES
    # =====================================================

    df_principal.drop(
        columns=[
            "_RUT_BUSQUEDA",
            "_FECHA_BUSQUEDA"
        ],
        inplace=True
    )


    # =====================================================
    # RESULTADOS
    # =====================================================

    total = len(df_principal)

    sexo_encontrado = (
        df_principal["Sexo"] != "No encontrado"
    ).sum()

    prevision_encontrada = (
        df_principal["PREVISIÓN"] != "No encontrado"
    ).sum()

    modalidad_encontrada = (
        df_principal["MODALIDAD DE ATENCIÓN"]
        != "No encontrado"
    ).sum()


    st.subheader("📊 Resultado")


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Registros principales",
            total
        )


    with col2:

        st.metric(
            "Sexo encontrado",
            sexo_encontrado
        )


    with col3:

        st.metric(
            "Previsión encontrada",
            prevision_encontrada
        )


    with col4:

        st.metric(
            "Modalidad encontrada",
            modalidad_encontrada
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
            file_name="resultado_con_sexo_prevision_modalidad.xlsx",
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

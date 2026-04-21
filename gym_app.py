import streamlit as st
import json
import os
import random

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gym Pro AI", page_icon="💪", layout="wide")
DB_FILE = "gym_data.json"

# --- PERSISTENCIA ---
def guardar_todo(datos):
    with open(DB_FILE, "w", encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

def cargar_todo():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return {"perfil_completado": False, "user": {}, "rutina_semanal": {}}

if 'data' not in st.session_state:
    st.session_state.data = cargar_todo()

# --- LÓGICA DE CÁLCULOS SALUDABLES ---
def obtener_analisis(peso_lb, estatura_m):
    peso_kg = peso_lb * 0.453592
    imc = round(peso_kg / (estatura_m**2), 1)
    
    if imc < 18.5: estado = "Bajo peso"
    elif 18.5 <= imc <= 24.9: estado = "Peso normal"
    elif 25.0 <= imc <= 29.9: estado = "Sobrepeso"
    else: estado = "Obesidad"
    
    p_min = round(18.5 * (estatura_m**2) / 0.453592, 1)
    p_max = round(24.9 * (estatura_m**2) / 0.453592, 1)
    
    return imc, estado, p_min, p_max

# --- MOTOR DE RUTINA ---
def generar_rutina_ia(objetivos, peso_lb):
    ejercicios_db = {
        "Pecho": ["Press de Banca", "Aperturas con mancuernas"],
        "Espalda": ["Remo con barra", "Jalón al pecho"],
        "Piernas": ["Sentadillas", "Prensa"],
        "Hombros": ["Press Militar", "Elevaciones laterales"],
        "Brazos": ["Curl de Bíceps", "Copa de Tríceps"],
        "Cardio": ["Caminata Inclinada", "Bicicleta"],
        "Abdomen": ["Plancha", "Crunches"]
    }
    distribucion = {"Lunes": ["Pecho", "Brazos"], "Martes": ["Piernas"], "Miércoles": ["Descanso"], "Jueves": ["Espalda", "Hombros"], "Viernes": ["Cardio", "Abdomen"]}
    
    rutina = {}
    es_hipertrofia = any("masa" in obj.lower() or "fuerza" in obj.lower() for obj in objetivos)
    series = 4 if es_hipertrofia else 3
    reps = "8-12" if es_hipertrofia else "15-20"

    for dia, grupos in distribucion.items():
        if dia == "Miércoles":
            rutina[dia] = "Descanso activo o estiramientos"
        else:
            ej_dia = []
            for g in grupos:
                for e in ejercicios_db.get(g, []):
                    libras = round(peso_lb * random.uniform(0.2, 0.4), 0)
                    ej_dia.append({"ejercicio": e, "grupo": g, "series": series, "reps": reps, "libras": libras})
            rutina[dia] = ej_dia
    return rutina

# --- REGISTRO INICIAL ---
if not st.session_state.data.get("perfil_completado", False):
    st.title("👋 Configuración de Perfil")
    with st.form("registro"):
        nombre = st.text_input("Nombre")
        peso = st.number_input("Peso (Lbs)", 50.0, 500.0, 160.0)
        c1, c2 = st.columns(2)
        pies = c1.number_input("Pies", 3, 8, 5)
        pulgadas = c2.number_input("Pulgadas", 0, 11, 7)
        objs = st.multiselect("Objetivos", ["Ganar masa muscular", "Perder grasa", "Aumentar fuerza", "Tonificar"])
        
        if st.form_submit_button("Guardar y Ver Resultados"):
            est_m = ((pies * 12) + pulgadas) * 0.0254
            st.session_state.data["user"] = {"nombre": nombre, "peso_lb": peso, "pies": pies, "pulgadas": pulgadas, "estatura_m": est_m, "objetivos": objs}
            st.session_state.data["perfil_completado"] = True
            st.session_state.data["rutina_semanal"] = generar_rutina_ia(objs, peso)
            guardar_todo(st.session_state.data)
            st.rerun()

# --- PANEL PRINCIPAL ---
else:
    u = st.session_state.data["user"]
    imc, estado, p_min, p_max = obtener_analisis(u['peso_lb'], u['estatura_m'])

    st.title(f"Panel de {u['nombre']}")
    
    # MOSTRAR SIEMPRE EL ANÁLISIS DE SALUD ARRIBA
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        c1.metric("Tu IMC", imc)
        c2.metric("Estado", estado)
        c3.info(f"⚖️ Peso ideal: {p_min} - {p_max} lbs")

    tab_rutina, tab_perfil = st.tabs(["📅 Mi Rutina", "👤 Editar Perfil"])

    with tab_rutina:
        st.subheader("Plan Semanal Personalizado")
        rutina = st.session_state.data.get("rutina_semanal", {})
        for dia, contenido in rutina.items():
            with st.expander(f"📍 {dia.upper()}"):
                if isinstance(contenido, str): st.write(contenido)
                else:
                    for i, ej in enumerate(contenido):
                        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                        rutina[dia][i]['ejercicio'] = col1.text_input("Ejercicio", ej['ejercicio'], key=f"e_{dia}_{i}")
                        rutina[dia][i]['series'] = col2.number_input("Series", 1, 10, int(ej['series']), key=f"s_{dia}_{i}")
                        rutina[dia][i]['reps'] = col3.text_input("Reps", ej['reps'], key=f"r_{dia}_{i}")
                        rutina[dia][i]['libras'] = col4.number_input("Lbs", 0.0, 1000.0, float(ej['libras']), key=f"l_{dia}_{i}")
        if st.button("💾 Guardar Cambios en Rutina"):
            st.session_state.data["rutina_semanal"] = rutina
            guardar_todo(st.session_state.data)
            st.success("Rutina actualizada.")

    with tab_perfil:
        with st.form("edit_perfil"):
            n_nombre = st.text_input("Nombre", u['nombre'])
            n_peso = st.number_input("Peso (Lbs)", value=float(u['peso_lb']))
            c1, c2 = st.columns(2)
            n_pies = c1.number_input("Pies", 3, 8, value=int(u['pies']))
            n_pulgadas = c2.number_input("Pulgadas", 0, 11, value=int(u['pulgadas']))
            n_objs = st.multiselect("Objetivos", ["Ganar masa muscular", "Perder grasa", "Aumentar fuerza", "Tonificar"], default=u['objetivos'])
            
            if st.form_submit_button("Actualizar Datos y Recalcular IMC"):
                est_m = ((n_pies * 12) + n_pulgadas) * 0.0254
                st.session_state.data["user"] = {"nombre": n_nombre, "peso_lb": n_peso, "pies": n_pies, "pulgadas": n_pulgadas, "estatura_m": est_m, "objetivos": n_objs}
                guardar_todo(st.session_state.data)
                st.rerun()

    if st.sidebar.button("Reiniciar App"):
        st.session_state.data = {"perfil_completado": False, "user": {}, "rutina_semanal": {}}
        guardar_todo(st.session_state.data)
        st.rerun()

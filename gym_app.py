import streamlit as st
import json
import os
import random

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gym Pro AI", page_icon="💪", layout="wide")
DB_FILE = "gym_data.json"

# --- LISTA MAESTRA DE OBJETIVOS (PROTEGIDA) ---
LISTA_OBJETIVOS = [
    "🏋️ Ganar masa muscular (hipertrofia)",
    "🏋️ Perder grasa corporal",
    "🏋️ Aumentar fuerza (ej. mejorar en ejercicios clave)",
    "🏋️ Mejorar resistencia cardiovascular",
    "🏋️ Tonificar el cuerpo",
    "🏋️ Mejorar la movilidad y flexibilidad",
    "❤️ Reducir el estrés",
    "❤️ Dormir mejor",
    "❤️ Mejorar la salud cardiovascular",
    "❤️ Prevenir lesiones o dolores",
    "❤️ Aumentar niveles de energía diarios",
    "⚡ Correr más rápido o más distancia",
    "⚡ Saltar más alto o mejorar potencia",
    "⚡ Prepararse para un deporte específico",
    "⚡ Mejorar coordinación y equilibrio",
    "🎯 Marcar abdomen",
    "🎯 Aumentar glúteos o piernas",
    "🎯 Definir brazos y hombros",
    "🎯 Mejorar postura corporal",
    "🧠 Crear una rutina constante",
    "🧠 Aprender técnica correcta de ejercicios",
    "🧠 Mantener consistencia a largo plazo",
    "🧠 Desarrollar disciplina y autocontrol",
    "📊 Bajar peso en tiempo específico",
    "📊 Levantar cierto peso en ejercicios clave",
    "📊 Reducir porcentaje de grasa corporal",
    "📊 Completar metas de cardio"
]

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

# --- LÓGICA DE SALUD ---
def obtener_analisis(peso_lb, estatura_m):
    if estatura_m <= 0: return 0, "N/A", 0, 0
    peso_kg = peso_lb * 0.453592
    imc = round(peso_kg / (estatura_m**2), 1)
    
    if imc < 18.5: estado = "Bajo peso"
    elif 18.5 <= imc <= 24.9: estado = "Peso normal"
    elif 25.0 <= imc <= 29.9: estado = "Sobrepeso"
    else: estado = "Obesidad"
    
    p_min = round(18.5 * (estatura_m**2) / 0.453592, 1)
    p_max = round(24.9 * (estatura_m**2) / 0.453592, 1)
    
    return imc, estado, p_min, p_max

# --- MOTOR DE RUTINA IA ---
def generar_rutina_ia(objetivos, peso_lb):
    # Lógica de intensidad basada en objetivos físicos o estéticos
    es_intenso = any("masa" in obj.lower() or "fuerza" in obj.lower() or "glúteos" in obj.lower() for obj in objetivos)
    series = 4 if es_intenso else 3
    reps = "8-12" if es_intenso else "12-15"
    
    ejercicios_db = {
        "Pecho/Hombros": ["Press de Banca", "Press Militar", "Aperturas"],
        "Espalda/Brazos": ["Remo con barra", "Jalón al pecho", "Curl de Bíceps"],
        "Piernas": ["Sentadillas", "Prensa", "Peso Muerto Rumano"],
        "Funcional/Cardio": ["Burpees", "Caminata Inclinada", "Plancha"]
    }
    
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    rutina = {}
    
    distribucion = {
        "Lunes": "Pecho/Hombros",
        "Martes": "Piernas",
        "Miércoles": "Descanso activo",
        "Jueves": "Espalda/Brazos",
        "Viernes": "Funcional/Cardio"
    }

    for dia, enfoque in distribucion.items():
        if "Descanso" in enfoque:
            rutina[dia] = "Día de recuperación: Estiramientos o caminata ligera."
        else:
            ej_dia = []
            for e in ejercicios_db.get(enfoque, []):
                # Peso sugerido basado en el 30% del peso corporal como base
                libras = round(peso_lb * random.uniform(0.25, 0.45), 0)
                ej_dia.append({"ejercicio": e, "series": series, "reps": reps, "libras": libras})
            rutina[dia] = ej_dia
    return rutina

# --- INTERFAZ ---
if not st.session_state.data.get("perfil_completado", False):
    st.title("👋 Bienvenido a tu Gym Pro AI")
    with st.form("registro_inicial"):
        nombre = st.text_input("¿Cuál es tu nombre?")
        c_p, c_ft, c_in = st.columns(3)
        peso = c_p.number_input("Peso (Lbs)", 50.0, 500.0, 160.0)
        pies = c_ft.number_input("Pies", 3, 8, 5)
        pulgadas = c_in.number_input("Pulgadas", 0, 11, 7)
        
        st.write("### 🎯 Selecciona tus objetivos")
        objs = st.multiselect("Puedes elegir todos los que apliquen:", LISTA_OBJETIVOS)
        
        if st.form_submit_button("Guardar Perfil y Generar Mi Rutina"):
            if nombre and objs:
                est_m = ((pies * 12) + pulgadas) * 0.0254
                st.session_state.data["user"] = {
                    "nombre": nombre, "peso_lb": peso, "pies": pies, 
                    "pulgadas": pulgadas, "estatura_m": est_m, "objetivos": objs
                }
                st.session_state.data["perfil_completado"] = True
                st.session_state.data["rutina_semanal"] = generar_rutina_ia(objs, peso)
                guardar_todo(st.session_state.data)
                st.rerun()
            else:
                st.warning("Por favor completa tu nombre y elige al menos un objetivo.")

else:
    u = st.session_state.data.get("user", {})
    imc, estado, p_min, p_max = obtener_analisis(u.get('peso_lb', 160), u.get('estatura_m', 1.70))
    
    st.title(f"Panel de Control: {u.get('nombre')}")
    
    # Métrica de Salud Siempre Visible
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        c1.metric("IMC Actual", imc)
        c2.metric("Estado Físico", estado)
        c3.success(f"⚖️ Rango de Peso Ideal: {p_min} - {p_max} lbs")

    t_rutina, t_perfil = st.tabs(["📅 Mi Rutina Recomendada", "👤 Configuración de Perfil"])

    with t_rutina:
        st.subheader("Tu Plan de Entrenamiento")
        rutina = st.session_state.data.get("rutina_semanal", {})
        for dia, ejercicios in rutina.items():
            with st.expander(f"📌 {dia.upper()}", expanded=(dia=="Lunes")):
                if isinstance(ejercicios, str):
                    st.info(ejercicios)
                else:
                    for i, ej in enumerate(ejercicios):
                        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                        # Permitir edición inmediata
                        rutina[dia][i]['ejercicio'] = c1.text_input("Ejercicio", ej['ejercicio'], key=f"e_{dia}_{i}")
                        rutina[dia][i]['series'] = c2.number_input("Series", 1, 10, int(ej['series']), key=f"s_{dia}_{i}")
                        rutina[dia][i]['reps'] = c3.text_input("Reps", ej['reps'], key=f"r_{dia}_{i}")
                        rutina[dia][i]['libras'] = c4.number_input("Lbs", 0.0, 1000.0, float(ej['libras']), key=f"l_{dia}_{i}")
        
        if st.button("💾 Guardar Cambios en la Rutina"):
            st.session_state.data["rutina_semanal"] = rutina
            guardar_todo(st.session_state.data)
            st.toast("¡Cambios guardados!", icon="✅")

    with t_perfil:
        st.subheader("Editar Datos Personales")
        with st.form("edit_perfil"):
            n_nombre = st.text_input("Nombre", u.get('nombre'))
            n_peso = st.number_input("Peso (Lbs)", value=float(u.get('peso_lb')))
            c_f, c_i = st.columns(2)
            n_pies = c_f.number_input("Pies", 3, 8, value=int(u.get('pies')))
            n_pulgadas = c_i.number_input("Pulgadas", 0, 11, value=int(u.get('pulgadas')))
            
            # Filtro de seguridad para los objetivos seleccionados
            objs_actuales = [o for o in u.get('objetivos', []) if o in LISTA_OBJETIVOS]
            n_objs = st.multiselect("Mis Objetivos", LISTA_OBJETIVOS, default=objs_actuales)
            
            if st.form_submit_button("Actualizar mi Perfil"):
                est_m = ((n_pies * 12) + n_pulgadas) * 0.0254
                st.session_state.data["user"] = {
                    "nombre": n_nombre, "peso_lb": n_peso, "pies": n_pies, 
                    "pulgadas": n_pulgadas, "estatura_m": est_m, "objetivos": n_objs
                }
                guardar_todo(st.session_state.data)
                st.rerun()

    if st.sidebar.button("⚠️ Reiniciar App"):
        st.session_state.data = {"perfil_completado": False, "user": {}, "rutina_semanal": {}}
        guardar_todo(st.session_state.data)
        st.rerun()

import streamlit as st
import json
import os
import random

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gym Pro AI", page_icon="💪", layout="wide")
DB_FILE = "gym_data.json"

# Cargar CSS
if os.path.exists("style.css"):
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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
                data = json.load(f)
                # Asegurar compatibilidad con versiones anteriores
                if "historial_pesos" not in data:
                    data["historial_pesos"] = []
                return data
        except: pass
    return {"perfil_completado": False, "user": {}, "rutina_semanal": {}, "historial_pesos": []}

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

# --- LÓGICA NUTRICIONAL ---
def calcular_macros(u):
    peso_kg = u.get('peso_lb', 160) * 0.453592
    estatura_cm = u.get('estatura_m', 1.70) * 100
    edad = u.get('edad', 25)
    
    # BMR (Mifflin-St Jeor para hombres como base, ajustable)
    bmr = (10 * peso_kg) + (6.25 * estatura_cm) - (5 * edad) + 5
    tdee = bmr * 1.4 # Nivel de actividad moderado
    
    objetivos = u.get('objetivos', [])
    target = tdee
    if any("perder grasa" in obj.lower() or "bajar peso" in obj.lower() for obj in objetivos):
        target = tdee * 0.8 # Déficit 20%
    elif any("ganar masa" in obj.lower() or "aumentar fuerza" in obj.lower() for obj in objetivos):
        target = tdee * 1.1 # Superávit 10%
        
    prot = peso_kg * 2.0 # 2g por kg
    grasas = peso_kg * 0.8
    carbs = (target - (prot * 4) - (grasas * 9)) / 4
    
    return round(target), round(prot), round(grasas), round(carbs)

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
    st.markdown('<h1 class="main-header">💪 Gym Pro AI</h1>', unsafe_allow_html=True)
    st.markdown("### Bienvenido. Vamos a construir tu mejor versión.")
    
    with st.form("registro_inicial"):
        st.markdown("#### 👤 Datos Personales")
        nombre = st.text_input("¿Cuál es tu nombre?")
        
        st.markdown("#### 📏 Medidas y Edad")
        c_p, c_ft, c_in, c_ed = st.columns(4)
        peso = c_p.number_input("Peso (Lbs)", 50.0, 500.0, 160.0)
        pies = c_ft.number_input("Pies", 3, 8, 5)
        pulgadas = c_in.number_input("Pulgadas", 0, 11, 7)
        edad = c_ed.number_input("Edad", 12, 100, 25)
        
        st.markdown("#### 🎯 Objetivos de Entrenamiento")
        objs = st.multiselect("Selecciona tus metas:", LISTA_OBJETIVOS)
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("🚀 Generar Mi Plan Inteligente", use_container_width=True)
        
        if submit:
            if nombre and objs:
                est_m = ((pies * 12) + pulgadas) * 0.0254
                st.session_state.data["user"] = {
                    "nombre": nombre, "peso_lb": peso, "pies": pies, 
                    "pulgadas": pulgadas, "estatura_m": est_m, "objetivos": objs,
                    "edad": edad
                }
                st.session_state.data["perfil_completado"] = True
                st.session_state.data["rutina_semanal"] = generar_rutina_ia(objs, peso)
                guardar_todo(st.session_state.data)
                st.rerun()
            else:
                st.warning("⚠️ Completa tu nombre y elige al menos un objetivo para continuar.")

else:
    u = st.session_state.data.get("user", {})
    imc, estado, p_min, p_max = obtener_analisis(u.get('peso_lb', 160), u.get('estatura_m', 1.70))
    
    # --- SIDEBAR PREMIUN ---
    with st.sidebar:
        st.markdown(f"""
            <div style="text-align: center; padding: 20px 0;">
                <h2 style="margin:0;">💪 Gym Pro AI</h2>
                <p style="color: grey;">Tu Entrenador Personal Inteligente</p>
            </div>
            <hr style="margin: 10px 0; border: 0.1px solid rgba(255,255,255,0.1);">
            <p class="sidebar-label">Perfil de Usuario</p>
            <h3>👤 {u.get('nombre')}</h3>
            <p>🎂 Edad: {u.get('edad', 'N/A')} años</p>
            <p>🎯 {u.get('objetivos')[0] if u.get('objetivos') else 'Sin objetivos'}</p>
        """, unsafe_allow_html=True)
        st.info(f"📍 Meta: {len(u.get('objetivos', []))} objetivos seleccionados.")
        
        if st.button("⚠️ Reiniciar App", use_container_width=True):
            st.session_state.data = {"perfil_completado": False, "user": {}, "rutina_semanal": {}}
            guardar_todo(st.session_state.data)
            st.rerun()

    # --- DASHBOARD PRINCIPAL ---
    st.markdown(f'<h1 class="main-header">Panel de Control: {u.get("nombre")}</h1>', unsafe_allow_html=True)
    
    # Métrica de Salud Siempre Visible
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("IMC Actual", imc, help="Índice de Masa Corporal")
    with c2:
        st.metric("Estado Físico", estado)
    with c3:
        st.metric("Peso Ideal (Lbs)", f"{p_min} - {p_max}")

    t_rutina, t_progreso, t_perfil = st.tabs(["📅 Mi Rutina", "📈 Mi Progreso", "👤 Perfil"])

    with t_rutina:
        st.markdown("### 🏋️ Tu Plan de Entrenamiento Personalizado")
        rutina = st.session_state.data.get("rutina_semanal", {})
        for dia, ejercicios in rutina.items():
            with st.expander(f"📅 {dia.upper()}", expanded=(dia=="Lunes")):
                if isinstance(ejercicios, str):
                    st.info(ejercicios)
                else:
                    for i, ej in enumerate(ejercicios):
                        st.markdown(f"""
                            <div class="exercise-card">
                                <strong>{ej['ejercicio']}</strong><br>
                                <small>Configuración actual: {ej['series']} series x {ej['reps']} reps @ {ej['libras']} lbs</small>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                        rutina[dia][i]['ejercicio'] = c1.text_input("Ejercicio", ej['ejercicio'], key=f"e_{dia}_{i}", label_visibility="collapsed")
                        rutina[dia][i]['series'] = c2.number_input("Sets", 1, 10, int(ej['series']), key=f"s_{dia}_{i}")
                        rutina[dia][i]['reps'] = c3.text_input("Reps", ej['reps'], key=f"r_{dia}_{i}")
                        rutina[dia][i]['libras'] = c4.number_input("Lbs", 0.0, 1000.0, float(ej['libras']), key=f"l_{dia}_{i}")
        
        if st.button("💾 Guardar Cambios en la Rutina"):
            st.session_state.data["rutina_semanal"] = rutina
            guardar_todo(st.session_state.data)
            st.toast("¡Cambios guardados!", icon="✅")

    with t_progreso:
        st.markdown("### 📊 Evolución y Análisis Nutricional")
        
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.markdown("#### ⚖️ Registrar Peso")
            with st.form("log_peso"):
                n_p = st.number_input("Peso de hoy (Lbs)", 50.0, 500.0, float(u.get('peso_lb')))
                if st.form_submit_button("Anotar Peso"):
                    from datetime import date
                    hoy = str(date.today())
                    st.session_state.data["historial_pesos"].append({"fecha": hoy, "peso": n_p})
                    st.session_state.data["user"]["peso_lb"] = n_p # Actualizar peso actual
                    guardar_todo(st.session_state.data)
                    st.success(f"¡Peso de {n_p} lbs registrado!")
                    st.rerun()
            
            # Cálculo de macros
            cal, p, g, c = calcular_macros(u)
            st.markdown(f"""
                <div class="exercise-card" style="border-left-color: var(--secondary);">
                    <h4 style="margin:0;">🔥 Calorías Objetivo</h4>
                    <h2 style="margin:0; color: var(--secondary);">{cal} kcal</h2>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"**Macros Directriz:**")
            st.write(f"🥩 Proteína: {p}g")
            st.write(f"🍞 Carbos: {c}g")
            st.write(f"🥑 Grasas: {g}g")

        with c2:
            st.markdown("#### 📉 Tendencia de Peso")
            historial = st.session_state.data.get("historial_pesos", [])
            if historial:
                import pandas as pd
                df = pd.DataFrame(historial)
                df['fecha'] = pd.to_datetime(df['fecha'])
                st.line_chart(df.set_index('fecha')['peso'])
            else:
                st.info("Aún no tienes registros de peso. ¡Empieza hoy!")

    with t_perfil:
        st.markdown("### ⚙️ Configuración de Perfil")
        with st.form("edit_perfil"):
            st.markdown("#### 👤 Información Personal")
            n_nombre = st.text_input("Nombre", u.get('nombre'))
            
            st.markdown("#### 📏 Medidas y Edad")
            n_peso = st.number_input("Peso (Lbs)", value=float(u.get('peso_lb')))
            c_f, c_i, c_e = st.columns(3)
            n_pies = c_f.number_input("Pies", 3, 8, value=int(u.get('pies')))
            n_pulgadas = c_i.number_input("Pulgadas", 0, 11, value=int(u.get('pulgadas')))
            n_edad = c_e.number_input("Edad", 12, 100, value=int(u.get('edad', 25)))
            
            st.markdown("#### 🎯 Mis Objetivos")
            objs_actuales = [o for o in u.get('objetivos', []) if o in LISTA_OBJETIVOS]
            n_objs = st.multiselect("Editar objetivos:", LISTA_OBJETIVOS, default=objs_actuales)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("✅ Actualizar mi Perfil", use_container_width=True):
                est_m = ((n_pies * 12) + n_pulgadas) * 0.0254
                st.session_state.data["user"] = {
                    "nombre": n_nombre, "peso_lb": n_peso, "pies": n_pies, 
                    "pulgadas": n_pulgadas, "estatura_m": est_m, "objetivos": n_objs,
                    "edad": n_edad
                }
                guardar_todo(st.session_state.data)
                st.rerun()

    if st.sidebar.button("⚠️ Reiniciar App"):
        st.session_state.data = {"perfil_completado": False, "user": {}, "rutina_semanal": {}}
        guardar_todo(st.session_state.data)
        st.rerun()

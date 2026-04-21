import streamlit as st
import pandas as pd
import json
import os
import time
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(page_title="Gym Pro AI", layout="centered", page_icon="💪")

# --- LÓGICA DE PERSISTENCIA ---
DB_FILE = "gym_data.json"

def guardar_todo(datos):
    with open(DB_FILE, "w") as f:
        json.dump(datos, f)

def cargar_todo():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {
        "perfil_completado": False, 
        "user": {}, 
        "rutinas": [],
        "medidas": [],
        "biblioteca_personal": {
            "Press de Banca": "Pecho", "Sentadillas": "Piernas", 
            "Peso Muerto": "Espalda", "Caminata Inclinada": "Cardio",
            "Press Militar": "Hombros", "Cur de Bíceps": "Brazos"
        }
    }

if 'data' not in st.session_state:
    st.session_state.data = cargar_todo()

# --- EXTRACCIÓN SEGURA DE DATOS ---
user_data = st.session_state.data.get("user", {})
u_nombre = user_data.get("nombre", "Usuario")
u_edad = user_data.get("edad", 25)
u_imc = user_data.get("imc", 0)
u_peso = user_data.get("peso", 160.0)
u_estatura = user_data.get("estatura_m", 1.70)
u_p_max = user_data.get("p_max_lb", 0)
u_objetivos = user_data.get("objetivos", ["Mantener peso"])

# --- PANTALLA DE BIENVENIDA ---
if not st.session_state.data.get("perfil_completado", False):
    st.title("👋 ¡Bienvenido a Gym Pro AI!")
    if st.button("Configurar mi Perfil ahora"):
        st.session_state.data["perfil_completado"] = True 
        guardar_todo(st.session_state.data)
        st.rerun()

# --- PANEL PRINCIPAL ---
else:
    st.title(f"Gym Pro AI - {u_nombre}")
    
    tabs = st.tabs(["📅 Rutina", "📊 Progreso", "🔮 Super IA", "🏆 Logros", "👤 Perfil"])
    tab1, tab2, tab3, tab4, tab5 = tabs

    # --- TAB 1: RUTINA (CON CALCULADORA Y TIMER INTEGRADO) ---
    with tab1:
        st.header("Entrenamiento Activo")
        
        biblioteca = st.session_state.data.get("biblioteca_personal", {})
        ej_actual = st.selectbox("🎯 Ejercicio actual:", list(biblioteca.keys()))
        
        col_info, col_timer = st.columns([2, 1])
        with col_info:
            st.info(f"Enfoque: **{ej_actual}**")
        with col_timer:
            # Timer siempre visible para uso rápido entre series
            with st.popover("⏱️ Timer Descanso"):
                t_desc = st.select_slider("Segundos", options=[30, 45, 60, 90, 120, 180], value=90)
                if st.button("▶️ Iniciar"):
                    placeholder = st.empty()
                    for t in range(t_desc, -1, -1):
                        placeholder.metric("Descansando...", f"{t}s")
                        time.sleep(1)
                    st.balloons()
                    st.success("¡Dale!")

        st.divider()

        # Calculadora de Discos / Mancuernas
        with st.expander("⚖️ Calculadora de Carga (Discos/Mancuernas)"):
            p_obj = st.number_input("Peso total objetivo (lbs)", 5, 1000, 135)
            tipo_carga = st.radio("Tipo de equipo:", ["Barra Olímpica (45lb)", "Mancuernas / Barra Z"], horizontal=True)
            
            if "Barra Olímpica" in tipo_carga:
                peso_lado = (p_obj - 45) / 2
                if peso_lado < 0: st.warning("El peso es menor a la barra solo.")
                else:
                    discos = [45, 35, 25, 10, 5, 2.5]
                    res = []
                    for d in discos:
                        cant = int(peso_lado // d)
                        if cant > 0: res.append(f"{cant}x{d}lb"); peso_lado -= cant * d
                    st.write("**Cargar en cada lado:** " + (", ".join(res) if res else "Barra sola"))
            else:
                st.write(f"Utiliza un par de mancuernas de **{p_obj/2 if p_obj > 1 else p_obj} lbs** cada una.")

        # Registro de Series
        if biblioteca.get(ej_actual) == "Cardio":
            c1, c2 = st.columns(2)
            m_c = c1.number_input("Minutos", 1, 300, 30)
            i_c = c2.number_input("Inclinación", 0.0, 20.0, 10.0)
            if st.button(f"✅ Registrar Cardio"):
                st.session_state.data["rutinas"].append({
                    "fecha": str(datetime.now().date()), "ejercicio": ej_actual, 
                    "es_cardio": True, "minutos": m_c, "inclinacion": i_c
                })
                guardar_todo(st.session_state.data); st.success("¡Cardio guardado!"); st.rerun()
        else:
            n_s = st.number_input("Número de Series", 1, 10, 3)
            detalles_temp = []
            cols_s = st.columns(min(n_s, 5))
            for i in range(n_s):
                with cols_s[i % 5]:
                    r = st.number_input(f"R{i+1}", 1, 50, 10, key=f"r_{i}_{ej_actual}")
                    p = st.number_input(f"Lb{i+1}", 0.0, 1000.0, 45.0, key=f"p_{i}_{ej_actual}")
                    detalles_temp.append({"serie": i+1, "reps": r, "peso": p})
            
            if st.button(f"➕ Guardar Entrenamiento de {ej_actual}"):
                st.session_state.data["rutinas"].append({
                    "fecha": str(datetime.now().date()), "ejercicio": ej_actual, 
                    "grupo": biblioteca.get(ej_actual), "detalles": detalles_temp
                })
                guardar_todo(st.session_state.data)
                st.toast(f"¡{ej_actual} guardado!", icon="💪")

    # --- TAB 2: PROGRESO ---
    with tab2:
        st.header("Historial")
        hist = st.session_state.data.get("rutinas", [])
        if hist:
            for item in reversed(hist[-10:]):
                with st.container(border=True):
                    f = item.get("fecha", "S/F")
                    e = item.get("ejercicio", "S/E")
                    st.write(f"📅 {f} - **{e}**")
                    if not item.get("es_cardio"):
                        st.caption(" | ".join([f"{s.get('reps')}x{s.get('peso')}lb" for s in item.get("detalles", [])]))
        else: st.info("No hay registros.")

    # --- TAB 3: SUPER IA ---
    with tab3:
        st.header("🔮 Super IA: Análisis")
        pk = u_peso * 0.453592
        acm = u_estatura * 100
        grasa = (1.20 * u_imc) + (0.23 * u_edad) - 16.2
        tmb = (10 * pk) + (6.25 * acm) - (5 * u_edad) + 5
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Grasa Est.", f"{max(grasa, 5):.1f}%")
        c2.metric("Agua/Día", f"{(u_peso * 0.6) / 33.8:.1f} L")
        c3.metric("TMB", f"{tmb:.0f} kcal")

        rutinas_ia = st.session_state.data.get("rutinas", [])
        if rutinas_ia:
            fuerza = {}
            for r in rutinas_ia:
                if not r.get("es_cardio") and "detalles" in r:
                    best = max(r['detalles'], key=lambda x: x.get('peso', 0))
                    if 1 < best.get('reps', 0) <= 12:
                        rm = best['peso'] * (36 / (37 - best['reps']))
                        ej_n = r.get('ejercicio')
                        if ej_n not in fuerza or rm > fuerza[ej_n]: fuerza[ej_n] = rm
            if fuerza:
                st.subheader("Fuerza Máxima Estimada (1RM)")
                for e, v in fuerza.items(): st.write(f"💪 **{e}**: {v:.1f} lbs")

    # --- TAB 4: LOGROS ---
    with tab4:
        st.header("🏆 Logros")
        f_u = sorted(list(set([r.get("fecha") for r in st.session_state.data.get("rutinas", []) if r.get("fecha")])))
        racha = 0
        if f_u:
            hoy = datetime.now().date()
            while str(hoy) in f_u: racha += 1; hoy -= timedelta(days=1)
        st.metric("🔥 Racha Actual", f"{racha} Días")

    # --- TAB 5: PERFIL ---
    with tab5:
        st.header("👤 Perfil")
        with st.expander("Editar Datos"):
            ed_p = st.number_input("Peso (Lbs)", value=float(u_peso))
            opts = ["Bajar de peso", "Ganar Masa Muscular", "Tonificar", "Resistencia", "Fuerza Pura"]
            vals = [o for o in u_objetivos if o in opts]
            ed_o = st.multiselect("Objetivos", opts, default=vals)
            if st.button("Guardar Cambios"):
                st.session_state.data["user"]["peso"] = ed_p
                st.session_state.data["user"]["objetivos"] = ed_o
                guardar_todo(st.session_state.data); st.rerun()

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

# --- EXTRACCIÓN DE DATOS DEL USUARIO ---
user_data = st.session_state.data.get("user", {})
u_nombre = user_data.get("nombre", "Usuario")
u_edad = user_data.get("edad", 25)
u_imc = user_data.get("imc", 0)
u_peso = user_data.get("peso", 160.0)
u_estatura = user_data.get("estatura_m", 1.70)
u_p_max = user_data.get("p_max_lb", 0)
u_objetivos = user_data.get("objetivos", ["Mantener peso"])

# --- PANTALLA DE BIENVENIDA ---
if not st.session_state.data["perfil_completado"]:
    st.title("👋 ¡Bienvenido a Gym Pro AI!")
    st.write("Configura tu perfil para activar el análisis inteligente.")
    if st.button("Configurar mi Perfil ahora"):
        st.session_state.data["perfil_completado"] = True 
        guardar_todo(st.session_state.data)
        st.rerun()

# --- PANEL PRINCIPAL ---
else:
    st.title(f"Gym Pro AI - {u_nombre}")
    
    tabs = st.tabs(["📅 Rutina", "📊 Progreso", "🔮 Super IA", "🏆 Logros", "👤 Perfil"])
    tab1, tab2, tab3, tab4, tab5 = tabs

    # --- TAB 1: RUTINA (MODO ENFOQUE Y DESCANSO) ---
    with tab1:
        st.header("Entrenamiento Activo")
        
        # Selector de Ejercicio Actual
        biblioteca = st.session_state.data["biblioteca_personal"]
        ejercicios_lista = list(biblioteca.keys())
        
        col_ej, col_rest = st.columns([2, 1])
        
        with col_ej:
            ej_actual = st.selectbox("🎯 Ejercicio en ejecución:", ejercicios_lista, index=0)
            st.info(f"Trabajando ahora: **{ej_actual}** ({biblioteca.get(ej_actual)})")

        with col_rest:
            # Popover para configuración de descanso rápida
            with st.popover("⏱️ Timer"):
                t_descanso = st.select_slider("Segundos", options=[30, 45, 60, 90, 120, 180], value=90)
                if st.button("🔔 Iniciar"):
                    placeholder = st.empty()
                    for t in range(t_descanso, -1, -1):
                        placeholder.metric("Descansa...", f"{t}s")
                        time.sleep(1)
                    st.balloons()
                    st.success("¡Siguiente serie!")

        st.divider()

        # Registro de Series del Ejercicio Actual
        if biblioteca.get(ej_actual) == "Cardio":
            c1, c2 = st.columns(2)
            m_c = c1.number_input("Minutos", 1, 300, 30)
            i_c = c2.number_input("Inclinación", 0.0, 20.0, 10.0)
            if st.button(f"✅ Registrar {ej_actual}"):
                st.session_state.data["rutinas"].append({
                    "dia": "Hoy", 
                    "ejercicio": ej_actual, "grupo": "Cardio", 
                    "es_cardio": True, "minutos": m_c, "inclinacion": i_c, 
                    "fecha": str(datetime.now().date())
                })
                guardar_todo(st.session_state.data)
                st.success("Cardio guardado.")
        else:
            with st.expander("🧮 Calculadora de Discos"):
                p_obj = st.number_input("Peso total (lbs)", 45, 1000, 135, key="calc_disc_active")
                p_lado = (p_obj - 45) / 2
                if p_lado >= 0:
                    discs = [45, 35, 25, 10, 5, 2.5]
                    res = []
                    for d in discs:
                        cant = int(p_lado // d)
                        if cant > 0: res.append(f"{cant}x{d}lb"); p_lado -= cant * d
                    st.write("**En cada lado:** " + (", ".join(res) if res else "Barra sola"))

            n_series = st.number_input("Series", 1, 10, 3)
            detalles_series = []
            cols_s = st.columns(n_series)
            for i in range(n_series):
                with cols_s[i]:
                    r = st.number_input(f"R{i+1}", 1, 50, 10, key=f"r_act_{ej_actual}_{i}")
                    p = st.number_input(f"Lb{i+1}", 0.0, 1000.0, 45.0, key=f"p_act_{ej_actual}_{i}")
                    detalles_series.append({"serie": i+1, "reps": r, "peso": p})
            
            if st.button(f"➕ Guardar {ej_actual}"):
                st.session_state.data["rutinas"].append({
                    "dia": datetime.now().strftime("%A"), # Se traduce en la IA
                    "ejercicio": ej_actual, "grupo": biblioteca.get(ej_actual), 
                    "detalles": detalles_series, "fecha": str(datetime.now().date())
                })
                guardar_todo(st.session_state.data)
                st.toast(f"¡{ej_actual} registrado!", icon="💪")

    # --- TAB 2: PROGRESO ---
    with tab2:
        st.header("Historial y Medidas")
        with st.expander("📏 Registrar Medidas"):
            col1, col2 = st.columns(2)
            cint = col1.number_input("Cintura (cm)", 40.0, 150.0, 80.0)
            braz = col2.number_input("Brazo (cm)", 10.0, 70.0, 30.0)
            if st.button("Guardar Medidas"):
                st.session_state.data.setdefault("medidas", []).append({"fecha": str(datetime.now().date()), "cintura": cint, "brazo": braz})
                guardar_todo(st.session_state.data); st.rerun()

        hist = st.session_state.data.get("rutinas", [])
        if hist:
            for item in reversed(hist[-5:]):
                with st.container(border=True):
                    st.write(f"📅 {item['fecha']} - **{item['ejercicio']}**")
                    if not item.get("es_cardio"):
                        st.caption(" | ".join([f"{s['reps']}x{s['peso']}lb" for s in item['detalles']]))
        else: st.info("Sin registros aún.")

    # --- TAB 3: SUPER IA (PROTEGIDA) ---
    with tab3:
        st.header("🔮 Super IA: Análisis 360°")
        pk = u_peso * 0.453592
        acm = u_estatura * 100
        grasa = (1.20 * u_imc) + (0.23 * u_edad) - 16.2
        mm_kg = pk * (1 - (max(0, grasa)/100))
        tmb = (10 * pk) + (6.25 * acm) - (5 * u_edad) + 5
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Grasa Est.", f"{max(grasa, 5):.1f}%")
        m2.metric("Masa Magra", f"{mm_kg:.1f} kg")
        m3.metric("Agua/Día", f"{(u_peso * 0.6) / 33.8:.1f} L")
        m4.metric("TMB", f"{tmb:.0f} kcal")

        st.divider()
        rutinas_ia = st.session_state.data.get("rutinas", [])
        if rutinas_ia:
            st.subheader("📊 Análisis de Rendimiento")
            fuerza = {}
            vol_s = 0
            for r in rutinas_ia:
                if not r.get("es_cardio"):
                    vol_s += sum([s['reps'] * s['peso'] for s in r['detalles']])
                    best = max(r['detalles'], key=lambda x: x['peso'])
                    if 1 < best['reps'] <= 12:
                        rm = best['peso'] * (36 / (37 - best['reps']))
                        if r['ejercicio'] not in fuerza or rm > fuerza[r['ejercicio']]: fuerza[r['ejercicio']] = rm
            if fuerza:
                cols_f = st.columns(min(len(fuerza), 4))
                for i, (e, v) in enumerate(fuerza.items()): cols_f[i % 4].metric(e, f"{v:.1f} lb")
            st.write(f"📈 Volumen Semanal: {vol_s:.0f} lbs.")

    # --- TAB 4: LOGROS (PROTEGIDA) ---
    with tab4:
        st.header("🏆 Logros")
        f_u = sorted(list(set([r["fecha"] for r in st.session_state.data.get("rutinas", []) if "fecha" in r])))
        racha = 0
        if f_u:
            hoy = datetime.now().date()
            while str(hoy) in f_u: racha += 1; hoy -= timedelta(days=1)
        st.metric("🔥 Racha de Días", f"{racha}")
        
        st.subheader("🥇 Récords Personales")
        prs = {}
        for r in st.session_state.data.get("rutinas", []):
            if not r.get("es_cardio"):
                ej = r["ejercicio"]
                pm = max([s["peso"] for s in r["detalles"]])
                if ej not in prs or pm > prs[ej]: prs[ej] = pm
        for e, p in prs.items(): st.write(f"⭐ **{e}**: {p} lbs")

    # --- TAB 5: PERFIL (CON CORRECCIÓN DE MULTISELECT) ---
    with tab5:
        st.header("👤 Perfil")
        with st.expander("Editar Datos"):
            ed_p = st.number_input("Peso (Lbs)", value=float(u_peso))
            opts = ["Bajar de peso", "Ganar Masa Muscular", "Tonificar", "Resistencia", "Fuerza Pura"]
            vals = [o for o in u_objetivos if o in opts]
            ed_o = st.multiselect("Objetivos", opts, default=vals)
            if st.button("Guardar"):
                st.session_state.data["user"]["peso"] = ed_p
                st.session_state.data["user"]["objetivos"] = ed_o
                guardar_todo(st.session_state.data); st.rerun()

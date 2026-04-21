import streamlit as st
import pandas as pd
import json
import os
import time
from datetime import datetime, timedelta

# Configuración
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
            "Peso Muerto": "Espalda", "Caminata Inclinada": "Cardio"
        }
    }

if 'data' not in st.session_state:
    st.session_state.data = cargar_todo()

# --- EXTRACCIÓN DE DATOS ---
user_data = st.session_state.data.get("user", {})
u_nombre = user_data.get("nombre", "Usuario")
u_edad = user_data.get("edad", 25)
u_imc = user_data.get("imc", 0)
u_peso = user_data.get("peso", 160.0)
u_estatura = user_data.get("estatura_m", 1.70)
u_p_max = user_data.get("p_max_lb", 0)

# --- PANTALLA DE BIENVENIDA ---
if not st.session_state.data["perfil_completado"]:
    st.title("👋 ¡Bienvenido a Gym Pro AI!")
    st.write("Para empezar, necesitamos configurar tus datos básicos.")
    if st.button("Configurar mi Perfil ahora"):
        st.session_state.data["perfil_completado"] = True 
        guardar_todo(st.session_state.data)
        st.rerun()

# --- PANEL PRINCIPAL ---
else:
    st.title(f"Gym Pro AI - {u_nombre}")
    
    tabs = st.tabs(["📅 Rutina", "📊 Progreso", "🔮 Super IA", "🏆 Logros", "👤 Perfil"])
    tab1, tab2, tab3, tab4, tab5 = tabs

    # --- TAB 1: RUTINA ---
    with tab1:
        col_t1, col_t2 = st.columns([2, 1])
        with col_t1: st.header("Registrar HOY")
        with col_t2:
            with st.popover("⏱️ Descanso"):
                segundos = st.slider("Segundos", 30, 180, 90, step=30)
                if st.button("Iniciar"):
                    placeholder = st.empty()
                    for t in range(segundos, -1, -1):
                        placeholder.metric("Vuelve en:", f"{t}s")
                        time.sleep(1)
                    st.balloons()

        dia = st.selectbox("Día", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
        biblioteca = st.session_state.data["biblioteca_personal"]
        ej_sel = st.selectbox("Ejercicio", list(biblioteca.keys()))
        
        if biblioteca.get(ej_sel) == "Cardio":
            c1, c2 = st.columns(2)
            m_c = c1.number_input("Minutos", 1, 300, 30)
            i_c = c2.number_input("Inclinación", 0.0, 20.0, 10.0)
            if st.button("➕ Agregar Cardio"):
                st.session_state.data["rutinas"].append({"dia": dia, "ejercicio": ej_sel, "grupo": "Cardio", "es_cardio": True, "minutos": m_c, "inclinacion": i_c, "fecha": str(datetime.now().date())})
                guardar_todo(st.session_state.data); st.rerun()
        else:
            with st.expander("🧮 Calculadora de Discos"):
                peso_target = st.number_input("Peso Total (lbs)", 45, 1000, 135)
                lado = (peso_target - 45) / 2
                discos = [45, 35, 25, 10, 5, 2.5]
                res_discos = []
                for d in discos:
                    cnt = int(lado // d)
                    if cnt > 0: res_discos.append(f"{cnt}x{d}lb"); lado -= cnt * d
                st.write("**Cada lado:** " + (", ".join(res_discos) if res_discos else "Solo barra"))

            n_s = st.number_input("Series", 1, 10, 3)
            detalles_temp = []
            cols = st.columns(n_s)
            for i in range(n_s):
                with cols[i]:
                    r = st.number_input(f"Reps S{i+1}", 1, 100, 10, key=f"r{i}{dia}{ej_sel}")
                    p = st.number_input(f"Lbs S{i+1}", 0.0, 1000.0, 20.0, key=f"p{i}{dia}{ej_sel}")
                    detalles_temp.append({"serie": i+1, "reps": r, "peso": p})
            
            if st.button("➕ Agregar Ejercicio"):
                st.session_state.data["rutinas"].append({"dia": dia, "ejercicio": ej_sel, "grupo": biblioteca.get(ej_sel), "detalles": detalles_temp, "fecha": str(datetime.now().date())})
                guardar_todo(st.session_state.data); st.rerun()

    # --- TAB 2: PROGRESO ---
    with tab2:
        st.header("Seguimiento")
        with st.expander("📏 Registrar Medidas (cm)"):
            c_cint = st.number_input("Cintura", 40.0, 200.0, 80.0)
            c_braz = st.number_input("Brazo", 15.0, 70.0, 30.0)
            if st.button("Guardar Medidas"):
                st.session_state.data.setdefault("medidas", []).append({"fecha": str(datetime.now().date()), "cintura": c_cint, "brazo": c_braz})
                guardar_todo(st.session_state.data); st.rerun()

        rutinas = st.session_state.data.get("rutinas", [])
        for d in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
            filtro = [x for x in rutinas if x["dia"] == d]
            if filtro:
                with st.expander(f"🗓️ {d.upper()}"):
                    for it in filtro:
                        st.write(f"💪 **{it['ejercicio']}**")
                        if not it.get("es_cardio"):
                            st.caption(" | ".join([f"S{s['serie']}: {s['reps']}x{s['peso']}lb" for s in it['detalles']]))

    # --- TAB 3: SUPER IA (RESTAURADA AL 100%) ---
    with tab3:
        st.header("🔮 Análisis Inteligente Avanzado")
        pk = u_peso * 0.453592
        est_cm = u_estatura * 100
        grasa = (1.20 * u_imc) + (0.23 * u_edad) - 16.2
        mm = pk * (1 - (max(0, grasa)/100))
        tmb = (10 * pk) + (6.25 * est_cm) - (5 * u_edad) + 5
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Grasa Est.", f"{max(grasa, 5):.1f}%")
        c2.metric("Masa Magra", f"{mm:.1f} kg")
        c3.metric("Agua/Día", f"{(u_peso * 0.6) / 33.8:.1f} L")
        c4.metric("TMB", f"{tmb:.0f} kcal")

        if user_data.get("objetivos"):
            obj = user_data["objetivos"][0]
            cal = tmb * 1.2 - 500 if "Bajar" in obj else tmb * 1.2 + 300 if "Masa" in obj else tmb * 1.2
            st.info(f"🥗 **Nutrición:** Para {obj.lower()}, meta de **{cal:.0f} kcal/día**.")

        st.divider()
        rutinas_ia = st.session_state.data.get("rutinas", [])
        if not rutinas_ia:
            st.warning("Sin datos para análisis.")
        else:
            st.subheader("📊 Rendimiento y Fuerza")
            fuerza_maxima = {}
            vol_total_pesas = 0
            for r in rutinas_ia:
                if not r.get("es_cardio"):
                    v = sum([s['reps'] * s['peso'] for s in r['detalles']])
                    vol_total_pesas += v
                    mejores = max(r['detalles'], key=lambda x: x['peso'])
                    if 1 < mejores['reps'] <= 12:
                        rm1 = mejores['peso'] * (36 / (37 - mejores['reps']))
                        if r['ejercicio'] not in fuerza_maxima or rm1 > fuerza_maxima[r['ejercicio']]:
                            fuerza_maxima[r['ejercicio']] = rm1

            if fuerza_maxima:
                cols_f = st.columns(len(fuerza_maxima))
                for i, (ej, rm) in enumerate(fuerza_maxima.items()):
                    cols_f[i].metric(ej, f"{rm:.1f} lb")

            st.divider()
            st.subheader("🔋 Recuperación (SNC)")
            idx_hoy = datetime.now().weekday()
            dias_ref = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            recup = {r["grupo"]: (idx_hoy - dias_ref.index(r["dia"])) % 7 for r in rutinas_ia if not r.get("es_cardio")}
            cols_r = st.columns(len(recup))
            for i, (m, d) in enumerate(recup.items()):
                estado = "🔴 Fatiga" if d < 1 else "🟡 Recuperando" if d < 2 else "🟢 Listo"
                cols_r[i].write(f"**{m}**\n{estado}")

    # --- TAB 4: LOGROS ---
    with tab4:
        st.header("🏆 Logros")
        fechas = sorted(list(set([r["fecha"] for r in st.session_state.data.get("rutinas", []) if "fecha" in r])))
        racha = 0
        if fechas:
            check = datetime.now().date()
            while str(check) in fechas: racha += 1; check -= timedelta(days=1)
        st.subheader(f"🔥 Racha: {racha} días")

    # --- TAB 5: PERFIL ---
    with tab5:
        st.header("👤 Perfil")
        with st.expander("Editar Datos"):
            np = st.number_input("Peso", value=float(u_peso))
            if st.button("Guardar"):
                st.session_state.data["user"]["peso"] = np
                guardar_todo(st.session_state.data); st.rerun()

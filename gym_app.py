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

    # --- TAB 1: RUTINA (Con Temporizador y Calculadora) ---
    with tab1:
        col_t1, col_t2 = st.columns([2, 1])
        with col_t1:
            st.header("Registrar HOY")
        with col_t2:
            # --- FUNCIÓN: TEMPORIZADOR DE DESCANSO ---
            with st.popover("⏱️ Descanso"):
                segundos = st.slider("Segundos", 30, 180, 90, step=30)
                if st.button("Iniciar Cuenta Regresiva"):
                    placeholder = st.empty()
                    for t in range(segundos, -1, -1):
                        placeholder.metric("Vuelve en:", f"{t}s")
                        time.sleep(1)
                    st.balloons()
                    st.success("¡A darle otra vez!")

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
            # --- FUNCIÓN: CALCULADORA DE DISCOS ---
            with st.expander("🧮 Calculadora de Discos (Barra 45lb)"):
                peso_target = st.number_input("Peso Total a cargar (lbs)", 45, 1000, 135)
                peso_sin_barra = peso_target - 45
                if peso_sin_barra < 0: st.write("Solo la barra.")
                else:
                    lado = peso_sin_barra / 2
                    discos = [45, 35, 25, 10, 5, 2.5]
                    res_discos = []
                    for d in discos:
                        cnt = int(lado // d)
                        if cnt > 0:
                            res_discos.append(f"{cnt} de {d}lb")
                            lado -= cnt * d
                    st.write("**Pon de cada lado:** " + (", ".join(res_discos) if res_discos else "Nada"))

            n_s = st.number_input("Series", 1, 10, 3)
            detalles_temp = []
            cols = st.columns(n_s)
            for i in range(n_s):
                with cols[i]:
                    r = st.number_input(f"Reps S{i+1}", 1, 100, 10, key=f"r{i}{dia}{ej_sel}")
                    p = st.number_input(f"Lbs S{i+1}", 0.0, 1000.0, 20.0, key=f"p{i}{dia}{ej_sel}")
                    detalles_temp.append({"serie": i+1, "reps": r, "peso": p})
            
            if st.button("➕ Agregar Ejercicio"):
                st.session_state.data["rutinas"].append({
                    "dia": dia, "ejercicio": ej_sel, "grupo": biblioteca.get(ej_sel), 
                    "detalles": detalles_temp, "fecha": str(datetime.now().date())
                })
                guardar_todo(st.session_state.data); st.rerun()

    # --- TAB 2: PROGRESO (Con Medidas Corporales) ---
    with tab2:
        st.header("Seguimiento Físico")
        
        with st.expander("📏 Registrar Medidas (cm)"):
            fecha_m = str(datetime.now().date())
            col_m1, col_m2 = st.columns(2)
            cintura = col_m1.number_input("Cintura", 40.0, 200.0, 80.0)
            brazo = col_m2.number_input("Brazo (Bíceps)", 15.0, 70.0, 30.0)
            pecho = col_m1.number_input("Pecho", 50.0, 200.0, 95.0)
            muslo = col_m2.number_input("Muslo", 20.0, 120.0, 50.0)
            if st.button("Guardar Medidas"):
                if "medidas" not in st.session_state.data: st.session_state.data["medidas"] = []
                st.session_state.data["medidas"].append({"fecha": fecha_m, "cintura": cintura, "brazo": brazo, "pecho": pecho, "muslo": muslo})
                guardar_todo(st.session_state.data); st.success("Medidas guardadas."); st.rerun()

        rutinas = st.session_state.data.get("rutinas", [])
        if not rutinas: st.info("Registra algo hoy para ver tu historial.")
        else:
            for d in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
                filtro = [x for x in rutinas if x["dia"] == d]
                if filtro:
                    with st.expander(f"🗓️ {d.upper()}", expanded=False):
                        for it in filtro:
                            if it.get("es_cardio"):
                                st.write(f"🏃 **{it['ejercicio']}**: {it['minutos']} min | Inc: {it['inclinacion']}")
                            else:
                                st.write(f"💪 **{it['ejercicio']}** ({it['grupo']})")
                                res = " | ".join([f"S{s['serie']}: {s['reps']}x{s['peso']}lb" for s in it['detalles']])
                                st.caption(res)
            if st.button("🗑️ Resetear Semana"):
                st.session_state.data["rutinas"] = []; guardar_todo(st.session_state.data); st.rerun()

    # --- TAB 3: SUPER IA (Igual que antes) ---
    with tab3:
        st.header("🔮 Inteligencia Artificial")
        # (Aquí se mantiene todo el código analítico previo)
        pk = u_peso * 0.453592
        est_cm = u_estatura * 100
        grasa = (1.20 * u_imc) + (0.23 * u_edad) - 16.2
        tmb = (10 * pk) + (6.25 * est_cm) - (5 * u_edad) + 5
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Grasa Est.", f"{max(grasa, 5):.1f}%")
        c2.metric("Agua/Día", f"{(u_peso * 0.6) / 33.8:.1f} L")
        c3.metric("TMB", f"{tmb:.0f} kcal")

        rutinas_ia = st.session_state.data.get("rutinas", [])
        if rutinas_ia:
            vol_total = sum([sum([s['reps'] * s['peso'] for s in r['detalles']]) for r in rutinas_ia if not r.get("es_cardio")])
            st.write(f"📈 **Sobrecarga Progresiva:** Tu volumen semanal es **{vol_total:.0f} lbs**. La próxima semana intenta llegar a **{vol_total * 1.05:.0f} lbs**.")

    # --- TAB 4: LOGROS (Rachas y PRs) ---
    with tab4:
        st.header("🏆 Salón de la Fama")
        
        # --- FUNCIÓN: RACHAS (STREAKS) ---
        rutinas_todas = st.session_state.data.get("rutinas", [])
        fechas_entreno = sorted(list(set([r["fecha"] for r in rutinas_todas if "fecha" in r])))
        
        racha = 0
        if fechas_entreno:
            hoy = datetime.now().date()
            racha = 0
            check_date = hoy
            fechas_set = set(fechas_entreno)
            while str(check_date) in fechas_set:
                racha += 1
                check_date -= timedelta(days=1)
        
        st.subheader(f"🔥 Racha Actual: {racha} días")
        st.progress(min(racha / 7, 1.0), text="Progreso hacia meta semanal")

        st.divider()
        
        # --- FUNCIÓN: RÉCORDS PERSONALES (PRs) ---
        st.subheader("🥇 Récords Personales (Peso Máximo)")
        prs = {}
        for r in rutinas_todas:
            if not r.get("es_cardio"):
                ej = r["ejercicio"]
                max_p = max([s["peso"] for s in r["detalles"]])
                if ej not in prs or max_p > prs[ej]:
                    prs[ej] = max_p
        
        if not prs: st.write("Aún no hay récords. ¡Levanta pesado!")
        else:
            for ej, peso in prs.items():
                st.write(f"⭐ **{ej}**: {peso} lbs")

    # --- TAB 5: PERFIL ---
    with tab5:
        st.header("👤 Mi Perfil")
        c1, c2 = st.columns(2)
        c1.metric("IMC", f"{u_imc}")
        c2.metric("Meta Máx", f"{u_p_max} lbs")
        
        with st.expander("✏️ Editar Datos"):
            # (Aquí se mantiene el formulario de edición previo)
            nuevo_p = st.number_input("Actualizar Peso (Lbs)", value=float(u_peso))
            if st.button("Guardar cambios"):
                st.session_state.data["user"]["peso"] = nuevo_p
                guardar_todo(st.session_state.data); st.rerun()

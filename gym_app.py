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
            "Peso Muerto": "Espalda", "Caminata Inclinada": "Cardio"
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

    # --- TAB 1: RUTINA ---
    with tab1:
        col_header, col_tools = st.columns([2, 1])
        with col_header:
            st.header("Entrenamiento de Hoy")
        with col_tools:
            with st.popover("⏱️ Descanso"):
                segundos = st.slider("Segundos", 30, 180, 90, step=30)
                if st.button("Iniciar"):
                    placeholder = st.empty()
                    for t in range(segundos, -1, -1):
                        placeholder.metric("Vuelve en:", f"{t}s")
                        time.sleep(1)
                    st.balloons()
                    st.success("¡Siguiente serie!")

        dia = st.selectbox("Día de la semana", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
        biblioteca = st.session_state.data["biblioteca_personal"]
        ej_sel = st.selectbox("Selecciona Ejercicio", list(biblioteca.keys()))
        
        if biblioteca.get(ej_sel) == "Cardio":
            c1, c2 = st.columns(2)
            m_c = c1.number_input("Minutos", 1, 300, 30)
            i_c = c2.number_input("Inclinación", 0.0, 20.0, 10.0)
            if st.button("➕ Registrar Cardio"):
                st.session_state.data["rutinas"].append({
                    "dia": dia, "ejercicio": ej_sel, "grupo": "Cardio", 
                    "es_cardio": True, "minutos": m_c, "inclinacion": i_c, 
                    "fecha": str(datetime.now().date())
                })
                guardar_todo(st.session_state.data); st.rerun()
        else:
            with st.expander("🧮 Calculadora de Discos (Barra 45lb)"):
                peso_target = st.number_input("Peso total objetivo (lbs)", 45, 1000, 135)
                peso_neto = (peso_target - 45) / 2
                if peso_neto < 0:
                    st.write("Solo la barra olímpica.")
                else:
                    discos = [45, 35, 25, 10, 5, 2.5]
                    calc_res = []
                    for d in discos:
                        cantidad = int(peso_neto // d)
                        if cantidad > 0:
                            calc_res.append(f"{cantidad} de {d}lb")
                            peso_neto -= cantidad * d
                    st.write("**Cargar en cada lado:** " + (", ".join(calc_res) if calc_res else "Nada"))

            n_s = st.number_input("Número de Series", 1, 10, 3)
            detalles_temp = []
            cols_series = st.columns(n_s)
            for i in range(n_s):
                with cols_series[i]:
                    reps_i = st.number_input(f"Reps S{i+1}", 1, 100, 10, key=f"r{i}{dia}{ej_sel}")
                    peso_i = st.number_input(f"Lbs S{i+1}", 0.0, 1000.0, 20.0, key=f"p{i}{dia}{ej_sel}")
                    detalles_temp.append({"serie": i+1, "reps": reps_i, "peso": peso_i})
            
            if st.button("➕ Registrar Ejercicio"):
                st.session_state.data["rutinas"].append({
                    "dia": dia, "ejercicio": ej_sel, "grupo": biblioteca.get(ej_sel), 
                    "detalles": detalles_temp, "fecha": str(datetime.now().date())
                })
                guardar_todo(st.session_state.data); st.rerun()

    # --- TAB 2: PROGRESO ---
    with tab2:
        st.header("Evolución Física")
        with st.expander("📏 Registrar nuevas medidas corporales"):
            col_med1, col_med2 = st.columns(2)
            c_cintura = col_med1.number_input("Cintura (cm)", 40.0, 200.0, 80.0)
            c_brazo = col_med2.number_input("Brazo/Bíceps (cm)", 15.0, 70.0, 30.0)
            if st.button("Guardar Medidas"):
                if "medidas" not in st.session_state.data: st.session_state.data["medidas"] = []
                st.session_state.data["medidas"].append({
                    "fecha": str(datetime.now().date()), "cintura": c_cintura, "brazo": c_brazo
                })
                guardar_todo(st.session_state.data); st.success("Medidas guardadas."); st.rerun()

        st.subheader("Resumen Semanal")
        rutinas_hist = st.session_state.data.get("rutinas", [])
        if not rutinas_hist:
            st.info("Aún no tienes registros esta semana.")
        else:
            for d_nombre in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
                items_dia = [x for x in rutinas_hist if x["dia"] == d_nombre]
                if items_dia:
                    with st.expander(f"🗓️ {d_nombre.upper()}", expanded=False):
                        for item in items_dia:
                            if item.get("es_cardio"):
                                st.write(f"🏃 **{item['ejercicio']}**: {item['minutos']} min")
                            else:
                                st.write(f"💪 **{item['ejercicio']}**")
                                st.caption(" | ".join([f"S{s['serie']}: {s['reps']}x{s['peso']}lb" for s in item['detalles']]))

    # --- TAB 3: SUPER IA (DETALLES RESTAURADOS) ---
    with tab3:
        st.header("🔮 Super IA: Análisis 360°")
        peso_kg = u_peso * 0.453592
        altura_cm = u_estatura * 100
        grasa_est = (1.20 * u_imc) + (0.23 * u_edad) - 16.2
        masa_magra_kg = peso_kg * (1 - (max(0, grasa_est)/100))
        tmb_resultado = (10 * peso_kg) + (6.25 * altura_cm) - (5 * u_edad) + 5
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Grasa Est.", f"{max(grasa_est, 5):.1f}%")
        m2.metric("Masa Magra", f"{masa_magra_kg:.1f} kg")
        m3.metric("Agua/Día", f"{(u_peso * 0.6) / 33.8:.1f} L")
        m4.metric("TMB (Calorías)", f"{tmb_resultado:.0f}")

        st.divider()
        rutinas_ia = st.session_state.data.get("rutinas", [])
        if not rutinas_ia:
            st.warning("Sin registros para análisis.")
        else:
            st.subheader("📊 Fuerza y Volumen")
            fuerza_dict = {}
            vol_total = 0
            for r_ia in rutinas_ia:
                if not r_ia.get("es_cardio"):
                    vol_total += sum([s['reps'] * s['peso'] for s in r_ia['detalles']])
                    mejor = max(r_ia['detalles'], key=lambda x: x['peso'])
                    if 1 < mejor['reps'] <= 12:
                        rm_c = mejor['peso'] * (36 / (37 - mejor['reps']))
                        if r_ia['ejercicio'] not in fuerza_dict or rm_c > fuerza_dict[r_ia['ejercicio']]:
                            fuerza_dict[r_ia['ejercicio']] = rm_c
            
            if fuerza_dict:
                cols_rm = st.columns(min(len(fuerza_dict), 4))
                for idx, (n_e, v_rm) in enumerate(fuerza_dict.items()):
                    cols_rm[idx % 4].metric(n_e, f"{v_rm:.1f} lb")
            
            st.write(f"📈 **Volumen Semanal:** {vol_total:.0f} lbs. Objetivo: **{(vol_total * 1.05):.0f} lbs**.")

            st.divider()
            st.subheader("🔋 Estado de Recuperación (SNC)")
            dia_hoy_idx = datetime.now().weekday()
            dias_nom = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            recuperacion = {}
            for r_ia in rutinas_ia:
                if not r_ia.get("es_cardio"):
                    pasado = (dia_hoy_idx - dias_nom.index(r_ia["dia"])) % 7
                    if r_ia["grupo"] not in recuperacion or pasado < recuperacion[r_ia["grupo"]]:
                        recuperacion[r_ia["grupo"]] = pasado
            
            if recuperacion:
                cols_r = st.columns(min(len(recuperacion), 4))
                for i, (g, d) in enumerate(recuperacion.items()):
                    est = "🔴 Fatiga" if d == 0 else "🟡 Recuperando" if d == 1 else "🟢 Listo"
                    cols_r[i % 4].write(f"**{g}**\n{est}")

    # --- TAB 4: LOGROS (CORREGIDA) ---
    with tab4:
        st.header("🏆 Salón de la Fama")
        
        # Lógica de Racha
        todas_las_rutinas = st.session_state.data.get("rutinas", [])
        fechas_unicas = sorted(list(set([r["fecha"] for r in todas_las_rutinas if "fecha" in r])))
        
        racha_entreno = 0
        if fechas_unicas:
            hoy_dt = datetime.now().date()
            cursor = hoy_dt
            while str(cursor) in fechas_unicas:
                racha_entreno += 1
                cursor -= timedelta(days=1)
        
        st.metric("🔥 Racha Actual", f"{racha_entreno} Días")
        
        st.divider()
        st.subheader("🥇 Mis Récords Personales (PR)")
        
        mis_prs = {}
        for r_pr in todas_las_rutinas:
            if not r_pr.get("es_cardio"):
                nombre_ej = r_pr["ejercicio"]
                peso_max_sesion = max([s["peso"] for s in r_pr["detalles"]])
                if nombre_ej not in mis_prs or peso_max_sesion > mis_prs[nombre_ej]:
                    mis_prs[nombre_ej] = peso_max_sesion
        
        if mis_prs:
            for ej, peso in mis_prs.items():
                st.write(f"⭐ **{ej}**: {peso} lbs")
        else:
            st.info("Registra ejercicios con peso para ver tus récords aquí.")

    # --- TAB 5: PERFIL (CORREGIDA) ---
    with tab5:
        st.header("👤 Mi Perfil")
        
        v1, v2, v3 = st.columns(3)
        v1.metric("IMC", f"{u_imc}")
        v2.metric("Peso", f"{u_peso} lbs")
        v3.metric("Meta Máx", f"{u_p_max} lbs")

        st.divider()
        with st.expander("✏️ Editar mis datos"):
            ed_nombre = st.text_input("Nombre", value=u_nombre)
            ed_edad = st.number_input("Edad", 12, 95, value=u_edad)
            ed_peso = st.number_input("Peso (Lbs)", 50.0, 500.0, value=float(u_peso))
            
            # Altura en pies/pulgadas para facilidad del usuario
            val_pies = int((u_estatura / 0.0254) // 12)
            val_pulg = int((u_estatura / 0.0254) % 12)
            c_p1, c_p2 = st.columns(2)
            ed_pies = c_p1.number_input("Pies", 3, 8, value=val_pies)
            ed_pulg = c_p2.number_input("Pulgadas", 0, 11, value=val_pulg)
            
            ed_obj = st.multiselect("Objetivos", ["Bajar de peso", "Ganar Masa Muscular", "Tonificar"], default=u_objetivos)
            
            if st.button("Guardar Cambios"):
                est_final = ((ed_pies * 12) + ed_pulg) * 0.0254
                imc_n = round((ed_peso * 0.453592) / (est_final ** 2), 1)
                p_m_n = round((24.9 * (est_final ** 2)) / 0.453592, 1)
                
                st.session_state.data["user"] = {
                    "nombre": ed_nombre, "edad": ed_edad, "peso": ed_peso, 
                    "estatura_m": est_final, "imc": imc_n, "p_max_lb": p_m_n, "objetivos": ed_obj
                }
                guardar_todo(st.session_state.data)
                st.success("¡Datos actualizados!")
                st.rerun()

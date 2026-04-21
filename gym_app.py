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

    # --- TAB 1: RUTINA (Con herramientas de uso en vivo) ---
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

    # --- TAB 2: PROGRESO (Historial y Medidas) ---
    with tab2:
        st.header("Evolución Física")
        with st.expander("📏 Registrar nuevas medidas corporales"):
            col_med1, col_med2 = st.columns(2)
            c_cintura = col_med1.number_input("Cintura (cm)", 40.0, 200.0, 80.0)
            c_brazo = col_med2.number_input("Brazo/Bíceps (cm)", 15.0, 70.0, 30.0)
            c_pecho = col_med1.number_input("Pecho (cm)", 50.0, 250.0, 100.0)
            c_muslo = col_med2.number_input("Muslo (cm)", 20.0, 150.0, 55.0)
            if st.button("Guardar Medidas"):
                if "medidas" not in st.session_state.data: st.session_state.data["medidas"] = []
                st.session_state.data["medidas"].append({
                    "fecha": str(datetime.now().date()), "cintura": c_cintura, 
                    "brazo": c_brazo, "pecho": c_pecho, "muslo": c_muslo
                })
                guardar_todo(st.session_state.data); st.success("Medidas guardadas correctamente."); st.rerun()

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
                                st.write(f"🏃 **{item['ejercicio']}**: {item['minutos']} min | Inc: {item['inclinacion']}")
                            else:
                                st.write(f"💪 **{item['ejercicio']}** ({item['grupo']})")
                                desc_series = " | ".join([f"S{s['serie']}: {s['reps']}x{s['peso']}lb" for s in item['detalles']])
                                st.caption(desc_series)
            if st.button("🗑️ Limpiar Historial Semanal"):
                st.session_state.data["rutinas"] = []
                guardar_todo(st.session_state.data); st.rerun()

    # --- TAB 3: SUPER IA (DETALLES COMPLETOS) ---
    with tab3:
        st.header("🔮 Super IA: Análisis 360°")
        
        # 1. BIOMETRÍA Y METABOLISMO (Fórmulas avanzadas)
        st.subheader("🧬 Perfil Metabólico y Biometría")
        peso_kg = u_peso * 0.453592
        altura_cm = u_estatura * 100
        # Grasa estimada (Fórmula Deurenberg)
        grasa_est = (1.20 * u_imc) + (0.23 * u_edad) - 16.2
        masa_magra_kg = peso_kg * (1 - (max(0, grasa_est)/100))
        # TMB (Mifflin-St Jeor)
        tmb_resultado = (10 * peso_kg) + (6.25 * altura_cm) - (5 * u_edad) + 5
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Grasa Est.", f"{max(grasa_est, 5):.1f}%")
        m2.metric("Masa Magra", f"{masa_magra_kg:.1f} kg")
        m3.metric("Agua/Día", f"{(u_peso * 0.6) / 33.8:.1f} L")
        m4.metric("TMB (Calorías)", f"{tmb_resultado:.0f}")

        # Análisis nutricional según objetivo
        obj_act = u_objetivos[0] if u_objetivos else "Mantener"
        if "Bajar" in obj_act:
            cal_final = tmb_resultado * 1.2 - 500
            st.info(f"🥗 **Estrategia IA:** Para perder grasa, consume **{cal_final:.0f} kcal**. Prioriza 2.0g de proteína por kg.")
        elif "Masa" in obj_act or "Músculo" in obj_act:
            cal_final = tmb_resultado * 1.2 + 300
            st.info(f"🥩 **Estrategia IA:** Para ganar músculo, consume **{cal_final:.0f} kcal**. Prioriza carbohidratos complejos.")
        else:
            cal_final = tmb_resultado * 1.2
            st.info(f"⚖️ **Estrategia IA:** Para mantenimiento, consume **{cal_final:.0f} kcal**.")

        st.divider()

        # 2. ANÁLISIS DE FUERZA Y VOLUMEN (1RM)
        st.subheader("📊 Análisis de Fuerza y Volumen de Carga")
        rutinas_ia = st.session_state.data.get("rutinas", [])
        
        if not rutinas_ia:
            st.warning("Sin registros de entrenamiento para generar proyecciones de fuerza.")
        else:
            fuerza_max_dict = {}
            vol_total_semanal = 0
            cal_quemadas_ejercicio = 0
            
            for r_ia in rutinas_ia:
                if r_ia.get("es_cardio"):
                    # Estimación simple de quema calórica
                    cal_quemadas_ejercicio += r_ia["minutos"] * (8 + r_ia["inclinacion"]*0.5) * (peso_kg / 70)
                else:
                    v_ejer = sum([s['reps'] * s['peso'] for s in r_ia['detalles']])
                    vol_total_semanal += v_ejer
                    # Cálculo 1RM (Brzycki)
                    mejor_serie = max(r_ia['detalles'], key=lambda x: x['peso'])
                    if 1 < mejor_serie['reps'] <= 12:
                        rm_calc = mejor_serie['peso'] * (36 / (37 - mejor_serie['reps']))
                        if r_ia['ejercicio'] not in fuerza_max_dict or rm_calc > fuerza_max_dict[r_ia['ejercicio']]:
                            fuerza_max_dict[r_ia['ejercicio']] = rm_calc

            if fuerza_max_dict:
                st.write("**💪 Fuerza Máxima Estimada (1RM):**")
                cols_rm = st.columns(len(fuerza_max_dict) if len(fuerza_max_dict) < 5 else 4)
                for idx, (nombre_e, val_rm) in enumerate(fuerza_max_dict.items()):
                    cols_rm[idx % 4].metric(nombre_e, f"{val_rm:.1f} lb")
            
            st.write(f"🔥 **Gasto calórico estimado en gym:** ~{cal_quemadas_ejercicio:.0f} kcal.")
            st.write(f"📈 **Volumen de carga total:** {vol_total_semanal:.0f} lbs. Meta de sobrecarga: **{(vol_total_semanal * 1.05):.0f} lbs**.")

            st.divider()

            # 3. ESTADO DEL SISTEMA NERVIOSO CENTRAL (SNC) Y RECUPERACIÓN
            st.subheader("🔋 Estado de Recuperación y SNC")
            dia_idx_hoy = datetime.now().weekday()
            nombres_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            estado_recup = {}
            
            for r_ia in rutinas_ia:
                if not r_ia.get("es_cardio"):
                    g_musc = r_ia["grupo"]
                    dias_pasados = (dia_idx_hoy - nombres_dias.index(r_ia["dia"])) % 7
                    if g_musc not in estado_recup or dias_pasados < estado_recup[g_musc]:
                        estado_recup[g_musc] = dias_pasados
            
            if estado_recup:
                cols_snc = st.columns(len(estado_recup) if len(estado_recup) < 5 else 4)
                for idx_s, (g_m, d_p) in enumerate(estado_recup.items()):
                    if d_p == 0: st_texto, st_color = "🔴 Fatiga Alta", "red"
                    elif d_p == 1: st_texto, st_color = "🟡 Recuperando", "orange"
                    else: st_texto, st_color = "🟢 Listo", "green"
                    cols_snc[idx_s % 4].markdown(f"**{g_m}**\n\n:{st_color}[{st_texto}]")
            
            st.divider()
            
            # 4. RECOMENDACIÓN INTELIGENTE FINAL
            st.subheader("🤖 Recomendación de Próximo Paso")
            musculos_ready = [m for m, d in estado_recup.items() if d >= 2]
            if not estado_recup:
                st.write("Inicia tu semana entrenando grupos grandes como Pecho o Piernas.")
            elif musculos_ready:
                st.success(f"Tus grupos musculares listos para máxima intensidad: **{', '.join(musculos_ready)}**.")
            else:
                st.warning("Muchos grupos musculares fatigados. Considera un día de descanso o cardio ligero para permitir la recuperación del SNC.")

    # --- TAB 4: LOGROS (Rachas y PRs) ---
    with tab4:
        st.header("🏆 Salón de la Fama")
        todas_rutinas = st.session_state.data.get("rutinas", [])
        fechas_registradas = sorted(list(set([r["fecha"] for r in todas_rutinas if "fecha" in r])))
        
        racha_num = 0
        if fechas_registradas:
            hoy_dt = datetime.now().date()
            cursor = hoy_dt
            while str(cursor) in fechas_registradas:
                racha_num += 1
                cursor -= timedelta(days=1)
        
        st.metric("🔥 Racha de Entrenamiento", f"{racha_num} Días")
        
        st.divider()
        st.subheader("🥇 Récords Personales (PR)")
        pr_records = {}
        for r_pr in todas_rutinas:
            if not r_pr.get("es_cardio"):
                nombre_pr = r_pr["ejercicio"]
                max_peso_pr = max([s["peso"] for s in r_pr["detalles"]])
                if nombre_pr not in pr_records or max_peso_pr > pr_records[nombre_pr]:
                    pr_records[nombre_pr] = max_peso_pr
        
        if pr_records:
            for n_pr, v_pr in pr_records.items():
                st.write(f"⭐ **{n_pr}**: {v_pr} lbs")
        else:
            st.write("Aún no has registrado pesos máximos.")

    # --- TAB 5: PERFIL (Visualización y Edición) ---
    with tab4: # Nota: El usuario pidió visualizar datos aquí
        pass # La lógica de abajo maneja la visualización en la pestaña Perfil

    with tab5:
        st.header("👤 Mi Perfil y Datos Físicos")
        
        v1, v2, v3 = st.columns(3)
        v1.metric("IMC Actual", f"{u_imc}")
        v2.metric("Peso", f"{u_peso} lbs")
        v3.metric("Meta Máxima", f"{u_p_max} lbs")

        st.divider()
        
        with st.expander("✏️ Editar mis datos y objetivos"):
            ed_nombre = st.text_input("Nombre completo", value=u_nombre)
            ed_edad = st.number_input("Edad", 12, 95, value=u_edad)
            ed_peso = st.number_input("Peso actual (Lbs)", 50.0, 550.0, value=float(u_peso))
            
            # Cálculo de pies/pulgadas desde metros
            val_pies = int((u_estatura / 0.0254) // 12)
            val_pulg = int((u_estatura / 0.0254) % 12)
            
            c_p1, c_p2 = st.columns(2)
            ed_pies = c_p1.number_input("Estatura (Pies)", 3, 8, value=val_pies)
            ed_pulg = c_p2.number_input("Estatura (Pulgadas)", 0, 11, value=val_pulg)
            
            ed_obj = st.multiselect("Tus Objetivos", 
                                    ["Bajar de peso", "Ganar Masa Muscular", "Tonificar", "Resistencia", "Fuerza Pura"],
                                    default=u_objetivos)
            
            # Nuevos cálculos
            est_m_final = ((ed_pies * 12) + ed_pulg) * 0.0254
            imc_nuevo = round((ed_peso * 0.453592) / (est_m_final ** 2), 1) if est_m_final > 0 else 0
            p_max_nuevo = round((24.9 * (est_m_final ** 2)) / 0.453592, 1)

            if st.button("Actualizar Perfil"):
                st.session_state.data["user"] = {
                    "nombre": ed_nombre, "edad": ed_edad, "peso": ed_peso, 
                    "estatura_m": est_m_final, "imc": imc_nuevo, "p_max_lb": p_max_nuevo,
                    "objetivos": ed_obj
                }
                guardar_todo(st.session_state.data)
                st.success("¡Perfil actualizado con éxito!")
                st.rerun()

        st.subheader("Estatura Registrada")
        st.write(f"Mides actualmente **{u_estatura:.2f} metros**.")

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

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
    
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Rutina", "📊 Progreso", "🔮 Super IA", "👤 Perfil"])

    # --- TAB 1: RUTINA ---
    with tab1:
        with st.expander("➕ Crear nuevo ejercicio"):
            n_ej = st.text_input("Nombre Ejercicio")
            g_ej = st.selectbox("Grupo", ["Pecho", "Espalda", "Piernas", "Hombros", "Bíceps", "Tríceps", "Abdomen", "Cardio"])
            if st.button("Guardar Ejercicio"):
                st.session_state.data["biblioteca_personal"][n_ej] = g_ej
                guardar_todo(st.session_state.data); st.rerun()

        st.header("Registrar Entrenamiento")
        dia = st.selectbox("Día", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
        biblioteca = st.session_state.data["biblioteca_personal"]
        ej_sel = st.selectbox("Ejercicio", list(biblioteca.keys()))
        
        if biblioteca.get(ej_sel) == "Cardio":
            c1, c2 = st.columns(2)
            m_c = c1.number_input("Minutos", 1, 300, 30)
            i_c = c2.number_input("Inclinación", 0.0, 20.0, 10.0)
            if st.button("➕ Agregar Cardio"):
                st.session_state.data["rutinas"].append({"dia": dia, "ejercicio": ej_sel, "grupo": "Cardio", "es_cardio": True, "minutos": m_c, "inclinacion": i_c})
                guardar_todo(st.session_state.data); st.rerun()
        else:
            n_s = st.number_input("Series", 1, 10, 3)
            detalles_temp = []
            cols = st.columns(n_s)
            for i in range(n_s):
                with cols[i]:
                    r = st.number_input(f"Reps S{i+1}", 1, 100, 10, key=f"r{i}{dia}{ej_sel}")
                    p = st.number_input(f"Lbs S{i+1}", 0.0, 1000.0, 20.0, key=f"p{i}{dia}{ej_sel}")
                    detalles_temp.append({"serie": i+1, "reps": r, "peso": p})
            if st.button("➕ Agregar Ejercicio"):
                st.session_state.data["rutinas"].append({"dia": dia, "ejercicio": ej_sel, "grupo": biblioteca.get(ej_sel), "detalles": detalles_temp})
                guardar_todo(st.session_state.data); st.rerun()

    # --- TAB 2: PROGRESO ---
    with tab2:
        st.header("Historial Semanal")
        rutinas = st.session_state.data.get("rutinas", [])
        if not rutinas: st.info("No hay ejercicios registrados.")
        else:
            for d in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
                filtro = [x for x in rutinas if x["dia"] == d]
                if filtro:
                    with st.expander(f"🗓️ {d.upper()}", expanded=True):
                        for it in filtro:
                            if it.get("es_cardio"):
                                st.write(f"🏃 **{it['ejercicio']}**: {it['minutos']} min | Inc: {it['inclinacion']}")
                            else:
                                st.write(f"💪 **{it['ejercicio']}** ({it['grupo']})")
                                res = " | ".join([f"S{s['serie']}: {s['reps']}x{s['peso']}lb" for s in it['detalles']])
                                st.caption(res)
            if st.button("🗑️ Limpiar Todo"):
                st.session_state.data["rutinas"] = []; guardar_todo(st.session_state.data); st.rerun()

    # --- TAB 3: SUPER IA (EXPANDIDA) ---
    with tab3:
        st.header("🔮 Análisis Inteligente Avanzado")
        
        # 1. BIOMETRÍA Y METABOLISMO
        st.subheader("🧬 Biometría y Metabolismo Estimado")
        pk = u_peso * 0.453592
        est_cm = u_estatura * 100
        grasa = (1.20 * u_imc) + (0.23 * u_edad) - 16.2
        mm = pk * (1 - (max(0, grasa)/100))
        
        # Ecuación de Mifflin-St Jeor para Tasa Metabólica Basal
        tmb = (10 * pk) + (6.25 * est_cm) - (5 * u_edad) + 5
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Grasa Est.", f"{max(grasa, 5):.1f}%")
        c2.metric("Masa Magra", f"{mm:.1f} kg")
        c3.metric("Agua/Día", f"{(u_peso * 0.6) / 33.8:.1f} L")
        c4.metric("TMB (Reposo)", f"{tmb:.0f} kcal")

        # Ajuste calórico según objetivo
        if user_data.get("objetivos"):
            obj_principal = user_data["objetivos"][0]
            if "Bajar de peso" in obj_principal:
                cal_rec = tmb * 1.2 - 500
                st.info(f"🥗 **Nutrición IA:** Para {obj_principal.lower()}, tu límite sugerido es de **{cal_rec:.0f} kcal/día**. Mantienes un déficit calórico seguro.")
            elif "Masa Muscular" in obj_principal:
                cal_rec = tmb * 1.2 + 300
                st.info(f"🥩 **Nutrición IA:** Para hipertrofia, tu consumo debe ser de **{cal_rec:.0f} kcal/día**. Asegura al menos **{pk * 2.2:.0f}g de proteína diaria**.")
            else:
                cal_rec = tmb * 1.2
                st.info(f"⚖️ **Nutrición IA:** Para tonificar/mantener, tu consumo sugerido es de **{cal_rec:.0f} kcal/día**.")

        # Proyección de meta de peso
        if u_p_max > 0 and u_peso > u_p_max:
            semanas_est = (u_peso - u_p_max) / 1.5 
            st.warning(f"🎯 **Proyección Temporal:** Te faltan {u_peso - u_p_max:.1f} lbs para tu peso ideal máximo. Con una constancia del 80%, podrías alcanzarlo en **{semanas_est:.1f} semanas**.")

        st.divider()

        rutinas_ia = st.session_state.data.get("rutinas", [])
        if not rutinas_ia:
            st.warning("Aún no hay datos suficientes de entrenamiento. Registra ejercicios para activar las proyecciones de fuerza y recuperación neuronal.")
        else:
            # 2. ANÁLISIS DE ENTRENAMIENTO Y FUERZA
            st.subheader("📊 Análisis de Rendimiento y Fuerza Bruta")
            
            vol_por_grupo = {}
            fuerza_maxima = {} 
            calorias_quemadas = 0
            vol_total_pesas = 0
            
            for r in rutinas_ia:
                grupo = r["grupo"]
                ejercicio = r["ejercicio"]
                
                if r.get("es_cardio"):
                    calorias_quemadas += r["minutos"] * (8 + (r["inclinacion"] * 0.5)) * (pk / 70)
                else:
                    v = sum([s['reps'] * s['peso'] for s in r['detalles']])
                    vol_total_pesas += v
                    if grupo not in vol_por_grupo: vol_por_grupo[grupo] = 0
                    vol_por_grupo[grupo] += v
                    
                    # Cálculo de 1RM (Fórmula de Brzycki)
                    mejores_reps = max(r['detalles'], key=lambda x: x['peso'])
                    if 1 < mejores_reps['reps'] <= 12: 
                        rm1 = mejores_reps['peso'] * (36 / (37 - mejores_reps['reps']))
                        if ejercicio not in fuerza_maxima or rm1 > fuerza_maxima[ejercicio]:
                            fuerza_maxima[ejercicio] = rm1

            if fuerza_maxima:
                st.write("**💪 Tu Fuerza Máxima Estimada (1RM):**")
                st.caption("Peso máximo teórico que puedes levantar a una sola repetición.")
                cols_f = st.columns(min(len(fuerza_maxima), 4))
                for i, (ej, rm) in enumerate(list(fuerza_maxima.items())[:4]):
                    cols_f[i].metric(ej, f"{rm:.1f} lbs")
                    
            st.write(f"🔥 **Calorías extra quemadas esta semana:** ~{calorias_quemadas:.0f} kcal (Entrenamiento activo).")

            st.divider()

            # 3. FATIGA Y SISTEMA NERVIOSO CENTRAL (SNC)
            st.subheader("🔋 Estado del Sistema Nervioso y Recuperación Muscular")
            idx_hoy = datetime.now().weekday()
            dias_ref = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            recup_status = {}
            
            for r in rutinas_ia:
                if not r.get("es_cardio"):
                    g = r["grupo"]
                    diff = (idx_hoy - dias_ref.index(r["dia"])) % 7
                    recup_status[g] = diff
            
            if recup_status:
                cols_r = st.columns(4)
                idx_col = 0
                for m, d in recup_status.items():
                    if d == 0: estado = "🔴 Alta Fatiga (Entrenado hoy)"
                    elif d == 1: estado = "🟡 Recuperando (Hace 1 día)"
                    elif d == 2: estado = "🟢 Listo (Hace 2 días)"
                    else: estado = "🔵 Óptimo (Descansado)"
                    
                    cols_r[idx_col % 4].write(f"**{m}**\n{estado}")
                    idx_col += 1

            st.divider()

            # 4. RECOMENDADOR ESTRATÉGICO
            st.subheader("🤖 Recomendaciones de la IA para tu próxima sesión")
            
            musculos_descansados = [m for m, d in recup_status.items() if d >= 2 or m not in recup_status]
            
            if not recup_status:
                st.write("Empieza tu ciclo de entrenamiento priorizando grupos musculares grandes (Pecho o Piernas).")
            elif musculos_descansados:
                st.success(f"Tus grupos musculares más descansados son: **{', '.join(musculos_descansados)}**. ¡Priorízalos en tu próxima rutina para evitar lesiones!")
            else:
                st.warning("Tu sistema central tiene mucha carga reciente. La IA recomienda hacer **Cardio activo ligero, estiramientos o tomar un día completo de descanso**.")
                
            st.write(f"📈 **Sobrecarga Progresiva:** Tu volumen de carga actual es **{vol_total_pesas:.0f} lbs**. Para evitar estancamientos, tu objetivo en tu próximo ciclo de la semana debe ser alcanzar **{vol_total_pesas * 1.05:.0f} lbs** (Aumento del 5%).")

    # --- TAB 4: PERFIL ---
    with tab4:
        st.header("👤 Mi Perfil y Datos Físicos")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("IMC Actual", f"{u_imc}")
        c2.metric("Peso", f"{u_peso} lbs")
        c3.metric("Meta Máxima", f"{u_p_max} lbs")

        st.divider()
        
        with st.expander("✏️ Editar mis datos y medidas"):
            nuevo_nombre = st.text_input("Nombre", value=u_nombre)
            nueva_edad = st.number_input("Edad", 12, 90, value=u_edad)
            
            col_p, col_pies, col_pulg = st.columns(3)
            nuevo_p = col_p.number_input("Peso (Lbs)", 50.0, 500.0, value=float(u_peso))
            
            pies_val = int((u_estatura / 0.0254) // 12)
            pulg_val = int((u_estatura / 0.0254) % 12)
            
            nuevo_pies = col_pies.number_input("Pies", 3, 8, value=pies_val)
            nueva_pulg = col_pulg.number_input("Pulgadas", 0, 11, value=pulg_val)
            
            est_m = ((nuevo_pies * 12) + nueva_pulg) * 0.0254
            imc_calc = round((nuevo_p * 0.453592) / (est_m ** 2), 1) if est_m > 0 else 0
            p_max_lb = round((24.9 * (est_m ** 2)) / 0.453592, 1)

            if st.button("Actualizar mi información"):
                st.session_state.data["user"] = {
                    "nombre": nuevo_nombre, "edad": nueva_edad, "peso": nuevo_p, 
                    "estatura_m": est_m, "imc": imc_calc, "p_max_lb": p_max_lb,
                    "objetivos": user_data.get("objetivos", [])
                }
                guardar_todo(st.session_state.data)
                st.success("¡Datos actualizados!")
                st.rerun()

        st.subheader("ℹ️ Detalles de composición")
        if u_imc < 18.5: st.info("Estado: Bajo peso")
        elif 18.5 <= u_imc < 25: st.success("Estado: Peso saludable")
        elif 25 <= u_imc < 30: st.warning("Estado: Sobrepeso")
        else: st.error("Estado: Obesidad")
        
        st.write(f"Tu estatura registrada es de **{u_estatura:.2f} metros**.")

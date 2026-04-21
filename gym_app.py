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

# --- PANTALLA DE BIENVENIDA (SOLO SI ES LA PRIMERA VEZ) ---
if not st.session_state.data["perfil_completado"]:
    st.title("👋 ¡Bienvenido a Gym Pro AI!")
    st.write("Para empezar, necesitamos configurar tus datos básicos.")
    if st.button("Configurar mi Perfil ahora"):
        st.session_state.data["perfil_completado"] = True # Marcamos como true para entrar al panel, pero lo mandaremos a la pestaña perfil
        guardar_todo(st.session_state.data)
        st.rerun()

# --- PANEL PRINCIPAL ---
else:
    st.title(f"Gym Pro AI - {u_nombre}")
    
    # Creamos las 4 pestañas, incluyendo la nueva de Perfil
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

    # --- TAB 3: SUPER IA ---
    with tab3:
        st.header("🔮 Análisis Inteligente")
        rutinas_ia = st.session_state.data.get("rutinas", [])
        
        if not rutinas_ia:
            st.warning("Completa tu rutina para activar el análisis de IA.")
        else:
            vol_total = 0
            for r in rutinas_ia:
                if not r.get("es_cardio"):
                    vol_total += sum([s['reps'] * s['peso'] for s in r['detalles']])
            
            st.subheader("🚀 Proyecciones")
            st.write(f"Volumen de carga actual: **{vol_total:.0f} lbs**")
            st.write(f"Meta sugerida (Sobrecarga progresiva): **{vol_total * 1.05:.0f} lbs**")

    # --- TAB 4: PERFIL (TU NUEVA SECCIÓN) ---
    with tab4:
        st.header("👤 Mi Perfil y Datos Físicos")
        
        # Mostrar métricas actuales en tarjetas bonitas
        c1, c2, c3 = st.columns(3)
        c1.metric("IMC Actual", f"{u_imc}")
        c2.metric("Peso", f"{u_peso} lbs")
        c3.metric("Meta Máxima", f"{u_p_max} lbs")

        st.divider()
        
        # Formulario de edición dentro de la pestaña
        with st.expander("✏️ Editar mis datos y medidas"):
            nuevo_nombre = st.text_input("Nombre", value=u_nombre)
            nueva_edad = st.number_input("Edad", 12, 90, value=u_edad)
            
            col_p, col_pies, col_pulg = st.columns(3)
            nuevo_p = col_p.number_input("Peso (Lbs)", 50.0, 500.0, value=float(u_peso))
            
            # Re-calculamos pies/pulgadas para el input basándonos en metros (aprox)
            pies_val = int((u_estatura / 0.0254) // 12)
            pulg_val = int((u_estatura / 0.0254) % 12)
            
            nuevo_pies = col_pies.number_input("Pies", 3, 8, value=pies_val)
            nueva_pulg = col_pulg.number_input("Pulgadas", 0, 11, value=pulg_val)
            
            # Cálculos en tiempo real
            est_m = ((nuevo_pies * 12) + nueva_pulg) * 0.0254
            imc_calc = round((nuevo_p * 0.453592) / (est_m ** 2), 1) if est_m > 0 else 0
            p_max_lb = round((24.9 * (est_m ** 2)) / 0.453592, 1)

            if st.button("Actualizar mi información"):
                st.session_state.data["user"] = {
                    "nombre": nuevo_nombre, "edad": nueva_edad, "peso": nuevo_p, 
                    "estatura_m": est_m, "imc": imc_calc, "p_max_lb": p_max_lb
                }
                guardar_todo(st.session_state.data)
                st.success("¡Datos actualizados!")
                st.rerun()

        # Detalle informativo del IMC
        st.subheader("ℹ️ Detalles de composición")
        if u_imc < 18.5: st.info("Estado: Bajo peso")
        elif 18.5 <= u_imc < 25: st.success("Estado: Peso saludable")
        elif 25 <= u_imc < 30: st.warning("Estado: Sobrepeso")
        else: st.error("Estado: Obesidad")
        
        st.write(f"Tu estatura registrada es de **{u_estatura:.2f} metros**.")

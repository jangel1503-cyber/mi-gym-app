import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Configuración
st.set_page_config(page_title="Gym Pro AI", layout="centered")

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

# --- EXTRACCIÓN SEGURA ---
user_data = st.session_state.data.get("user", {})
u_nombre = user_data.get("nombre", "Usuario")
u_edad = user_data.get("edad", 0)
u_imc = user_data.get("imc", 0)
u_peso = user_data.get("peso", 0)

# --- PROTECCIÓN PARA MULTISELECT ---
opciones_objetivos = ["Bajar de peso", "Tonificar", "Masa Muscular"]
objetivos_guardados = user_data.get("objetivos", [])
# Solo dejamos los objetivos que sí existen en nuestra lista actual para evitar el error
objetivos_validos = [obj for obj in objetivos_guardados if obj in opciones_objetivos]

if u_edad == 0 or u_imc == 0 or u_peso == 0:
    st.session_state.data["perfil_completado"] = False

# --- PANTALLA 1: PERFIL ---
if not st.session_state.data["perfil_completado"]:
    st.title("👤 Configura tu Perfil")
    nombre = st.text_input("Nombre", value=u_nombre)
    edad = st.number_input("Edad", 12, 90, value=25 if u_edad == 0 else u_edad)
    
    col1, col2, col3 = st.columns(3)
    with col1: p_lb = st.number_input("Peso (Lbs)", 50.0, 500.0, 160.0 if u_peso == 0 else u_peso)
    with col2: pies = st.number_input("Pies", 3, 8, 5)
    with col3: pulgadas = st.number_input("Pulgadas", 0, 11, 7)
    
    est_m = ((pies * 12) + pulgadas) * 0.0254
    imc_calc = (p_lb * 0.453592) / (est_m ** 2) if est_m > 0 else 0
    
    # Aquí ya usamos la lista filtrada 'objetivos_validos'
    objs = st.multiselect("Objetivos", opciones_objetivos, default=objetivos_validos)

    if st.button("Guardar y Recalcular todo"):
        st.session_state.data["user"] = {
            "nombre": nombre, "edad": edad, "peso": p_lb, "estatura_m": est_m, 
            "imc": round(imc_calc, 1), "objetivos": objs
        }
        st.session_state.data["perfil_completado"] = True
        guardar_todo(st.session_state.data); st.rerun()

# --- EL RESTO DEL CÓDIGO SE MANTIENE IGUAL ---
else:
    st.title(f"💪 Panel de {u_nombre}")
    
    tab1, tab2, tab3 = st.tabs(["📅 Rutina", "📊 Progreso", "🔮 Super IA"])

    with tab1:
        with st.expander("➕ Crear nuevo ejercicio"):
            n_ej = st.text_input("Nombre")
            g_ej = st.selectbox("Grupo", ["Pecho", "Espalda", "Piernas", "Hombros", "Bíceps", "Tríceps", "Abdomen", "Cardio"])
            if st.button("Guardar Ejercicio"):
                st.session_state.data["biblioteca_personal"][n_ej] = g_ej
                guardar_todo(st.session_state.data); st.rerun()

        st.header("Registrar HOY")
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

    with tab2:
        st.header("Tu Plan Semanal")
        rutinas = st.session_state.data.get("rutinas", [])
        if not rutinas: st.info("Sin registros.")
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
            if st.button("🗑️ Borrar Semana"):
                st.session_state.data["rutinas"] = []; guardar_todo(st.session_state.data); st.rerun()

    with tab3:
        st.header("🔮 Inteligencia Artificial")
        rutinas_ia = st.session_state.data.get("rutinas", [])
        
        pk = u_peso * 0.453592
        grasa = (1.20 * u_imc) + (0.23 * u_edad) - 16.2
        mm = pk * (1 - (max(0, grasa)/100))
        
        st.subheader("⚖️ Composición Corporal")
        c1, c2, c3 = st.columns(3)
        c1.metric("Grasa Est.", f"{grasa:.1f}%")
        c2.metric("Masa Magra", f"{mm:.1f} kg")
        c3.metric("Agua/Día", f"{(u_peso * 0.6) / 33.8:.1f} L")

        st.divider()

        if not rutinas_ia:
            st.warning("Registra ejercicios para ver tus proyecciones.")
        else:
            st.subheader("🔋 Estado de Recuperación")
            idx_hoy = datetime.now().weekday()
            dias_ref = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            recup_status = {}
            vol_total = 0
            
            for r in rutinas_ia:
                if not r.get("es_cardio"):
                    g = r["grupo"]
                    v = sum([s['reps'] * s['peso'] for s in r['detalles']])
                    vol_total += v
                    diff = (idx_hoy - dias_ref.index(r["dia"])) % 7
                    recup_status[g] = "🔴 Recuperando" if diff < 2 else "🟢 Listo"
            
            if recup_status:
                cols_r = st.columns(len(recup_status))
                for i, (m, s) in enumerate(recup_status.items()):
                    cols_r[i].write(f"**{m}**\n{s}")

            st.divider()
            st.subheader("🚀 Rendimiento Futuro")
            col_izq, col_der = st.columns(2)
            with col_izq:
                st.write("**📈 Proyección a 90 días:**")
                st.write(f"Carga: **{vol_total * 1.25:.0f} lbs**")
            with col_der:
                lista_i = [x['inclinacion'] for x in rutinas_ia if x.get("es_cardio")]
                if lista_i:
                    horas_q = 5 if max(lista_i) > 8 else 2
                    st.write(f"**🔥 Efecto EPOC:**")
                    st.write(f"**{horas_q} horas** extras.")

    st.divider()
    if st.button("⚙️ Editar Perfil / Cambiar Peso"):
        st.session_state.data["perfil_completado"] = False
        guardar_todo(st.session_state.data); st.rerun()
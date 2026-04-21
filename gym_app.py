import streamlit as st
import json
import os
import random

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gym Pro AI", page_icon="💪", layout="wide")
DB_FILE = "gym_data.json"

# --- PERSISTENCIA ---
def guardar_todo(datos):
    with open(DB_FILE, "w", encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

def cargar_todo():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return {"perfil_completado": False, "user": {}, "rutina_semanal": {}}

if 'data' not in st.session_state:
    st.session_state.data = cargar_todo()

# --- MOTOR DE INTELIGENCIA ---
def generar_rutina_ia(objetivos, peso_lb):
    ejercicios_db = {
        "Pecho": ["Press de Banca", "Aperturas con mancuernas"],
        "Espalda": ["Remo con barra", "Jalón al pecho"],
        "Piernas": ["Sentadillas", "Prensa"],
        "Hombros": ["Press Militar", "Elevaciones laterales"],
        "Brazos": ["Curl de Bíceps", "Copa de Tríceps"],
        "Cardio": ["Caminata Inclinada", "Bicicleta"],
        "Abdomen": ["Plancha", "Crunches"]
    }
    
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    rutina = {}
    es_hipertrofia = any("masa" in obj.lower() or "fuerza" in obj.lower() for obj in objetivos)
    series = 4 if es_hipertrofia else 3
    reps = "8-12" if es_hipertrofia else "15-20"
    
    distribucion = {
        "Lunes": ["Pecho", "Brazos"],
        "Martes": ["Piernas"],
        "Miércoles": ["Descanso"],
        "Jueves": ["Espalda", "Hombros"],
        "Viernes": ["Cardio", "Abdomen"]
    }

    for dia, grupos in distribucion.items():
        if dia == "Miércoles":
            rutina[dia] = "Descanso activo o estiramientos"
        else:
            ejercicios_dia = []
            for g in grupos:
                lista = ejercicios_db.get(g, ["Ejercicio General"])
                for e in lista:
                    libras_sugeridas = round(peso_lb * random.uniform(0.2, 0.4), 0)
                    ejercicios_dia.append({
                        "ejercicio": e, "grupo": g, "series": series, "reps": reps, "libras": libras_sugeridas
                    })
            rutina[dia] = ejercicios_dia
    return rutina

# --- INTERFAZ DE REGISTRO INICIAL ---
if not st.session_state.data.get("perfil_completado", False):
    st.title("👋 Configuración Inicial de Perfil")
    with st.form("registro"):
        nombre = st.text_input("Nombre")
        peso = st.number_input("Peso (Lbs)", 50.0, 500.0, 160.0)
        c1, c2 = st.columns(2)
        pies = c1.number_input("Pies", 3, 8, 5)
        pulgadas = c2.number_input("Pulgadas", 0, 11, 7)
        
        lista_opciones = [
            "Ganar masa muscular (hipertrofia)", "Perder grasa corporal", "Aumentar fuerza",
            "Tonificar el cuerpo", "Mejorar salud cardiovascular", "Marcar abdomen"
        ]
        objs = st.multiselect("Tus Objetivos", lista_opciones)
        
        if st.form_submit_button("Guardar y Generar Mi Plan"):
            est_m = ((pies * 12) + pulgadas) * 0.0254
            st.session_state.data["user"] = {
                "nombre": nombre, "peso_lb": peso, "pies": pies, 
                "pulgadas": pulgadas, "estatura_m": est_m, "objetivos": objs
            }
            st.session_state.data["perfil_completado"] = True
            st.session_state.data["rutina_semanal"] = generar_rutina_ia(objs, peso)
            guardar_todo(st.session_state.data)
            st.rerun()

# --- PANEL PRINCIPAL ---
else:
    st.title("Gym Pro AI - Mi Entrenamiento")
    tab_rutina, tab_perfil = st.tabs(["📅 Mi Rutina", "👤 Mi Perfil"])

    # --- PESTAÑA 1: RUTINA (Edición y Visualización) ---
    with tab_rutina:
        st.subheader("Tu Plan Semanal Sugerido")
        rutina = st.session_state.data.get("rutina_semanal", {})
        
        for dia, contenido in rutina.items():
            with st.expander(f"📍 {dia.upper()}", expanded=(dia=="Lunes")):
                if isinstance(contenido, str):
                    st.write(f"✨ {contenido}")
                else:
                    for i, ej in enumerate(contenido):
                        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                        rutina[dia][i]['ejercicio'] = c1.text_input("Ejercicio", ej['ejercicio'], key=f"re_{dia}_{i}")
                        rutina[dia][i]['series'] = c2.number_input("Series", 1, 10, int(ej['series']), key=f"rs_{dia}_{i}")
                        rutina[dia][i]['reps'] = c3.text_input("Reps", ej['reps'], key=f"rr_{dia}_{i}")
                        rutina[dia][i]['libras'] = c4.number_input("Lbs", 0.0, 1000.0, float(ej['libras']), key=f"rl_{dia}_{i}")
        
        if st.button("💾 Guardar Cambios en la Rutina"):
            st.session_state.data["rutina_semanal"] = rutina
            guardar_todo(st.session_state.data)
            st.success("Rutina actualizada.")

    # --- PESTAÑA 2: PERFIL (Edición Permanente) ---
    with tab_perfil:
        st.subheader("Configuración de mi Perfil")
        u = st.session_state.data["user"]
        
        with st.form("editar_perfil"):
            nuevo_nombre = st.text_input("Nombre", value=u['nombre'])
            nuevo_peso = st.number_input("Peso (Lbs)", value=float(u['peso_lb']))
            c1, c2 = st.columns(2)
            n_pies = c1.number_input("Pies", 3, 8, value=int(u['pies']))
            n_pulgadas = c2.number_input("Pulgadas", 0, 11, value=int(u['pulgadas']))
            
            lista_opciones = [
                "Ganar masa muscular (hipertrofia)", "Perder grasa corporal", "Aumentar fuerza",
                "Tonificar el cuerpo", "Mejorar salud cardiovascular", "Marcar abdomen"
            ]
            nuevos_objs = st.multiselect("Objetivos", lista_opciones, default=u['objetivos'])
            
            if st.form_submit_button("Actualizar mis Datos"):
                est_m = ((n_pies * 12) + n_pulgadas) * 0.0254
                st.session_state.data["user"] = {
                    "nombre": nuevo_nombre, "peso_lb": nuevo_peso, "pies": n_pies, 
                    "pulgadas": n_pulgadas, "estatura_m": est_m, "objetivos": nuevos_objs
                }
                guardar_todo(st.session_state.data)
                st.success("¡Datos actualizados permanentemente!")
                st.rerun()

        st.divider()
        # Resumen informativo debajo del editor
        peso_kg = u['peso_lb'] * 0.453592
        imc = round(peso_kg / (u['estatura_m']**2), 1)
        st.write(f"📊 **Resumen actual:** IMC de {imc} | {n_pies}'{n_pulgadas}'' | {nuevo_peso} lbs")

    if st.sidebar.button("Borrar todo"):
        st.session_state.data = {"perfil_completado": False, "user": {}, "rutina_semanal": {}}
        guardar_todo(st.session_state.data)
        st.rerun()

import streamlit as st
import json
import os

# --- CONFIGURACIÓN Y BASE DE DATOS ---
st.set_page_config(page_title="Gym Pro AI", page_icon="💪")
DB_FILE = "gym_data.json"

def guardar_todo(datos):
    with open(DB_FILE, "w", encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

def cargar_todo():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"perfil_completado": False, "user": {}}

if 'data' not in st.session_state:
    st.session_state.data = cargar_todo()

# --- LÓGICA DE CÁLCULOS ---
def calcular_imc(peso_lb, estatura_m):
    peso_kg = peso_lb * 0.453592
    imc = peso_kg / (estatura_m ** 2)
    return round(imc, 1)

def clasificar_imc(imc):
    if imc < 18.5: return "Bajo peso"
    elif 18.5 <= imc <= 24.9: return "Peso normal"
    elif 25.0 <= imc <= 29.9: return "Sobrepeso"
    else: return "Obesidad"

def obtener_peso_ideal(estatura_m):
    # Basado en el rango saludable de IMC (18.5 - 24.9)
    peso_min_kg = 18.5 * (estatura_m ** 2)
    peso_max_kg = 24.9 * (estatura_m ** 2)
    return round(peso_min_kg / 0.453592, 1), round(peso_max_kg / 0.453592, 1)

# --- PANTALLA DE REGISTRO (PRIMERA VEZ) ---
if not st.session_state.data.get("perfil_completado", False):
    st.title("👋 Bienvenido a Gym Pro AI")
    st.write("Para empezar, necesitamos configurar tu perfil:")

    with st.form("registro_perfil"):
        nombre = st.text_input("¿Cómo te llamas?")
        edad = st.number_input("Edad (años)", min_value=12, max_value=100, value=25)
        
        st.write("Estatura")
        c1, c2 = st.columns(2)
        pies = c1.number_input("Pies", min_value=3, max_value=8, value=5)
        pulgadas = c2.number_input("Pulgadas", min_value=0, max_value=11, value=7)
        
        peso = st.number_input("Peso (Libras)", min_value=50.0, max_value=600.0, value=160.0)
        
        st.write("🎯 Selecciona tus objetivos:")
        objetivos = st.multiselect("Puedes elegir varios:", [
            "Ganar masa muscular (hipertrofia)", "Perder grasa corporal", "Aumentar fuerza",
            "Mejorar resistencia cardiovascular", "Tonificar el cuerpo", "Mejorar movilidad y flexibilidad",
            "Reducir el estrés", "Dormir mejor", "Mejorar salud cardiovascular", "Prevenir lesiones",
            "Aumentar niveles de energía", "Correr más rápido", "Saltar más alto", 
            "Prepararse para deporte específico", "Mejorar coordinación y equilibrio",
            "Marcar abdomen", "Aumentar glúteos o piernas", "Definir brazos y hombros", "Mejorar postura",
            "Crear rutina constante", "Aprender técnica correcta", "Mantener consistencia",
            "Desarrollar disciplina", "Bajar peso en tiempo específico", "Levantar peso clave"
        ])

        enviado = st.form_submit_button("Guardar mi perfil")

        if enviado:
            if not nombre:
                st.error("Por favor, ingresa tu nombre.")
            else:
                # Convertir estatura a metros para cálculos
                estatura_m = ((pies * 12) + pulgadas) * 0.0254
                st.session_state.data["user"] = {
                    "nombre": nombre,
                    "edad": edad,
                    "pies": pies,
                    "pulgadas": pulgadas,
                    "estatura_m": estatura_m,
                    "peso_lb": peso,
                    "objetivos": objetivos
                }
                st.session_state.data["perfil_completado"] = True
                guardar_todo(st.session_state.data)
                st.rerun()

# --- PANTALLA PRINCIPAL (RESULTADOS DEL PERFIL) ---
else:
    u = st.session_state.data["user"]
    st.title(f"Hola, {u['nombre']} 👋")
    
    # Cálculos en tiempo real
    imc_actual = calcular_imc(u['peso_lb'], u['estatura_m'])
    estado = clasificar_imc(imc_actual)
    p_min, p_max = obtener_peso_ideal(u['estatura_m'])

    st.subheader("📊 Análisis de composición")
    
    c1, c2 = st.columns(2)
    c1.metric("Tu IMC", f"{imc_actual}")
    c2.metric("Estado de peso", estado)

    st.info(f"💡 Según tu altura, tu peso ideal debería estar entre **{p_min}** y **{p_max} lbs**.")

    if st.button("Reiniciar perfil (Borrar todo)"):
        st.session_state.data = {"perfil_completado": False, "user": {}}
        guardar_todo(st.session_state.data)
        st.rerun()

import streamlit as st
from enigma_simulator import enigma_step_debug, bombe_brute_force, REFLECTORS

def formatear_en_grupos_de_5(texto):
    return ' '.join([texto[i:i+5] for i in range(0, len(texto), 5)])

st.set_page_config(page_title="Simulador Enigma & Bombe", layout="centered")
st.title("🧠 Proyecto: Máquina Enigma y Bombe")

modo_simulador = st.sidebar.radio("Selecciona el simulador", ["🔐 Enigma", "🧠 Bombe"])

if modo_simulador == "🔐 Enigma":
    st.header("Simulador Máquina Enigma")

    if "cargar_mensaje" not in st.session_state:
        st.session_state.cargar_mensaje = False

    if st.button("📜 Cargar mensaje histórico (25/11/1941)"):
        st.session_state.mensaje = "GCDSE AHUGW TQGRK VLFGX UCALX VYMIG MMNMF DXTGN VHVRM MEVOU YFZSL RHDRR XFJWC FHUHM UNZEF RDISI KBGPM YVXUZ"
        st.session_state.rotor_izq = "II"
        st.session_state.rotor_med = "I"
        st.session_state.rotor_der = "III"
        st.session_state.pos_izq = 6
        st.session_state.pos_med = 15
        st.session_state.pos_der = 12
        st.session_state.ring_izq = 24
        st.session_state.ring_med = 13
        st.session_state.ring_der = 22
        st.session_state.reflector = "A"
        st.session_state.stecker_input = "AM FI NV PS TU WZ"
        st.session_state.modo = "Descifrar"
        st.session_state.cargar_mensaje = True

    mensaje = st.text_area("📨 Mensaje (solo letras A-Z)", st.session_state.get("mensaje", ""))

    col1, col2, col3 = st.columns(3)
    rotor_izq = col1.selectbox("Rotor Izquierdo", ["I", "II", "III"], index=["I", "II", "III"].index(st.session_state.get("rotor_izq", "I")))
    rotor_med = col2.selectbox("Rotor Medio", ["I", "II", "III"], index=["I", "II", "III"].index(st.session_state.get("rotor_med", "II")))
    rotor_der = col3.selectbox("Rotor Derecho", ["I", "II", "III"], index=["I", "II", "III"].index(st.session_state.get("rotor_der", "III")))

    col4, col5, col6 = st.columns(3)
    pos_izq = col4.slider("Posición Inicial Izquierdo", 0, 25, st.session_state.get("pos_izq", 0))
    pos_med = col5.slider("Posición Inicial Medio", 0, 25, st.session_state.get("pos_med", 0))
    pos_der = col6.slider("Posición Inicial Derecho", 0, 25, st.session_state.get("pos_der", 0))

    col7, col8, col9 = st.columns(3)
    ring_izq = col7.slider("Anillo Izquierdo", 0, 25, st.session_state.get("ring_izq", 0))
    ring_med = col8.slider("Anillo Medio", 0, 25, st.session_state.get("ring_med", 0))
    ring_der = col9.slider("Anillo Derecho", 0, 25, st.session_state.get("ring_der", 0))

    reflector = st.selectbox("Reflector", ["A", "B", "C"], index=["A", "B", "C"].index(st.session_state.get("reflector", "B")))

    stecker_input = st.text_input("🔗 Steckerbrett (pares como AB CD EF)", st.session_state.get("stecker_input", ""))
    modo = st.radio("Modo", ["Cifrar", "Descifrar"], index=0 if st.session_state.get("modo", "Cifrar") == "Cifrar" else 1)

    if st.button("🛠️ Ejecutar Enigma"):
        stecker = {}
        for par in stecker_input.upper().split():
            if len(par) == 2:
                a, b = par[0], par[1]
                stecker[a] = b
                stecker[b] = a

        rotors = [rotor_izq, rotor_med, rotor_der]
        pos = [pos_izq, pos_med, pos_der]
        rings = [ring_izq, ring_med, ring_der]

        reflector_map = REFLECTORS[reflector]

        resultado = enigma_step_debug(
            message=mensaje,
            rotors_order=rotors,
            rotor_positions=pos,
            ring_settings=rings,
            reflector=reflector_map,
            steckerbrett=stecker,
            encrypt=(modo == "Cifrar")
        )

        st.text_area("Resultado", formatear_en_grupos_de_5(resultado), height=200)

elif modo_simulador == "🧠 Bombe":
    st.header("Simulador Máquina Bombe (Versión simplificada)")

    mensaje_cifrado = st.text_area("🔐 Mensaje cifrado (A-Z)", "")
    known_plaintext = st.text_input("📍 Texto esperado (crib)", "")
    reflector_bombe = st.selectbox("Reflector (fijo para Bombe)", ["B", "C"], index=0)

    if st.button("🧠 Ejecutar Bombe"):
        if mensaje_cifrado and known_plaintext:
            with st.spinner("Buscando configuración correcta... Esto puede tardar varios minutos"):
                resultado_bombe = bombe_brute_force(
                    mensaje_cifrado.upper(),
                    known_plaintext.upper(),
                    reflector_name=reflector_bombe
                )
            if resultado_bombe:
                st.success(f"🎉 Se encontraron {len(resultado_bombe)} configuración(es):")
                for idx, res in enumerate(resultado_bombe, 1):
                    st.markdown(f"### Resultado {idx}")
                    st.write(f"- Orden rotores: {res['rotors_order']}")
                    st.write(f"- Posiciones iniciales: {res['positions']}")
                    st.write(f"- Ringstellung: {res['ring_settings']}")
                    st.text_area("Texto descifrado", formatear_en_grupos_de_5(res['plaintext']), height=150)
            else:
                st.error("No se encontró coincidencia con esta configuración.")
        else:
            st.warning("Por favor, introduce tanto el mensaje cifrado como el texto esperado.")

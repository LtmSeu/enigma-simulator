# enigma_simulator.py
import string
import itertools

# --- Datos de rotores y reflectores (simplificado, versión Enigma I clásica) ---

ROTOR_WIRINGS = {
    "I":    "EKMFLGDQVZNTOWYHXUSPAIBRCJ",
    "II":   "AJDKSIRUXBLHWTMCQGZNPYFVOE",
    "III":  "BDFHJLCPRTXVZNYEIWGAKMUSQO",
}

ROTOR_NOTCHES = {
    "I":    "Q",  # el rotor avanza el siguiente cuando pasa de Q a R
    "II":   "E",
    "III":  "V",
}

REFLECTORS = {
    "A": "EJMZALYXVBWFCRQUONTSPIKHGD",
    "B": "YRUHQSLDPXNGOKMIEBFZCWVJAT",
    "C": "FVPJIAOYEDRZXWGCTKUQSBNMHL",
}

ALPHABET = string.ascii_uppercase

# --- Funciones básicas ---

def rotor_forward(c, wiring, pos, ring):
    idx = (ALPHABET.index(c) + pos - ring) % 26
    wired_c = wiring[idx]
    return ALPHABET[(ALPHABET.index(wired_c) - pos + ring) % 26]

def rotor_backward(c, wiring, pos, ring):
    idx = (ALPHABET.index(c) + pos - ring) % 26
    wired_idx = wiring.index(ALPHABET[idx])
    return ALPHABET[(wired_idx - pos + ring) % 26]

def plugboard_swap(c, steckerbrett):
    return steckerbrett.get(c, c)

# --- Máquina Enigma simulada con 3 rotores ---

def enigma_step_debug(message, rotors_order, rotor_positions, ring_settings, reflector, steckerbrett, encrypt=True):
    # Inicializar posiciones de rotores
    pos_left, pos_mid, pos_right = rotor_positions
    ring_left, ring_mid, ring_right = ring_settings

    rotor_left_wiring = ROTOR_WIRINGS[rotors_order[0]]
    rotor_mid_wiring = ROTOR_WIRINGS[rotors_order[1]]
    rotor_right_wiring = ROTOR_WIRINGS[rotors_order[2]]

    rotor_left_notch = ROTOR_NOTCHES[rotors_order[0]]
    rotor_mid_notch = ROTOR_NOTCHES[rotors_order[1]]
    rotor_right_notch = ROTOR_NOTCHES[rotors_order[2]]

    result = []

    for char in message:
        if char not in ALPHABET:
            result.append(char)
            continue

        # --- Avance de rotores (doble paso)
        # El rotor medio avanza si el derecho está en su notch (doble paso)
        # y el izquierdo avanza si el medio está en notch

        # Rotor medio avanza si rotor derecho está en notch en la posición actual
        if ALPHABET[pos_right] == rotor_right_notch:
            pos_mid = (pos_mid + 1) % 26
            # Si rotor medio en notch, rotor izquierdo avanza
            if ALPHABET[pos_mid] == rotor_mid_notch:
                pos_left = (pos_left + 1) % 26

        # Rotor derecho siempre avanza un paso
        pos_right = (pos_right + 1) % 26

        # Si rotor medio en notch (doble paso)
        if ALPHABET[pos_mid] == rotor_mid_notch:
            pos_left = (pos_left + 1) % 26

        # --- Pasar por plugboard
        c = plugboard_swap(char, steckerbrett)

        # --- Pasar por rotores hacia adelante (derecha a izquierda)
        c = rotor_forward(c, rotor_right_wiring, pos_right, ring_right)
        c = rotor_forward(c, rotor_mid_wiring, pos_mid, ring_mid)
        c = rotor_forward(c, rotor_left_wiring, pos_left, ring_left)

        # --- Pasar por reflector
        c = reflector[ALPHABET.index(c)]

        # --- Pasar por rotores hacia atrás (izquierda a derecha)
        c = rotor_backward(c, rotor_left_wiring, pos_left, ring_left)
        c = rotor_backward(c, rotor_mid_wiring, pos_mid, ring_mid)
        c = rotor_backward(c, rotor_right_wiring, pos_right, ring_right)

        # --- Pasar por plugboard otra vez
        c = plugboard_swap(c, steckerbrett)

        result.append(c)

    return ''.join(result)

def bombe_brute_force(ciphertext, crib, reflector_name="B"):
    reflector = REFLECTORS[reflector_name]

    # Configuración fija
    rotors_order = ["I", "II", "III"]
    positions = [0, 0, 0]
    ring_settings = [0, 0, 0]
    steckerbrett = {}

    # Descifrar con esta única configuración
    decrypted = enigma_step_debug(
        message=ciphertext,
        rotors_order=rotors_order,
        rotor_positions=positions,
        ring_settings=ring_settings,
        reflector=reflector,
        steckerbrett=steckerbrett,
        encrypt=False
    )

    if crib in decrypted:
        return [{
            "rotors_order": rotors_order,
            "positions": positions,
            "ring_settings": ring_settings,
            "plaintext": decrypted
        }]
    else:
        return []

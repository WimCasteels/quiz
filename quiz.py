import streamlit as st
import json
import random
import os

def load_quiz_data():
    """Laad quiz vragen uit een extern JSON bestand"""
    try:
        # Probeer het JSON bestand te laden uit dezelfde directory als het script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, 'vragen.json')
        
        with open(json_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        st.error(f"Kon het vragen bestand niet laden: {str(e)}")
        st.error("Controleer of 'vragen.json' aanwezig is in dezelfde map als het script.")
        return {"vragen": []}

def initialize_session_state():
    if 'huidige_vraag' not in st.session_state:
        st.session_state.huidige_vraag = 0
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'quiz_data' not in st.session_state:
        st.session_state.quiz_data = load_quiz_data()
    if 'antwoord_gegeven' not in st.session_state:
        st.session_state.antwoord_gegeven = False
    if 'geschudde_opties' not in st.session_state:
        st.session_state.geschudde_opties = {}
    if 'gekozen_antwoord' not in st.session_state:
        st.session_state.gekozen_antwoord = None
    if 'feedback_container' not in st.session_state:
        st.session_state.feedback_container = None

def shuffle_options(vraag_index):
    if vraag_index not in st.session_state.geschudde_opties:
        opties = st.session_state.quiz_data["vragen"][vraag_index]["opties"].copy()
        random.shuffle(opties)
        st.session_state.geschudde_opties[vraag_index] = opties
    return st.session_state.geschudde_opties[vraag_index]

def volgende_vraag():
    st.session_state.huidige_vraag += 1
    st.session_state.antwoord_gegeven = False
    st.session_state.gekozen_antwoord = None
    st.rerun()

def main():
    st.title("Quiz: AI & De Aarde")
    
    initialize_session_state()
    
    # Controleer of er vragen zijn geladen
    if not st.session_state.quiz_data["vragen"]:
        st.error("Geen vragen gevonden. Controleer het vragen.json bestand.")
        return

    if st.session_state.huidige_vraag < len(st.session_state.quiz_data["vragen"]):
        vraag_data = st.session_state.quiz_data["vragen"][st.session_state.huidige_vraag]
        
        # Maak kolommen voor vraagnummer en score
        col1, col2 = st.columns(2)
        
        # Toon vraag nummer en score in kolommen
        with col1:
            st.write(f"Vraag {st.session_state.huidige_vraag + 1} van {len(st.session_state.quiz_data['vragen'])}")
        with col2:
            st.write(f"**Score**: {st.session_state.score}")
        
        # Voeg wat ruimte toe tussen de header en de vraag
        st.write("")
        
        # Toon de vraag
        st.header(vraag_data["vraag"])
        
        # Haal geschudde opties op
        opties = shuffle_options(st.session_state.huidige_vraag)
        
        # Container voor feedback en volgende vraag knop
        feedback_container = st.container()
        
        # Als er nog geen antwoord is gegeven
        if not st.session_state.antwoord_gegeven:
            # Toon radio buttons met de opties
            st.session_state.gekozen_antwoord = st.radio(
                "Kies je antwoord:",
                opties,
                key=f"vraag_{st.session_state.huidige_vraag}"
            )
            
            # Controleer antwoord knop
            if st.button("Controleer antwoord"):
                st.session_state.antwoord_gegeven = True
                
                with feedback_container:
                    if st.session_state.gekozen_antwoord == vraag_data["correct_antwoord"]:
                        st.success("Correct! " + vraag_data["uitleg"])
                        st.session_state.score += 1
                    else:
                        st.error(f"Helaas, het juiste antwoord was {vraag_data['correct_antwoord']}. " + vraag_data["uitleg"])
                    
                    # Direct de volgende vraag knop tonen
                    if st.button("Volgende vraag"):
                        volgende_vraag()
        
        # Als er wel een antwoord is gegeven
        else:
            # Toon het gekozen antwoord
            try:
                antwoord_index = opties.index(st.session_state.gekozen_antwoord)
            except ValueError:
                antwoord_index = 0
                
            st.radio(
                "Gekozen antwoord:",
                opties,
                key=f"answered_{st.session_state.huidige_vraag}",
                index=antwoord_index,
                disabled=True
            )
            
            # Toon het resultaat en de volgende vraag knop
            with feedback_container:
                if st.session_state.gekozen_antwoord == vraag_data["correct_antwoord"]:
                    st.success("Correct! " + vraag_data["uitleg"])
                else:
                    st.error(f"Helaas, het juiste antwoord was {vraag_data['correct_antwoord']}. " + vraag_data["uitleg"])
                
                if st.button("Volgende vraag"):
                    volgende_vraag()
    
    else:
        # Quiz is afgelopen, toon eindresultaat
        st.success(f"Quiz voltooid! Je eindscore is: {st.session_state.score} van de {len(st.session_state.quiz_data['vragen'])}")
        
        # Reset knop
        if st.button("Start opnieuw"):
            st.session_state.huidige_vraag = 0
            st.session_state.score = 0
            st.session_state.antwoord_gegeven = False
            st.session_state.geschudde_opties = {}
            st.session_state.gekozen_antwoord = None
            st.rerun()

if __name__ == "__main__":
    main()
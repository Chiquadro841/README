import streamlit as st
import joblib
import pandas as pd

# Carica il modello addestrato
model = joblib.load('random_forest_model.pkl')

# Funzione di predizione
def predict_match(forzaA, forzaB, squadraA_heroes, squadraB_heroes, model):
    # Crea un dizionario con tutte le possibili colonne inizializzate a 0
    input_data = {col: 0 for col in model.feature_names_in_}
    
    # Imposta le forze
    input_data['forzaA'] = forzaA
    input_data['forzaB'] = forzaB
    
    # Imposta le variabili dummy per gli eroi di Squadra A
    for hero in squadraA_heroes:
        col_name = f'SquadraA_{hero}'
        if col_name in input_data:
            input_data[col_name] = 1
    
    # Imposta le variabili dummy per gli eroi di Squadra B
    for hero in squadraB_heroes:
        col_name = f'SquadraB_{hero}'
        if col_name in input_data:
            input_data[col_name] = 1
    
    # Converte il dizionario in un DataFrame
    input_df = pd.DataFrame([input_data])
    
    # Predice l'esito usando il modello
    prediction = model.predict(input_df)
    
    return prediction[0]

# Streamlit UI
st.title('Predizione Esito Partita')

st.header('Forza Squadra')
forzaA = st.number_input('Forza Squadra A', min_value=0, value=500)
forzaB = st.number_input('Forza Squadra B', min_value=0, value=95000)

st.header('Eroi Squadra A')
squadraA_heroes = [st.text_input(f'Eroe {i+1} Squadra A', '') for i in range(5)]

st.header('Eroi Squadra B')
squadraB_heroes = [st.text_input(f'Eroe {i+1} Squadra B', '') for i in range(5)]

if st.button('Predici Esito'):
    esito_predetto = predict_match(forzaA, forzaB, squadraA_heroes, squadraB_heroes, model)
    st.write(f"Esito predetto: {esito_predetto}")

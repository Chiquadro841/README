import streamlit as st
import pandas as pd
import joblib
import base64

# Carica il modello salvato
model_filename = 'random_forest_model.pkl'
model = joblib.load(model_filename)

# Lista degli eroi
heroes = ['estrilda', 'belinda', 'raine', 'fawkes', 'lucius', 'thane', 'hendrik', 'rowan', 'gwyneth', 'rosaline', 
          'cecilia', 'rigby', 'oscar', 'eluard', 'peggy', 'walker', 'morrow', 'scarlet', 'thaneA', 'sonia', 
          'palmer', 'belindaA', 'ginneas', 'jerome', 'luciusA', 'elyse', 'raoul', 'hogan', 'angelo', 'morvus', 
          'mirael', 'brutus', 'khasos', 'vurk', 'numisu', 'skreg', 'warek', 'antandra', 'safiya', 'satrana', 
          'tidus', 'drez', 'skriath', 'anoki', 'kren', 'thali', 'granit', 'thesku', 'alaro', 'anasta', 'brutusA', 
          'salaki', 'crassio', 'safiyaA', 'naroko', 'vika', 'villanelle', 'antandraA', 'ankhira', 'golus', 'saveas', 
          'nemora', 'kaz', 'lyca', 'tasi', 'ulmus', 'seirus', 'eironn', 'gorvo', 'lorsan', 'saurus', 'solise', 
          'peppi', 'respen', 'raku', 'mishka', 'astar', 'oku', 'eorin', 'soliseA', 'nevanthi', 'tamrus', 'trishea', 
          'lycaA', 'atheus', 'ira', 'ogi', 'arden', 'grezhul', 'shemira', 'thoran', 'isabella', 'nara', 'ferael', 
          'baden', 'kelthur', 'silas', 'oden', 'izold', 'torne', 'daimon', 'theowyn', 'desira', 'hodgkin', 'treznor', 
          'fane', 'kalene', 'badenA', 'edwin', 'ivan', 'shemiraA', 'simona', 'bronn', 'niru', 'silvina', 'vedan', 
          'athalia', 'elijah', 'orthros', 'talene', 'wukong', 'flora', 'zaphrael', 'alina', 'morael', 'titus', 
          'haelus', 'taleneA', 'audrae', 'tarnos', 'veithael', 'athaliaA', 'daemia', 'liberta', 'gavus', 'malkrie', 
          'ezizh', 'mehira', 'zolrath', 'khazard', 'mezoth', 'lucrezia', 'mortas', 'leofric', 'zikis', 'framton', 
          'ezizhA', 'vyloris', 'canisa', 'olgath', 'maetria', 'lucilla', 'sintonia', 'eugene', 'kalthin', 'nakoruru', 
          'arthur', 'ukyo', 'ezio', 'princeofpersia', 'albedo', 'ainz', 'queen', 'joker', 'merlino', 'leonardo', 
          'melusina', 'giovanna', 'geralt', 'yennefer', 'mulan', 'emilia', 'rem', 'robinhood', 'shuna', 'rimuru', 
          'hildwin', 'gwyneth2', 'nyla', 'pulina', 'cassio', 'melion', 'lan', 'none']

# Lista delle posizioni
positions = ['A1', 'A2', 'A3', 'A4', 'A5', 'B1', 'B2', 'B3', 'B4', 'B5']

# Definisci l'ordine delle colonne per il DataFrame di input
feature_columns = []
for pos in positions:
    for hero in heroes:
        feature_columns.append(f'{pos}_{hero}')
    feature_columns.append(f'{pos}_liv')
    
feature_columns.extend(['A_Attacco', 'B_Attacco'])




# Streamlit UI
st.title('Previsione dell\'Esito dell\'Incontro')

# Percorso dell'immagine
image_path = 'afkimage.jpg'


# Carica l'immagine e la converte in base64
with open(image_path, "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode()

# Aggiungi l'immagine centrata utilizzando HTML e CSS
st.markdown(
    f"""
    <div style="display: flex; justify-content: center;">
        <img src="data:image/jpeg;base64,{encoded_image}" style="width:300px;">
    </div>
    """,
    unsafe_allow_html=True
)

# Aggiungi un testo sotto l'immagine, centrato
st.markdown(
    """
    <div style="text-align: center; margin-top: 20px;">
        <p>Previsione Esito Incontro</p>
    </div>
    """,
    unsafe_allow_html=True
)
st.write("Benvenuto nell'app di previsione degli esiti degli incontri. Seleziona gli eroi e i rispettivi livelli, "
         "poi inserisci i livelli di attacco per ogni squadra. L'app utilizzerà il modello addestrato per prevedere "
         "l'esito dell'incontro.")

st.write(" Per la forza di squadra, si usa come base già K :"
         "es forza 5000K --> 5000"
         "50M --> 50000"
         "50B --> 50000000")

# Selezione e livello degli eroi per le posizioni
inputs = {col: 0 for col in feature_columns}

for pos in positions:
    st.subheader(f'Posizione {pos}')
    
    # Crea due colonne affiancate
    col1, col2 = st.columns(2)
    
    # Colonna per la selezione dell'eroe
    with col1:
        hero = st.selectbox(f'Eroe', options=[''] + heroes, key=f'hero_{pos}')
    
    # Colonna per l'inserimento del livello
    with col2:
        level = st.number_input(f'Livello', min_value=1, value=1, key=f'level_{pos}')
    
    # Imposta le colonne dummy e il livello dell'eroe
    for hero_name in heroes:
        inputs[f'{pos}_{hero_name}'] = 1 if hero == hero_name else 0
    inputs[f'{pos}_liv'] = level

# Attacco delle squadre
st.subheader('Livelli di Attacco')
attack_A = st.number_input('Livello Attacco Squadra A', min_value=0, value=0)
attack_B = st.number_input('Livello Attacco Squadra B', min_value=0, value=0)

# Aggiungi i livelli di attacco
inputs['A_Attacco'] = attack_A
inputs['B_Attacco'] = attack_B

# Prepara il DataFrame per la previsione
input_df = pd.DataFrame([inputs], columns=feature_columns)

# Previsione
if st.button('Prevedi Esito'):
    prediction = model.predict(input_df)[0]
    st.write(f'Esito previsto: {"Vittoria" if prediction == 1 else "Sconfitta"}')

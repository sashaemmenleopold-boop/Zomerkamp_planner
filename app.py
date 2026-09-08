import streamlit as st
from datetime import datetime, timedelta
import data_manager
import pdf_generator

st.set_page_config(page_title="Kamp Planner", page_icon="⛺", layout="wide")

# --- INITIALISATIE ---
if 'db' not in st.session_state:
    st.session_state.db = data_manager.load_data()

def save():
    data_manager.save_data(st.session_state.db)

# --- SIDEBAR: LEIDING & DAGEN ---
with st.sidebar:
    st.header("⛺ Kamp Instellingen")
    
    # Dagen Beheer
    st.subheader("Dagen")
    nieuwe_dag = st.text_input("Voeg dag toe (bijv. Dinsdag):")
    if st.button("Dag Toevoegen") and nieuwe_dag:
        if nieuwe_dag not in st.session_state.db['dagen']:
            st.session_state.db['dagen'][nieuwe_dag] = {
                "start_tijd": "08:00", "blokken": [], 
                "notulen": {"pluimen": "", "morgen": "", "kinderen": "", "nacht": ""}
            }
            save()
            st.rerun()
            
    dag_opties = list(st.session_state.db['dagen'].keys())
    huidige_dag = st.selectbox("Kies een dag:", dag_opties) if dag_opties else None

    # Leiding Beheer
    st.markdown("---")
    st.subheader("Team (Tags)")
    nieuwe_leiding = st.text_input("Naam leiding:")
    if st.button("Voeg leiding toe") and nieuwe_leiding:
        if nieuwe_leiding not in st.session_state.db['leiding']:
            st.session_state.db['leiding'].append(nieuwe_leiding)
            save()
            st.rerun()
    
    # Activiteiten Beheer (Nieuw)
    st.markdown("---")
    st.subheader("Activiteiten Presets")
    
    # Zorg dat de lijst bestaat in oude opgeslagen data
    if 'activiteiten' not in st.session_state.db:
        st.session_state.db['activiteiten'] = ["Ochtendgym", "Ontbijt", "Corvee", "Spel", "Koken", "Avondritueel", "Vrije invulling"]
        
    nieuwe_act = st.text_input("Nieuwe activiteit preset:")
    if st.button("Voeg activiteit toe") and nieuwe_act:
        if nieuwe_act not in st.session_state.db['activiteiten']:
            st.session_state.db['activiteiten'].append(nieuwe_act)
            save()
            st.rerun()
            
    with st.expander("Beheer huidige presets"):
        for act in st.session_state.db['activiteiten']:
            c_act1, c_act2 = st.columns([4, 1])
            c_act1.write(f"- {act}")
            if c_act2.button("❌", key=f"del_act_{act}"):
                st.session_state.db['activiteiten'].remove(act)
                save()
                st.rerun()
    st.write("Huidig team:")
    for l in st.session_state.db['leiding']:
        cols = st.columns([4, 1])
        cols[0].write(f"- {l}")
        if cols[1].button("❌", key=f"del_{l}", help=f"Verwijder {l}"):
            st.session_state.db['leiding'].remove(l)
            save()
            st.rerun()

# --- MAIN APP ---
if huidige_dag:
    dag_data = st.session_state.db['dagen'][huidige_dag]
    
    st.title(f"Planning: {huidige_dag}")
    
    # 1. Starttijd Config
    col_tijd, col_leeg = st.columns([1, 3])
    nieuwe_starttijd = col_tijd.text_input("Starttijd van de dag (HH:MM):", value=dag_data.get('start_tijd', '08:00'))
    if nieuwe_starttijd != dag_data.get('start_tijd'):
        dag_data['start_tijd'] = nieuwe_starttijd
        save()
        st.rerun()

    st.markdown("---")
    
    # 2. Blokken Weergave & Tijdlijn Herberekening
    st.subheader("Tijdlijn")
    
    berekende_blokken = []
    try:
        # Tijdlijn auto-calculation logic
        current_time = datetime.strptime(dag_data['start_tijd'], "%H:%M")
        
        for idx, blok in enumerate(dag_data['blokken']):
            eind_tijd = current_time + timedelta(minutes=blok['duur'])
            
            # Voeg berekende tijden toe voor weergave
            berekende_blokken.append({
                "idx": idx,
                "start": current_time.strftime("%H:%M"),
                "eind": eind_tijd.strftime("%H:%M"),
                **blok
            })
            
            current_time = eind_tijd
            
            # Weergave per rij (met st.container of columns)
            with st.container():
                c1, c2, c3, c4 = st.columns([1, 4, 2, 1])
                c1.write(f"**{berekende_blokken[-1]['start']} - {berekende_blokken[-1]['eind']}**")
                c2.write(f"**{blok['activiteit']}**  \n*{blok['details']}*")
                c3.write(", ".join(blok['leiding']))
                
                # Actie knoppen (Omhoog, Omlaag, Verwijderen)
                with c4:
                    cols_btn = st.columns(3)
                    if cols_btn[0].button("🔼", key=f"up_{idx}") and idx > 0:
                        dag_data['blokken'][idx], dag_data['blokken'][idx-1] = dag_data['blokken'][idx-1], dag_data['blokken'][idx]
                        save()
                        st.rerun()
                    if cols_btn[1].button("🔽", key=f"down_{idx}") and idx < len(dag_data['blokken']) - 1:
                        dag_data['blokken'][idx], dag_data['blokken'][idx+1] = dag_data['blokken'][idx+1], dag_data['blokken'][idx]
                        save()
                        st.rerun()
                    if cols_btn[2].button("🗑️", key=f"del_blok_{idx}"):
                        dag_data['blokken'].pop(idx)
                        save()
                        st.rerun()
                st.divider()
                
    except ValueError:
        st.error("Ongeldig tijdformaat. Gebruik HH:MM (bijv. 08:00)")

    # 3. Nieuw blok toevoegen
    with st.expander("➕ Nieuw onderdeel toevoegen", expanded=True):
        with st.form("add_blok_form"):
            c1, c2 = st.columns(2)
            activiteit = c1.selectbox("Activiteit:", ["Ochtendgym", "Ontbijt", "Corvee", "Spel", "Koken", "Avondritueel", "Vrije invulling", "Overig"])
            if activiteit == "Overig":
                activiteit = c1.text_input("Vrije tekst activiteit:")
                
            duur = c2.number_input("Duur (minuten):", min_value=5, max_value=240, step=5, value=30)
            details = st.text_input("Details / Aandachtspunten:")
            
            # Leiding selectie (Iedereen als standaardoptie erbij)
            leiding_opties = ["Iedereen"] + st.session_state.db['leiding']
            leiding_keuze = st.multiselect("Verantwoordelijke leiding:", leiding_opties, default=["Iedereen"])
            
            if st.form_submit_button("Voeg toe aan planning"):
                dag_data['blokken'].append({
                    "activiteit": activiteit,
                    "details": details,
                    "duur": duur,
                    "leiding": leiding_keuze
                })
                save()
                st.rerun()

    # 4. Notulen & Evaluatie Sectie
    st.markdown("---")
    st.subheader("Notulen & Sync Bespreking")
    
    n_data = dag_data.get('notulen', {})
    col_n1, col_n2 = st.columns(2)
    
    pluimen = col_n1.text_area("Wat ging goed / Pluimen 🏅", value=n_data.get('pluimen', ''))
    morgen = col_n1.text_area("Aandachtspunten voor morgen ⚠️", value=n_data.get('morgen', ''))
    kinderen = col_n2.text_area("Nabespreking kinderen/situaties 👦👧", value=n_data.get('kinderen', ''))
    nacht = col_n2.text_area("Avondritueel & nachtverdeling 🌙", value=n_data.get('nacht', ''))

    if st.button("💾 Notulen Opslaan"):
        dag_data['notulen'] = {
            "pluimen": pluimen, "morgen": morgen, "kinderen": kinderen, "nacht": nacht
        }
        save()
        st.success("Notulen succesvol opgeslagen!")

    # 5. Export naar PDF
    st.markdown("---")
    st.subheader("Exporteren")
    if st.button("Genereer Kampboekje PDF"):
        if berekende_blokken:
            pdf_buffer = pdf_generator.generate_pdf(huidige_dag, berekende_blokken, n_data)
            st.download_button(
                label="📄 Download PDF",
                data=pdf_buffer,
                file_name=f"Planning_{huidige_dag}.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("Voeg eerst blokken toe aan de planning voordat je een PDF genereert.")

import os
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="EDU-IA", page_icon="🌍", layout="centered")

st.title("🌍 EDU-IA")
st.subheader("Ton professeur virtuel pour apprendre")
st.caption("Prototype pilote — Burkina Faso. Les contenus et traductions doivent être vérifiés.")

with st.sidebar:
    st.header("Mon profil d'apprentissage")
    country = st.selectbox("Pays", ["Burkina Faso"])
    level = st.selectbox("Niveau", ["Primaire", "Collège", "Remise à niveau"])
    subject = st.selectbox("Matière", [
        "Histoire", "Géographie", "Français", "Mathématiques",
        "Sciences", "Culture et patrimoine", "Bambara", "Dioula", "Autre"
    ])
    language = st.selectbox("Langue de réponse", [
        "Français simple", "Bambara (à vérifier)", "Dioula (à vérifier)"
    ])
    style = st.selectbox("Style d'explication", [
        "Étape par étape", "Résumé court", "Exemple concret", "Quiz : une question à la fois"
    ])
    st.caption("Ne partage jamais de nom complet, d'adresse, de mot de passe ou d'information privée.")
    if st.button("Effacer la conversation"):
        st.session_state.messages = []
        st.rerun()

def instructions():
    return f"""
Tu es EDU-IA, un assistant éducatif conçu pour accompagner les élèves du primaire et du collège au Burkina Faso.
Pays : {country}. Niveau : {level}. Matière : {subject}.
Langue demandée : {language}. Style : {style}.

Règles :
- Explique simplement, avec des étapes et des exemples concrets adaptés au Burkina Faso.
- Ne prétends pas suivre un programme officiel sans avoir une source officielle vérifiée.
- Pour les programmes, dates d'examens et contenus qui changent, recommande de vérifier auprès des autorités éducatives.
- Distingue les faits historiques documentés, les traditions orales et les interprétations.
- Pour le bambara et le dioula, ne prétends pas être infaillible ; indique qu'une validation par un enseignant ou locuteur compétent peut être nécessaire.
- Dans un quiz, pose une seule question à la fois et attends la réponse de l'élève avant de corriger.
- Aide l'élève à comprendre au lieu de faire son travail à sa place.
- Ne demande pas d'informations personnelles.
- Si tu n'es pas sûr, dis-le et propose comment vérifier.
Réponds avec bienveillance, dans un langage adapté au niveau choisi.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if not st.session_state.messages:
    st.info("Essaie : « Explique-moi l'empire du Mali comme à un élève du collège, puis pose-moi 3 questions. »")

if prompt := st.chat_input("Pose ta question à EDU-IA…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # La clé peut être ajoutée dans Streamlit Cloud > App settings > Secrets,
    # ou fournie comme variable d'environnement sur un autre hébergeur.
    api_key = None
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        pass
    api_key = api_key or os.getenv("OPENAI_API_KEY", "")

    with st.chat_message("assistant"):
        if not api_key:
            answer = (
                "L'interface EDU-IA fonctionne, mais le moteur IA n'est pas encore connecté.\n\n"
                "Le propriétaire du site doit ajouter OPENAI_API_KEY dans les Secrets de l'hébergeur. "
                "Ne partage jamais cette clé dans le chat ni dans un dépôt public."
            )
            st.warning(answer)
        else:
            try:
                client = OpenAI(api_key=api_key)
                with st.spinner("EDU-IA prépare ta leçon…"):
                    response = client.responses.create(
                        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
                        instructions=instructions(),
                        input=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages[-10:]
                        ],
                    )
                    answer = response.output_text
                st.markdown(answer)
            except Exception:
                answer = (
                    "Je n'ai pas pu obtenir de réponse. Le propriétaire doit vérifier la clé API, "
                    "le crédit disponible, le nom du modèle et les journaux de l'application."
                )
                st.error(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})

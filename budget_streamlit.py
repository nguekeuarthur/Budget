import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Visualisation Budget", layout="centered")

st.title("📊 Répartition du budget - Contributions cumulées")

# Chemin vers ton fichier (à adapter si besoin)
fichier = "Suivi du Budget T3.xlsx"

# Chargement des données
try:
    df = pd.read_excel(fichier, sheet_name="Feuille 1", header=0)
except Exception as e:
    st.error(f"Erreur lors du chargement du fichier : {e}")
    st.stop()

# Vérification des colonnes
if 'Unnamed: 0' not in df.columns or 'Total Individuel' not in df.columns:
    st.error(f"Colonnes attendues non trouvées. Colonnes disponibles : {list(df.columns)}")
    st.stop()

# Nettoyage
# On s'assure que df est bien un DataFrame
if not isinstance(df, pd.DataFrame):
    st.error("Le fichier n'a pas été lu comme un DataFrame. Vérifiez le format du fichier.")
    st.stop()

df = df.dropna(subset=['Unnamed: 0'])
df = df[~df['Unnamed: 0'].astype(str).str.contains("Total|Code couleur", case=False, na=False)]
df = df[['Unnamed: 0', 'Total Individuel']]
df.columns = ['Nom', 'Total Individuel']
df['Total Individuel'] = pd.to_numeric(df['Total Individuel'], errors='coerce')
df = df.dropna(subset=['Total Individuel'])

# Regroupement des contributions par nom (au cas où un nom apparaît plusieurs fois)
df_grouped = df.groupby('Nom', as_index=False).sum(numeric_only=True)
total_general = df_grouped['Total Individuel'].sum()
df_grouped['Part (%)'] = (df_grouped['Total Individuel'] / total_general * 100).round(2)

# Tri par contribution décroissante
df_grouped = df_grouped.sort_values(by='Part (%)', ascending=False).reset_index(drop=True)

# Ajout du classement
# Le classement 1 = plus grande part
# On trie déjà par 'Part (%)' décroissant, donc on peut simplement ajouter une colonne

# Réinitialiser l'index pour avoir un classement 1, 2, 3...
df_grouped = df_grouped.reset_index(drop=True)
df_grouped['Classement'] = df_grouped.index + 1

# Réorganiser les colonnes pour mettre Classement en premier
cols = ['Classement', 'Nom', 'Total Individuel', 'Part (%)']
df_grouped = df_grouped[cols]

# Affichage du total général
st.markdown(f"**💰 Total général collecté : {total_general:,.0f}**")

# Affichage du tableau avec barre de progression sur la part (%)
st.subheader("🧾 Tableau des parts")
st.dataframe(
    df_grouped.style
        .bar(subset=['Part (%)'], color='#5fba7d')
        .format({'Total Individuel': '{:,.0f}', 'Part (%)': '{:.2f}%'}),
    use_container_width=True
)

# Graphique camembert
st.subheader("📈 Répartition en pourcentage")

fig, ax = plt.subplots()
ax.pie(df_grouped['Part (%)'].tolist(), labels=df_grouped['Nom'].astype(str).tolist(), autopct='%1.1f%%', startangle=90)
ax.axis('equal')  # Camembert circulaire
st.pyplot(fig)

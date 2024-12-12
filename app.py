from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Forcer matplotlib à utiliser un backend non interactif
import matplotlib.pyplot as plt
import io
import base64


app = Flask(__name__)
app.secret_key = 'secretkey'

# MongoDB Connection URL
uri = "mongodb+srv://papesene:8199969998@cluster0.41qkl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB
client = MongoClient(uri, server_api=ServerApi('1'))

db = client['final']
collection = db['immigration']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        country = request.form.get('Country', '').strip()
        continent = request.form.get('Continent', '').strip()
        region = request.form.get('Region', '').strip()

        # Vérification de la présence des critères
        query = {}
        if country:
            query['Country'] = {'$regex': f'^{country}$', '$options': 'i'}
        if continent:
            query['Continent'] = {'$regex': f'^{continent}$', '$options': 'i'}
        if region:
            query['Region'] = {'$regex': f'^{region}$', '$options': 'i'}

        # Recherche dans MongoDB
        result = collection.find_one(query)

        if result:
            return render_template('search.html', result=result, Country=country, Continent=continent, Region=region)
        else:
            flash("Aucun document trouvé correspondant à ces critères.")
            return render_template('search.html', result=None)
    
    return render_template('search.html', result=None)


# Route pour afficher et rechercher un document à mettre à jour
@app.route('/update', methods=['GET', 'POST'])
def update():
    record = None
    if request.method == 'POST':
        country = request.form.get('country', '').strip()
        # Rechercher un document par le pays
        record = collection.find_one({'Country': {'$regex': f'^{country}$', '$options': 'i'}})
        if not record:
            flash("Aucun document trouvé pour ce pays.")
    return render_template('update.html', record=record)

@app.route('/update_action', methods=['POST'])
def update_action():
    """Effectuer une mise à jour partielle sur un document."""
    country = request.form.get('country', '').strip()

    # Récupérer tous les champs modifiés depuis le formulaire
    updated_fields = {key: request.form.get(key, '').strip() for key in request.form.keys() if key not in ['country']}

    # Supprimer les champs vides
    updated_fields = {key: value for key, value in updated_fields.items() if value}

    if not updated_fields:
        flash("Aucune mise à jour à effectuer. Veuillez modifier au moins un champ.")
        return redirect(url_for('update'))

    try:
        # Mise à jour dans MongoDB
        result = collection.update_one(
            {'Country': country},  # Filtre par pays
            {'$set': updated_fields}  # Mettre à jour les champs spécifiés
        )

        if result.modified_count > 0:
            flash("Mise à jour effectuée avec succès.")
        else:
            flash("Aucune modification effectuée. Vérifiez les données et réessayez.")

    except Exception as e:
        flash(f"Erreur lors de la mise à jour : {e}")

    return redirect(url_for('update'))

# Route pour supprimer un champ ou le document entier
@app.route('/delete', methods=['POST'])
def delete():
    country = request.form.get('country', '').strip()
    field_to_delete = request.form.get('field_to_delete', '').strip()

    if field_to_delete:  # Si un champ spécifique doit être supprimé
        collection.update_one(
            {'Country': country},
            {'$unset': {field_to_delete: ""}}
        )
        flash(f"Champ '{field_to_delete}' supprimé avec succès.")
    else:  # Supprimer tout le document
        collection.delete_one({'Country': country})
        flash("Document supprimé avec succès.")

    return redirect(url_for('update'))


def encode_image():
    """Encode le graphique Matplotlib actuel en Base64."""
    buffer = io.BytesIO()  # Crée un buffer en mémoire pour enregistrer l'image
    plt.savefig(buffer, format='png')  # Sauvegarde le graphique dans le buffer au format PNG
    buffer.seek(0)  # Déplace le pointeur au début du buffer
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')  # Encode l'image en Base64
    buffer.close()  # Ferme le buffer
    plt.close()  # Ferme la figure Matplotlib pour libérer de la mémoire
    return image_base64

@app.route('/charts')
def charts():
    # Récupération des données depuis MongoDB
    documents = collection.find({}, {"Country": 1, "Total": 1, **{str(year): 1 for year in range(1980, 2014)}}).limit(10)
    
    countries = []
    totals = []
    yearly_data = {str(year): [] for year in range(1980, 2014)}

    for doc in documents:
        countries.append(doc.get("Country", ""))
        totals.append(int(doc.get("Total", 0)))  # On s'assure que le total est un entier

        for year in range(1980, 2014):
            # Convertir les valeurs en entier
            yearly_data[str(year)].append(int(doc.get(str(year), 0)))  # Force la conversion en int

    # Graphique en barres (Total par pays)
    plt.figure(figsize=(10, 6))
    plt.bar(countries, totals, color='skyblue')
    plt.xlabel('Country')
    plt.ylabel('Total')
    plt.title('Total par pays')
    plt.xticks(rotation=45)
    bar_chart = encode_image()

    # Graphique en lignes (Évolution des années 1980-2013)
    plt.figure(figsize=(12, 8))
    for year, data in yearly_data.items():
        plt.plot(countries, data, label=f"{year}")
    plt.xlabel('Country')
    plt.ylabel('Valeurs')
    plt.title('Évolution des données par pays (1980-2013)')
    plt.legend(fontsize="small", ncol=5)
    plt.xticks(rotation=45)
    line_chart = encode_image()

    # Histogramme (Distribution des Totals)
    plt.figure(figsize=(10, 6))
    plt.hist(totals, bins=10, color='purple', alpha=0.7)
    plt.xlabel('Total')
    plt.ylabel('Fréquence')
    plt.title('Distribution des Totals')
    histogram = encode_image()

    return render_template('charts.html', bar_chart=bar_chart, line_chart=line_chart, histogram=histogram)



@app.route('/ml')
def ml_page():
    # Chargement et nettoyage des données depuis MongoDB
    documents = list(collection.find({}, {"Total": 1, **{str(year): 1 for year in range(1980, 2014)}}))
    data = []

    for doc in documents:
        entry = {}
        for year in range(1980, 2014):
            entry[str(year)] = float(doc.get(str(year), 0))
        entry["Total"] = float(doc.get("Total", 0))
        data.append(entry)

    df = pd.DataFrame(data)
    df.fillna(0, inplace=True)  # Nettoyage
    df = df[(df.T != 0).any()]  # Supprimer les lignes nulles
    years = list(map(str, range(1980, 2014)))
    X = df[years]
    y = df["Total"]

    # Générer les graphiques
    lr_chart = generate_linear_regression_chart(X, y)
    knn_chart = generate_knn_chart(X, y)
    rf_chart = generate_random_forest_chart(X, y)

    return render_template(
        'ml.html',
        lr_chart=lr_chart,
        knn_chart=knn_chart,
        rf_chart=rf_chart
    )

def generate_linear_regression_chart(X, y):
    """Génère un graphique pour la régression linéaire avec MSE."""
    # Diviser les données en ensembles d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Créer et entraîner le modèle de régression linéaire
    model_lr = LinearRegression()
    model_lr.fit(X_train, y_train)

    # Prédictions sur l'ensemble de test
    predictions_lr = model_lr.predict(X_test)

    # Calcul du MSE
    mse_lr = mean_squared_error(y_test, predictions_lr)

    # Tracer les valeurs réelles et prédites
    plt.figure(figsize=(10, 6))
    plt.scatter(range(len(y_test)), y_test, color='blue', label='Réel (Test)', alpha=0.6)
    plt.scatter(range(len(predictions_lr)), predictions_lr, color='red', label='Régression linéaire (Prédictions)', alpha=0.6)
    plt.plot([0, len(y_test)], [y_test.mean(), y_test.mean()], 'k-',lw=4, label='Moyenne des réels')  # Ligne moyenne

    # Ajouter le titre avec le MSE
    plt.title(f"Régression Linéaire : Valeurs Réelles vs Prédictions\nMSE: {mse_lr:.2f}")
    plt.xlabel("Index des pays")
    plt.ylabel("Total d'immigrants")
    plt.legend()

    # Encoder le graphique en base64
    return encode_image()


def generate_knn_chart(X, y):
    """Génère un graphique pour KNN."""
    model_knn = KNeighborsClassifier(n_neighbors=5)
    y_class = (y > y.median()).astype(int)  # Classe 0 = faible, Classe 1 = élevé
    model_knn.fit(X, y_class)  # Entraîner le modèle KNN
    

    # Tracer les classes réelles et prédites
    plt.figure(figsize=(10, 6))
    plt.scatter(range(len(y_class)), y_class, color="blue", label="Classes réelles")  # Classes réelles en bleu
    plt.title("KNN : Classification des Totaux d'Immigration")
    plt.xlabel("Index des pays")
    plt.ylabel("Classe (0 = faible, 1 = élevé)")
    plt.legend()

    return encode_image()

def generate_random_forest_chart(X, y):
    """Génère un graphique pour Random Forest avec MSE."""
    # Diviser les données en ensembles d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Créer et entraîner le modèle Random Forest
    model_rf = RandomForestRegressor(n_estimators=100, random_state=42)
    model_rf.fit(X_train, y_train)

    # Prédictions sur l'ensemble de test
    predictions_rf = model_rf.predict(X_test)

    # Calcul du MSE
    mse_rf = mean_squared_error(y_test, predictions_rf)

    # Tracer les valeurs réelles et prédites
    plt.figure(figsize=(10, 6))
    plt.scatter(range(len(y_test)), y_test, color='blue', label='Réel (Test)', alpha=0.6)
    plt.scatter(range(len(predictions_rf)), predictions_rf, color='red', label='Random Forest (Prédictions)', alpha=0.6)
    plt.plot([0, len(y_test)], [y_test.mean(), y_test.mean()], 'k-',lw=4 , label='Moyenne des réels')  # Ligne moyenne

    # Ajouter le titre avec le MSE
    plt.title(f"Random Forest : Valeurs Réelles vs Prédictions\nMSE: {mse_rf:.2f}")
    plt.xlabel("Index des pays")
    plt.ylabel("Total d'immigrants")
    plt.legend()

    # Encoder le graphique en base64
    return encode_image()



@app.route('/classify', methods=['GET', 'POST'])
def classify():
    if request.method == 'POST':
        country = request.form.get('country')

        # Récupérer le document correspondant au pays
        document = collection.find_one({'Country': {'$regex': country, '$options': 'i'}})

        if document:
            # Extraire les données du document
            years = list(map(str, range(1980, 2014)))
            features = [float(document.get(year, 0)) for year in years]
            total = float(document.get('Total', 0))

            # Charger les données pour KNN
            documents = collection.find({}, {"Total": 1, **{str(year): 1 for year in range(1980, 2014)}})
            data = []
            for doc in documents:
                entry = {str(year): float(doc.get(str(year), 0)) for year in years}
                entry["Total"] = float(doc.get("Total", 0))
                data.append(entry)

            # Préparation du DataFrame
            df = pd.DataFrame(data)
            df["HighTotal"] = (df["Total"] > df["Total"].median()).astype(int)
            X = df[years]
            y = df["HighTotal"]

            # Entraînement du modèle KNN
            model_knn = KNeighborsClassifier(n_neighbors=3)
            model_knn.fit(X, y)

            # Prédiction pour le document donné
            prediction = model_knn.predict([features])[0]
            classe = 'Élevé' if prediction == 1 else 'Faible'

            return render_template('classify.html', country=country, classe=classe, total=total)

        else:
            flash("Aucun document trouvé pour ce pays.")
            return redirect(url_for('classify'))

    return render_template('classify.html', country=None, classe=None, total=None)

if __name__ == '__main__':
    app.run(debug=True)

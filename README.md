Ce projet consiste en une application web Flask permettant de visualiser, analyser, et classer les données d'immigration à partir d'une base de données hébergée dans MongoDB. L'application utilise des algorithmes d'apprentissage automatique pour effectuer des prédictions sur les données d'immigration (par exemple, classification basée sur le total d'immigrants d'un pays).

Table des matières
    a. Technologies utilisées
    b. Installation
    c. Fonctionnalités
        1. Recherche de pays
        2. Mise à jour des informations
        3. Visualisation des graphiques
        4. Apprentissage automatique
        5. Classification d'un document
    d. Exécution de l'application
    e. Structure des fichiers


    a. Technologies utilisées
Flask : Framework Python pour le développement web.
MongoDB : Base de données NoSQL utilisée pour stocker les données.
matplotlib : Bibliothèque Python utilisée pour la génération de graphiques.
scikit-learn : Bibliothèque d'apprentissage automatique pour la régression linéaire, KNN et Random Forest.
Pandas : Bibliothèque de manipulation de données utilisée pour gérer les ensembles de données.
HTML/CSS : Technologies utilisées pour l'interface utilisateur (UI).
JavaScript : Pour certaines interactions avec l'utilisateur.

    b. Installation
        1. Prérequis
Avant de commencer, assurez-vous que vous avez Python et pip installés sur votre machine. Vous aurez également besoin d'un accès à une instance MongoDB (par exemple via MongoDB Atlas).

        2. Étapes d'installation
Clonez ce projet depuis GitHub :

git clone https://github.com/Khokhane0/GestionEntrepot.git

Installez les dépendances : Assurez-vous d'avoir un environnement virtuel configuré, puis installez les dépendances via pip : pip install -r requirements.txt
Le fichier requirements.txt contient toutes les dépendances nécessaires :
Flask==2.2.2
pymongo==4.3.3
scikit-learn==1.2.2
matplotlib==3.7.0
pandas==2.1.3

Créez une base de données MongoDB : Si vous utilisez MongoDB Atlas, créez un cluster et obtenez l'URL de connexion. Modifiez ensuite l'URL de connexion dans app.py pour qu'elle pointe vers votre cluster MongoDB.

Exemple d'URL MongoDB :

uri = "mongodb+srv://<username>:<password>@cluster0.mongodb.net/immigration?retryWrites=true&w=majority"
Exécutez l'application : Pour démarrer le serveur local, exécutez :

python app.py

L'application sera accessible à l'adresse suivante : http://127.0.0.1:5000/.

    c. Fonctionnalités
1. Recherche de pays
L'utilisateur peut rechercher un pays spécifique dans la base de données en fournissant un nom de pays, un continent et une région. La recherche renverra un ou plusieurs résultats correspondant à ces critères.

2. Mise à jour des informations
Permet à l'utilisateur de rechercher un pays, puis de mettre à jour les informations associées à ce pays (par exemple, le total d'immigrants ou les années d'immigration). L'utilisateur peut également supprimer des informations pour un pays donné.

3. Visualisation des graphiques
L'application génère des graphiques pour explorer les données d'immigration :

Un diagramme en barres pour montrer les immigrants par pays.
Un graphique en ligne pour visualiser l'évolution des immigrants au fil des années.
Un histogramme pour examiner la distribution des totaux d'immigrants.

4. Apprentissage automatique
L'application applique trois algorithmes d'apprentissage automatique pour prédire la classe d'un pays :

Régression linéaire : Prédire la tendance du total d'immigrants au fil des années.
KNN (K-Nearest Neighbors) : Classer les pays en fonction du total d'immigrants comme étant "faible" ou "élevé".
Random Forest : Utilisé pour classifier les pays et prédire leur total d'immigrants.
Les utilisateurs peuvent accéder à ces modèles via un bouton dans l'interface.

5. Classification d'un document
L'utilisateur peut rechercher un pays, puis utiliser un modèle d'apprentissage automatique (KNN) pour déterminer si le total des immigrants pour ce pays est dans la classe faible (0) ou élevé (1). Le modèle KNN est entraîné sur les données de la base de données, et la classification s'affiche sur la page.

    
    d. Exécution de l'application
Démarrer l'application Flask : Exécutez la commande suivante pour démarrer le serveur local Flask :

python app.py

Naviguer dans l'application :

Accueil : Page d'accueil avec des liens vers les différentes sections.
Recherche : Effectuer une recherche de pays dans la base de données.
Mise à jour : Mettre à jour ou supprimer des informations sur un pays.
Graphiques : Voir les graphiques générés pour les données d'immigration.
Apprentissage automatique : Explorer les modèles d'apprentissage automatique appliqués aux données.

    e. Structure des fichiers

/projet final
│
├── /static
│   ├── style.css         # Styles personnalisés pour l'interface
│   ├── statistics.png    # Logo du projet
│   ├── ml.jpg            # Image du bouton pour accéder aux modèles d'apprentissage automatique
│
├── /templates
│   ├── base.html         # Template de base pour toutes les pages
│   ├── index.html        # Page d'accueil
│   ├── search.html       # Page de recherche de pays
│   ├── update.html       # Page de mise à jour des informations
│   ├── ml.html           # Page de visualisation des modèles d'apprentissage automatique
│   └── classify.html     # Page de classification des documents
│
├── app.py                # Code principal de l'application Flask
├── requirements.txt      # Liste des dépendances nécessaires
└── README.md             # Ce fichier

Merci d'avoir utilisé ce projet ! 😊 Si vous avez des questions ou des suggestions, n'hésitez pas à ouvrir un problème (issue) sur GitHub.
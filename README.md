# API de Crowdsourcing pour le Labeling

Une API REST Django pour la collecte et la validation collaborative d'annotations de données (texte et audio) via un système de consensus.

## Description

Cette plateforme permet :
- Aux **contributeurs** d'annoter des éléments de données avec des labels
- Aux **validateurs** d'approuver ou rejeter les annotations
- Le calcul automatique du **consensus** basé sur le vote majoritaire
- Le suivi des **statistiques** de performance des utilisateurs

## Architecture

### Modèles de données

- **User** : Utilisateur avec rôles (contributor, validator, admin)
- **DataItem** : Élément de données à annoter (texte ou audio)
- **Label** : Étiquettes disponibles pour l'annotation
- **Annotation** : Annotation d'un élément par un utilisateur
- **Validation** : Validation d'une annotation par un validateur

### Rôles utilisateurs

| Rôle | Permissions |
|------|-------------|
| `contributor` | Créer des annotations, consulter les données |
| `validator` | Valider/rejeter les annotations |
| `admin` | Gérer les labels, les utilisateurs et toutes les données |

## Installation

### Prérequis

- Python 3.12+
- PostgreSQL
- uv (gestionnaire de paquets Python)

### Configuration

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/Maxlil-code/crowdsourcing_labelling_api.git
   cd crowdsourcing_labelling_api
   ```

2. **Créer un environnement virtuel et installer les dépendances**
   ```bash
   uv venv
   uv pip install -e .
   ```

3. **Configurer les variables d'environnement**
   
   Créer un fichier `.env` à la racine du projet :
   ```bash
   cp .env.example .env
   ```
   
   Éditer le fichier `.env` avec vos paramètres :
   ```env
   SECRET_KEY=votre-clé-secrète-django-très-longue-et-aléatoire
   DEBUG=True
   
   DB_NAME=crowdsourcing_db
   DB_USER=postgres
   DB_PASSWORD=votre_mot_de_passe
   DB_HOST=localhost
   DB_PORT=5432
   ```

4. **Créer la base de données PostgreSQL**
   ```bash
   psql -U postgres
   CREATE DATABASE crowdsourcing_db;
   \q
   ```

5. **Appliquer les migrations**
   ```bash
   uv run python manage.py migrate
   ```

6. **Créer un superutilisateur**
   ```bash
   uv run python manage.py createsuperuser
   ```

7. **Lancer le serveur de développement**
   ```bash
   uv run python manage.py runserver
   ```

L'API est accessible sur `http://localhost:8000`

## Documentation API

### Documentation interactive

Une fois le serveur démarré, accédez à :
- **Swagger UI** : http://localhost:8000/api/docs/
- **ReDoc** : http://localhost:8000/api/redoc/
- **Schéma OpenAPI** : http://localhost:8000/api/schema/

### Authentification

L'API utilise **JWT (JSON Web Tokens)** pour l'authentification.

#### 1. Inscription (publique)
```http
POST /api/users/register/
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "MotDePasse123!",
  "password_confirm": "MotDePasse123!"
}
```

**Note** : Les utilisateurs créés via l'inscription publique ont automatiquement le rôle `contributor`.

#### 2. Connexion
```http
POST /api/login/
Content-Type: application/json

{
  "username": "john_doe",
  "password": "MotDePasse123!"
}
```

**Réponse** :
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### 3. Utiliser le token

Inclure le token `access` dans l'en-tête de chaque requête :
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Dans Swagger UI** : 
- Cliquer sur "Authorize"
- Entrer uniquement le token (sans "Bearer")
- Cliquer sur "Authorize"

#### 4. Renouveler le token
```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Endpoints principaux

#### Labels

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| GET | `/api/labels/` | Lister tous les labels | Authentifié |
| POST | `/api/labels/` | Créer un label | Admin |
| GET | `/api/labels/{id}/` | Détails d'un label | Authentifié |
| PUT/PATCH | `/api/labels/{id}/` | Modifier un label | Admin |
| DELETE | `/api/labels/{id}/` | Supprimer un label | Admin |

#### Éléments de données

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| GET | `/api/data-items/` | Lister les éléments actifs | Authentifié |
| GET | `/api/data-items/{id}/` | Détails d'un élément | Authentifié |
| GET | `/api/data-items/pending/` | Éléments non annotés par l'utilisateur | Authentifié |
| GET | `/api/data-items/{id}/progress/` | Progression de l'annotation | Authentifié |

#### Annotations

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| GET | `/api/annotations/` | Lister les annotations | Authentifié |
| POST | `/api/annotations/` | Créer une annotation | Contributor |
| GET | `/api/annotations/{id}/` | Détails d'une annotation | Authentifié |
| GET | `/api/annotations/{id}/consensus/` | Calculer le consensus | Authentifié |

#### Validations

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| GET | `/api/validations/` | Lister les validations | Validator |
| POST | `/api/validations/` | Créer une validation | Validator |
| GET | `/api/validations/{id}/` | Détails d'une validation | Validator |

#### Utilisateurs

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| POST | `/api/users/register/` | Inscription publique | Anonyme |
| GET | `/api/users/` | Lister les utilisateurs | Authentifié |
| GET | `/api/users/{id}/` | Détails d'un utilisateur | Authentifié |
| GET | `/api/users/{id}/stats/` | Statistiques d'annotation | Authentifié |

## Exemples d'utilisation

### 1. Créer un label
```bash
curl -X POST http://localhost:8000/api/labels/ \
  -H "Authorization: Bearer <votre_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Positif"}'
```

### 2. Lister les éléments en attente d'annotation
```bash
curl -X GET http://localhost:8000/api/data-items/pending/ \
  -H "Authorization: Bearer <votre_token>"
```

### 3. Créer une annotation
```bash
curl -X POST http://localhost:8000/api/annotations/ \
  -H "Authorization: Bearer <votre_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "item": 1,
    "label": 1
  }'
```

### 4. Valider une annotation
```bash
curl -X POST http://localhost:8000/api/validations/ \
  -H "Authorization: Bearer <votre_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "annotation": 1,
    "is_approved": true,
    "feedback": "Annotation correcte"
  }'
```

### 5. Obtenir le consensus pour un élément
```bash
curl -X GET http://localhost:8000/api/annotations/1/consensus/ \
  -H "Authorization: Bearer <votre_token>"
```

**Réponse** :
```json
{
  "consensus_label": "Positif",
  "confidence": "75.00%",
  "total_votes": 4
}
```

### 6. Consulter les statistiques d'un utilisateur
```bash
curl -X GET http://localhost:8000/api/users/1/stats/ \
  -H "Authorization: Bearer <votre_token>"
```

**Réponse** :
```json
{
  "user": "john_doe",
  "role": "contributor",
  "total_annotations": 25,
  "approved_annotations": 20,
  "rejected_annotations": 3,
  "pending_validations": 2,
  "precision": "80.00%"
}
```

### 7. Vérifier la progression d'un élément
```bash
curl -X GET http://localhost:8000/api/data-items/1/progress/ \
  -H "Authorization: Bearer <votre_token>"
```

**Réponse** :
```json
{
  "item_id": 1,
  "annotation_count": 5,
  "validated_count": 4,
  "approved_count": 3,
  "is_fully_validated": false,
  "validation_progress": "80.00%"
}
```

## Administration

Accéder au panneau d'administration Django : http://localhost:8000/admin/

Utilisez le superutilisateur créé lors de l'installation pour :
- Créer des utilisateurs avec des rôles spécifiques (validator, admin)
- Gérer les éléments de données
- Gérer les labels
- Visualiser toutes les annotations et validations

## Workflow typique

1. **Admin** : Crée des labels et importe des éléments de données
2. **Contributeur** : S'inscrit via `/api/users/register/`
3. **Contributeur** : Récupère les éléments en attente via `/api/data-items/pending/`
4. **Contributeur** : Crée des annotations pour chaque élément
5. **Validateur** : Consulte les annotations et les valide/rejette
6. **Système** : Calcule le consensus basé sur les votes majoritaires
7. **Admin/Utilisateurs** : Consultent les statistiques de performance

## Structure du projet

```
crowdsourcing_labelling_api/
├── core/                    # Configuration Django
│   ├── settings.py         # Paramètres du projet
│   ├── urls.py             # Routes principales
│   └── wsgi.py
├── labeling/               # Application principale
│   ├── models.py           # Modèles de données
│   ├── views.py            # ViewSets API
│   ├── serializers.py      # Sérialiseurs DRF
│   ├── permissions.py      # Permissions personnalisées
│   ├── urls.py             # Routes de l'app
│   ├── admin.py            # Configuration admin
│   └── migrations/         # Migrations de base de données
├── manage.py               # Script de gestion Django
├── pyproject.toml          # Dépendances du projet
├── .env.example            # Exemple de configuration
└── README.md               # Ce fichier
```

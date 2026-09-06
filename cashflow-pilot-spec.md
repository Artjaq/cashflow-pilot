# CASHFLOW-PILOT — Cahier des charges

> Gestionnaire de dépenses personnel, évolutif, avec IA branchable
> Stack : Vue 3 + FastAPI + PostgreSQL
> Hébergement cible : Raspberry Pi 5 (self-hosted)
> Dernière mise à jour : septembre 2026

---

## Contexte et positionnement

Le point de départ est un fichier Excel (`situation_financiere.xlsx`) construit à l'origine pour une situation financière ponctuelle (baisse temporaire de revenus, plans de paiement, prêt privé). Le projet **CashFlow-Pilot** en reprend la mécanique mais généralise le concept : un **gestionnaire de dépenses et de trésorerie pour la vie de tous les jours**, utilisable dans n'importe quelle situation (salarié, freelance, étudiant, etc.), pas seulement en gestion de crise.

Principes de conception :

- **Générique par défaut** : catégories, créanciers/marchands, types de dépenses sont configurables par l'utilisateur, pas figés dans le code
- **Quotidien et récurrent** : le système doit être aussi à l'aise pour suivre un café à 4.50 CHF que pour ventiler un plan de paiement sur 10 mois
- **IA branchable dès le départ** : l'architecture backend prévoit une interface d'abstraction pour connecter un ou plusieurs providers IA (Claude, autre) sans réécrire la logique métier — pas juste un chatbot ajouté à la fin
- **Import initial** : les données du fichier Excel (dépenses réelles, prêt en cours, etc.) servent de jeu de données de démarrage, importées comme des dépenses/plans ordinaires — rien de spécifique à la situation d'origine n'est modélisé en dur

L'objectif final : une app qui remplace un tableur, utilisable au quotidien pour suivre ses dépenses, anticiper sa trésorerie, et à terme se faire assister par une IA pour la saisie (scan de factures/mails) et l'analyse (conseils, questions en langage naturel).

---

## Conventions techniques globales

### Backend — FastAPI + Python

- Python 3.12+
- FastAPI avec async
- SQLAlchemy 2.0 (async, mapped_column)
- Alembic pour les migrations
- Pydantic v2 pour les schemas (validation + sérialisation)
- PostgreSQL 18 (pas de SQLite)
- Structure de dossier :

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app, CORS, lifespan
│   ├── config.py                # Settings via pydantic-settings (.env)
│   ├── db.py                    # async engine, sessionmaker, get_db
│   ├── models/
│   │   ├── __init__.py
│   │   ├── transaction.py       # dépenses ET revenus (voir 0.1)
│   │   ├── category.py
│   │   ├── payment_plan.py
│   │   ├── budget.py
│   │   ├── merchant.py
│   │   └── loan.py              # générique, aucun prêt nommé en dur
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── transaction.py
│   │   ├── category.py
│   │   ├── payment_plan.py
│   │   ├── dashboard.py
│   │   └── treasury.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── transactions.py
│   │   ├── categories.py
│   │   ├── payment_plans.py
│   │   ├── dashboard.py
│   │   ├── treasury.py
│   │   ├── budgets.py
│   │   ├── gmail.py             # Phase 2
│   │   └── assistant.py         # Phase 3
│   ├── services/
│   │   ├── __init__.py
│   │   ├── treasury.py          # logique calcul trésorerie
│   │   ├── dashboard.py         # agrégations dashboard
│   │   ├── gmail.py             # Phase 2
│   │   └── ai/                  # abstraction IA — voir section dédiée
│   │       ├── __init__.py
│   │       ├── base.py          # interface AIProvider
│   │       ├── claude_provider.py
│   │       └── tools.py         # tools exposés aux providers IA
├── alembic/
│   └── versions/
├── alembic.ini
├── scripts/
│   └── import_xlsx.py           # import initial du fichier Excel (données de démarrage)
├── requirements.txt
├── .env.example
└── Dockerfile
```

### Frontend — Vue 3

- Vue 3 Composition API (`<script setup>`)
- Vite comme bundler
- Pinia pour le state management
- Vue Router
- Tailwind CSS 3
- Axios pour les appels API
- Chart.js (via vue-chartjs) pour les graphiques
- Devise : CHF par défaut, champ configurable (voir Phase 4 pour multi-devises)
- Langue de l'interface : français
- Structure de dossier :

```
frontend/
├── src/
│   ├── App.vue
│   ├── main.js
│   ├── router/
│   │   └── index.js
│   ├── stores/
│   │   ├── transactions.js
│   │   ├── categories.js
│   │   ├── treasury.js
│   │   ├── budgets.js
│   │   └── dashboard.js
│   ├── views/
│   │   ├── DashboardView.vue
│   │   ├── TransactionsView.vue
│   │   ├── TreasuryView.vue
│   │   ├── PaymentPlansView.vue
│   │   ├── BudgetsView.vue
│   │   ├── CategoriesView.vue
│   │   ├── GmailView.vue        # Phase 2
│   │   └── AssistantView.vue    # Phase 3
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppSidebar.vue
│   │   │   ├── AppHeader.vue
│   │   │   └── AppLayout.vue
│   │   ├── dashboard/
│   │   │   ├── KpiCard.vue
│   │   │   ├── StatusChart.vue
│   │   │   ├── CategoryBreakdown.vue
│   │   │   ├── UpcomingDue.vue
│   │   │   └── RecentTransactions.vue
│   │   ├── transactions/
│   │   │   ├── TransactionTable.vue
│   │   │   ├── TransactionForm.vue
│   │   │   └── TransactionFilters.vue
│   │   ├── treasury/
│   │   │   ├── CashFlowTable.vue
│   │   │   └── CashFlowChart.vue
│   │   └── common/
│   │       ├── ConfirmDialog.vue
│   │       ├── StatusBadge.vue
│   │       └── CurrencyDisplay.vue
│   ├── api/
│   │   └── client.js            # instance axios + interceptors
│   ├── utils/
│   │   └── formatters.js        # formatage CHF, dates
│   └── assets/
├── tailwind.config.js
├── package.json
├── vite.config.js
└── Dockerfile
```

### Base de données PostgreSQL

Toutes les tables utilisent :
- `id` : UUID (gen_random_uuid)
- `created_at` : TIMESTAMPTZ DEFAULT now()
- `updated_at` : TIMESTAMPTZ DEFAULT now() (trigger on update)

Devise stockée en `NUMERIC(10,2)` — jamais de float pour de l'argent.

### Déploiement Raspberry Pi

- Docker Compose avec 3 services : `postgres`, `backend`, `frontend` (nginx)
- `.env` pour les secrets (DB_URL, clés API futures)
- Volumes persistants pour PostgreSQL
- Images ARM64-compatibles (PostgreSQL 16 Alpine OK nativement)

---

## PHASE 0 — Socle (fondations génériques + import des données)

### Objectif

Backend fonctionnel, modèle de données générique (pas lié à une situation particulière), et un script d'import qui migre les données du fichier Excel comme jeu de données de démarrage.

### 0.1 — Modèles de données

#### Table `categories`

Remplace l'enum figé — l'utilisateur peut créer/modifier ses catégories.

| Colonne     | Type          | Contraintes                          |
|-------------|---------------|---------------------------------------|
| id          | UUID          | PK                                    |
| name        | VARCHAR(50)   | UNIQUE NOT NULL                       |
| icon        | VARCHAR(50)   | NULLABLE (nom d'icône pour le frontend) |
| color       | VARCHAR(7)    | NULLABLE (hex, pour les graphiques)    |
| kind        | VARCHAR(20)   | NOT NULL — enum : expense, income      |

Catégories de démarrage (créées au seed, éditables) : Logement, Alimentation, Transport, Véhicule, Assurances, Télécom/Internet, Loisirs, Santé, Formation, Abonnements, Amendes/Poursuites, Autres — plus les catégories de revenus : Salaire, Freelance, Remboursement, Vente, Autres revenus.

#### Table `merchants` (optionnel mais utile pour le futur parsing IA/Gmail)

| Colonne     | Type          | Contraintes           |
|-------------|---------------|------------------------|
| id          | UUID          | PK                     |
| name        | VARCHAR(100)  | UNIQUE NOT NULL        |
| default_category_id | UUID | FK → categories, NULLABLE |
| email_domain_pattern | VARCHAR(100) | NULLABLE (ex: "*@assura.ch") |

#### Table `transactions`

Une seule table pour dépenses et revenus (différenciés par `kind`), pour que le modèle reste cohérent avec la notion générale de "mouvement d'argent" — plus simple à faire évoluer et à interroger par une IA.

| Colonne            | Type                     | Contraintes                                                                 |
|--------------------|--------------------------|-------------------------------------------------------------------------------|
| id                 | UUID                     | PK, default gen_random_uuid()                                               |
| kind               | VARCHAR(10)              | NOT NULL — enum : expense, income                                           |
| due_date           | DATE                     | NULLABLE                                                                    |
| description        | VARCHAR(255)             | NOT NULL                                                                    |
| amount             | NUMERIC(10,2)            | NOT NULL, CHECK > 0                                                         |
| category_id        | UUID                     | FK → categories, NOT NULL                                                   |
| merchant_id        | UUID                     | FK → merchants, NULLABLE                                                    |
| payment_method     | VARCHAR(100)             | NULLABLE                                                                    |
| status             | VARCHAR(20)              | NOT NULL, DEFAULT 'pending' — enum : pending, settled, installment          |
| priority           | SMALLINT                 | NULLABLE, CHECK BETWEEN 1 AND 5                                             |
| recurrence         | VARCHAR(20)              | NOT NULL, DEFAULT 'one_off' — enum : recurring, one_off, installment        |
| notes              | TEXT                     | NULLABLE                                                                    |
| settled_date       | DATE                     | NULLABLE                                                                    |
| created_at         | TIMESTAMPTZ              | DEFAULT now()                                                               |
| updated_at         | TIMESTAMPTZ              | DEFAULT now()                                                               |

#### Table `payment_plans`

| Colonne            | Type                     | Contraintes                                                                 |
|--------------------|--------------------------|-------------------------------------------------------------------------------|
| id                 | UUID                     | PK                                                                          |
| creditor           | VARCHAR(100)             | NOT NULL                                                                    |
| total_amount       | NUMERIC(10,2)            | NOT NULL                                                                    |
| installments       | SMALLINT                 | NOT NULL, CHECK > 0                                                         |
| monthly_amount     | NUMERIC(10,2)            | GENERATED ALWAYS AS (total_amount / installments)                          |
| start_month        | DATE                     | NOT NULL (1er du mois)                                                      |
| end_month          | DATE                     | calculé applicativement                                                     |
| transaction_id     | UUID                     | FK → transactions(id), NULLABLE — lien vers la transaction source           |
| created_at         | TIMESTAMPTZ              | DEFAULT now()                                                               |
| updated_at         | TIMESTAMPTZ              | DEFAULT now()                                                               |

#### Table `recurring_charges`

Charges fixes récurrentes (loyer, assurances, abonnements) — remplace les cellules bleues du Excel.

| Colonne            | Type            | Contraintes                                          |
|--------------------|-----------------|--------------------------------------------------------|
| id                 | UUID            | PK                                                    |
| label              | VARCHAR(100)    | NOT NULL                                              |
| amount             | NUMERIC(10,2)   | NOT NULL                                              |
| category_id        | UUID            | FK → categories                                       |
| active_from        | DATE            | NOT NULL                                              |
| active_until       | DATE            | NULLABLE (NULL = toujours actif)                       |
| frequency          | VARCHAR(20)     | NOT NULL, DEFAULT 'monthly' — enum : monthly, yearly  |

#### Table `budgets` (nouveau — pas dans le Excel d'origine, généralisation)

| Colonne            | Type            | Contraintes                                |
|--------------------|-----------------|---------------------------------------------|
| id                 | UUID            | PK                                          |
| category_id        | UUID            | FK → categories, NOT NULL                   |
| monthly_limit      | NUMERIC(10,2)   | NOT NULL                                    |
| created_at         | TIMESTAMPTZ     | DEFAULT now()                               |

Permet de suivre un budget par catégorie mois par mois (ex: max 300 CHF/mois en Loisirs) — utile pour un usage "vie de tous les jours" plutôt que crise budgétaire.

#### Table `loans` (générique — aucun prêt nommé en dur)

| Colonne         | Type           | Contraintes       |
|-----------------|----------------|--------------------|
| id              | UUID           | PK                |
| label           | VARCHAR(100)   | NOT NULL (ex: "Prêt privé A", "Prêt privé B") |
| total_amount    | NUMERIC(10,2)  | NOT NULL          |
| created_at      | TIMESTAMPTZ    | DEFAULT now()     |

#### Table `loan_repayments`

| Colonne       | Type           | Contraintes             |
|---------------|----------------|--------------------------|
| id            | UUID           | PK                       |
| loan_id       | UUID           | FK → loans, NOT NULL     |
| payment_date  | DATE           | NOT NULL                 |
| amount        | NUMERIC(10,2)  | NOT NULL                 |
| notes         | TEXT           | NULLABLE                 |
| created_at    | TIMESTAMPTZ    | DEFAULT now()            |

### 0.2 — Endpoints API (Phase 0)

Tous les endpoints sous `/api/v1/`.

#### Transactions

| Méthode | Route                       | Description                              |
|---------|------------------------------|--------------------------------------------|
| GET     | /transactions                | Liste avec filtres (kind, status, category, recurrence, month) + pagination |
| GET     | /transactions/{id}           | Détail                                   |
| POST    | /transactions                | Créer                                    |
| PUT     | /transactions/{id}           | Modifier                                 |
| PATCH   | /transactions/{id}/settle    | Marquer comme réglé                      |
| DELETE  | /transactions/{id}           | Supprimer                                |

#### Categories / Merchants

| Méthode | Route          | Description  |
|---------|----------------|--------------|
| GET/POST/PUT/DELETE | /categories | CRUD          |
| GET/POST/PUT/DELETE | /merchants  | CRUD          |

#### Payment Plans, Recurring Charges, Budgets, Loans

CRUD standard sur chaque ressource, même schéma que ci-dessus.

### 0.3 — Script d'import Excel

Fichier : `scripts/import_xlsx.py`

- Lit le fichier `situation_financiere.xlsx`
- Mappe les catégories Excel vers les nouvelles catégories génériques
- Peuple `transactions`, `payment_plans`, `recurring_charges`, `loans`/`loan_repayments`
- Idempotent, avec log de ce qui a été importé
- Sert de données de démarrage réalistes, pas de logique métier figée

### Critères d'acceptation Phase 0

- [ ] `docker compose up` lance les 3 services sans erreur
- [ ] Les catégories sont créées en base et modifiables via l'API
- [ ] Le script d'import peuple les transactions réelles depuis le Excel
- [ ] Chaque endpoint CRUD fonctionne (testable via Swagger UI `/docs`)
- [ ] Les montants sont en NUMERIC, jamais en float
- [ ] Rien dans le code n'est spécifique à une situation personnelle ou à un prêt nommé — tout est générique et paramétré en données

---

## PHASE 1 — Dashboard & Trésorerie (frontend)

### Objectif

Interface de suivi de dépenses quotidien : vue d'ensemble, historique, projection de trésorerie, suivi de budgets.

### 1.1 — Endpoints calculés

#### Dashboard

| Méthode | Route          | Description                                                       |
|---------|----------------|-----------------------------------------------------------------------|
| GET     | /dashboard     | KPIs généraux (voir champs ci-dessous)                             |

Champs retournés :
- `total_pending` : somme des transactions expense en attente
- `total_settled_this_month`
- `overdue_count`, `overdue_amount`
- `by_category` : répartition dépenses par catégorie (mois en cours)
- `current_month_balance` : revenus – dépenses du mois
- `cumulative_balance`
- `upcoming_transactions` : 5 prochaines échéances
- `recent_transactions` : dernières transactions réglées
- `budget_status` : par catégorie, consommé / limite (si un budget est défini)
- `loans_summary` : liste des prêts avec solde restant et progression

#### Trésorerie

| Méthode | Route                              | Description                          |
|---------|--------------------------------------|-----------------------------------------|
| GET     | /treasury?from=YYYY-MM&to=YYYY-MM    | Projection mensuelle sur la période  |

Champs par mois : charges récurrentes, mensualités plans, dépenses ponctuelles, total sorties, revenus attendus, solde du mois, solde cumulé.

### 1.2 — Pages frontend

#### Dashboard (`/`)
- KPI cards : reste à payer, réglé ce mois, en retard, solde cumulé
- Graphique donut : dépenses par catégorie (mois en cours)
- Graphique ligne : évolution du solde cumulé
- Bloc budgets : barres de progression par catégorie avec seuil
- Tableau : prochaines échéances
- Tableau : transactions récentes

#### Transactions (`/transactions`)
- Tableau avec tri/filtres (kind, statut, catégorie, récurrence, période)
- Ajout rapide (modale) — dépense ou revenu en un clic
- Marquer comme réglé, modifier, supprimer
- Vue "quotidien" : liste chronologique simple, façon relevé de compte

#### Trésorerie (`/treasury`)
- Tableau mensuel + graphique
- Alerte visuelle si solde cumulé négatif projeté

#### Plans de paiement (`/payment-plans`)
- Liste des plans actifs, grille mensuelle de ventilation

#### Budgets (`/budgets`)
- Définir un budget mensuel par catégorie
- Suivi visuel de consommation en temps réel

#### Catégories (`/categories`)
- Gestion des catégories et marchands (CRUD simple)

### Critères d'acceptation Phase 1

- [ ] Le dashboard reflète les vraies données importées
- [ ] La trésorerie projette correctement les mois futurs
- [ ] Un budget dépassé est visuellement signalé
- [ ] Ajouter une dépense quotidienne (ex: "café, 4.50 CHF, Alimentation") prend moins de 10 secondes dans l'UI
- [ ] L'app reste utilisable sans jamais toucher à du JSON/DB à la main

---

## PHASE 2 — Intégration Gmail

### Objectif

Détecter automatiquement les factures/reçus dans les emails et proposer leur ajout.

### 2.1 — Authentification Google

- OAuth2 (`google-auth-oauthlib`), scope `gmail.readonly`
- Token stocké en base (table `oauth_tokens`)

### 2.2 — Scan et parsing

#### Table `gmail_invoices`

| Colonne          | Type           | Description                                        |
|------------------|----------------|-------------------------------------------------------|
| id               | UUID           | PK                                                    |
| gmail_message_id | VARCHAR(100)   | Anti-doublon                                          |
| sender           | VARCHAR(255)   | Expéditeur                                            |
| subject          | VARCHAR(500)   | Sujet                                                 |
| received_date    | TIMESTAMPTZ    | Date de réception                                     |
| detected_amount  | NUMERIC(10,2)  | Montant détecté (NULLABLE)                            |
| detected_due_date| DATE           | Échéance détectée (NULLABLE)                          |
| detected_merchant_id | UUID       | FK → merchants, NULLABLE                              |
| status           | VARCHAR(20)    | pending / accepted / rejected                         |
| transaction_id   | UUID           | FK → transactions (rempli si accepté)                 |
| raw_snippet      | TEXT           | Extrait du mail pour vérification                     |
| created_at       | TIMESTAMPTZ    | DEFAULT now()                                         |

#### Parsing V1 : règles par marchand connu

Utilise la table `merchants.email_domain_pattern` pour matcher l'expéditeur → catégorie + créancier par défaut. Extraction du montant par regex sur le snippet.

> Cette étape peut être remplacée/complétée en Phase 3 par une extraction via IA (moins fragile que les regex, gère les formats inconnus).

#### Endpoints

| Méthode | Route                          | Description                                    |
|---------|-----------------------------------|-----------------------------------------------------|
| GET     | /gmail/status                  | Statut connexion OAuth                              |
| POST    | /gmail/auth                    | Initier le flow OAuth                               |
| GET     | /gmail/callback                | Callback OAuth                                      |
| POST    | /gmail/scan                    | Lancer un scan                                      |
| GET     | /gmail/invoices                | Liste des factures détectées                        |
| POST    | /gmail/invoices/{id}/accept    | Accepter → crée une transaction                     |
| POST    | /gmail/invoices/{id}/reject    | Rejeter                                             |

### 2.3 — Frontend

Page Gmail (`/gmail`) : connexion, scan, liste de factures détectées éditables avant validation.

### Critères d'acceptation Phase 2

- [ ] OAuth fonctionne
- [ ] Le scan détecte les factures des marchands connus
- [ ] L'acceptation crée une transaction correcte
- [ ] Pas de doublons au re-scan

---

## PHASE 3 — IA branchable

### Objectif

Rendre le système utilisable avec un ou plusieurs assistants IA, sans que la logique métier dépende d'un provider particulier.

### 3.1 — Architecture d'abstraction IA

L'idée centrale : une interface `AIProvider` dans `services/ai/base.py`, implémentée par `ClaudeProvider` (et potentiellement d'autres plus tard — OpenAI, modèle local via Ollama sur le Pi, etc.). Le reste de l'application ne parle jamais directement au SDK d'un provider — seulement à cette interface.

```python
# services/ai/base.py
from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    async def chat(self, message: str, history: list, tools: list) -> AsyncIterator[str]:
        """Retourne une réponse en streaming, avec support du tool use."""
        ...

    @abstractmethod
    async def extract_invoice_data(self, email_text: str) -> dict:
        """Extrait montant/date/marchand d'un texte d'email (remplace le regex Phase 2)."""
        ...

    @abstractmethod
    async def categorize_transaction(self, description: str, amount: float) -> str:
        """Suggère une catégorie pour une transaction."""
        ...
```

```python
# services/ai/claude_provider.py
class ClaudeProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        ...
```

Le choix du provider actif se fait via une variable d'environnement (`AI_PROVIDER=claude`), injecté par dependency injection FastAPI. Ça permet de tester avec un provider mock en dev, et de changer de modèle sans toucher au reste du code.

### 3.2 — Tools exposés au modèle conversationnel

```python
tools = [
    {"name": "get_dashboard", "description": "KPIs financiers actuels"},
    {"name": "get_transactions", "description": "Liste filtrable des transactions"},
    {"name": "get_treasury", "description": "Projection de trésorerie sur une période"},
    {"name": "get_payment_plans", "description": "Plans de paiement en cours"},
    {"name": "get_budget_status", "description": "Consommation des budgets par catégorie"},
    {"name": "simulate_expense", "description": "Simule l'impact d'une dépense hypothétique"},
]
```

### 3.3 — Cas d'usage IA

1. **Chat conversationnel** : questions en langage naturel sur les finances ("combien j'ai dépensé en loisirs ce mois-ci ?")
2. **Catégorisation automatique** : quand une transaction est créée sans catégorie (import Gmail, ajout rapide), l'IA suggère une catégorie basée sur la description
3. **Extraction Gmail améliorée** : remplace/complète les regex de la Phase 2 pour parser des factures dans des formats non prévus
4. **Recommandations proactives** (optionnel V1) : signaler un solde qui passerait en négatif, un budget dépassé

### 3.4 — Endpoints

| Méthode | Route                    | Description                                     |
|---------|----------------------------|------------------------------------------------------|
| POST    | /assistant/chat           | Chat streaming                                        |
| POST    | /assistant/categorize     | Suggestion de catégorie pour une transaction          |
| GET     | /assistant/history        | Historique (optionnel)                                |

### 3.5 — Frontend

Page Assistant (`/assistant`) : chat streaming, questions suggérées. Sur le formulaire de transaction, bouton "Suggérer une catégorie" qui appelle `/assistant/categorize`.

### Critères d'acceptation Phase 3

- [ ] Changer `AI_PROVIDER` dans `.env` ne casse rien (même si un seul provider est implémenté au départ)
- [ ] Le chat répond correctement en utilisant les tools sur les vraies données
- [ ] La catégorisation automatique propose une catégorie cohérente
- [ ] Le code métier (routers, services autres qu'IA) n'importe jamais directement le SDK Anthropic

---

## PHASE 4 — Évolutions futures (parking lot)

- **Open Banking** : import automatique des transactions bancaires (bLink, Contovista, ou équivalent)
- **Notifications** : Telegram bot ou PWA push (échéance proche, budget dépassé)
- **Multi-devises** : EUR pour revenus freelance à l'étranger, conversion automatique
- **Export PDF/CSV** : rapport mensuel
- **Multi-utilisateur** : auth JWT, partage avec un tiers (conseiller, partenaire)
- **Scan de documents papier** : OCR facture → transaction, via le provider IA
- **Provider IA local** : option Ollama tournant sur le Pi pour éviter les appels API externes sur les données sensibles
- **Application mobile** : PWA ou wrapper natif léger pour la saisie rapide en mobilité

---

## Notes pour Claude Code

### Comment utiliser ce document

1. **Phase 0** : setup Docker, modèles génériques, migrations, endpoints CRUD, script d'import
2. **Phase 1** : dashboard + trésorerie + budgets (frontend)
3. **Phase 2 et 3** : une fois la base solide — noter que la Phase 3 repose sur une interface `AIProvider` à respecter dès son introduction, pour rester agnostique du modèle utilisé

### Principes

- Générique avant tout : aucune règle métier ne doit référencer une situation personnelle particulière (nom de personne, statut spécifique, etc.) — tout passe par des données
- Pas de over-engineering : commence simple, itère
- Pas de mock data en dur dans le code : utilise l'import Excel comme jeu de données réel
- Tout doit tourner dans Docker sur Raspberry Pi 5 (ARM64)
- L'abstraction IA (Phase 3) doit être posée en interface dès sa première implémentation, même s'il n'y a qu'un seul provider au début

### Le fichier Excel source

Sert uniquement de données de démarrage à importer, pas de référence pour la modélisation. La logique des onglets "Trésorerie mensuelle" et "Plans de paiement" reste une bonne référence de calcul (les formules), mais les catégories et cas particuliers (prêt privé nommé, allocation spécifique) doivent être traités comme des données, pas comme des concepts du modèle.

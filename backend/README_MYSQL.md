# Migration vers MySQL

Ce document explique comment migrer le projet de SQLite vers MySQL.

## Prérequis

1. **MySQL Server 8.0+** installé et en cours d'exécution
2. **Python packages** installés : `pymysql`, `cryptography`

## Configuration

### 1. Variables d'environnement

Créez un fichier `.env` basé sur `.env.example` :

```bash
cp .env.example .env
```

Modifiez les variables MySQL dans `.env` :

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=sage_x3_user
MYSQL_PASSWORD=votre_mot_de_passe_mysql
MYSQL_DATABASE=sage_x3_db
DATABASE_URL=mysql+pymysql://sage_x3_user:votre_mot_de_passe_mysql@localhost:3306/sage_x3_db?charset=utf8mb4
```

### 2. Création de la base de données MySQL

#### Option A: Manuellement

```sql
-- Connexion en tant que root
mysql -u root -p

-- Création de la base de données
CREATE DATABASE sage_x3_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Création de l'utilisateur
CREATE USER 'sage_x3_user'@'localhost' IDENTIFIED BY 'votre_mot_de_passe_mysql';
CREATE USER 'sage_x3_user'@'%' IDENTIFIED BY 'votre_mot_de_passe_mysql';

-- Attribution des privilèges
GRANT ALL PRIVILEGES ON sage_x3_db.* TO 'sage_x3_user'@'localhost';
GRANT ALL PRIVILEGES ON sage_x3_db.* TO 'sage_x3_user'@'%';

-- Actualisation des privilèges
FLUSH PRIVILEGES;
```

#### Option B: Avec Docker

```bash
# Démarrer MySQL avec Docker Compose
docker-compose up -d mysql

# Attendre que MySQL soit prêt
docker-compose logs -f mysql
```

### 3. Installation des dépendances Python

```bash
pip install -r requirements.txt
```

### 4. Configuration initiale

```bash
# Créer les tables
python scripts/setup_mysql.py
```

### 5. Migration des données existantes (optionnel)

Si vous avez des données SQLite existantes :

```bash
# Migrer les données de SQLite vers MySQL
python scripts/migrate_to_mysql.py
```

## Utilisation avec Alembic (Migrations)

### Initialisation d'Alembic

```bash
# Initialiser Alembic (déjà fait)
alembic init alembic

# Créer une migration initiale
alembic revision --autogenerate -m "Initial migration"

# Appliquer les migrations
alembic upgrade head
```

### Gestion des migrations

```bash
# Créer une nouvelle migration
alembic revision --autogenerate -m "Description de la migration"

# Appliquer les migrations
alembic upgrade head

# Voir l'historique des migrations
alembic history

# Revenir à une migration précédente
alembic downgrade -1
```

## Déploiement avec Docker

### Développement

```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f sage_x3_app
```

### Production

1. Modifiez les mots de passe dans `docker-compose.yaml`
2. Utilisez des volumes persistants pour MySQL
3. Configurez les sauvegardes automatiques

## Optimisations MySQL

### Configuration recommandée

Dans `/etc/mysql/mysql.conf.d/mysqld.cnf` :

```ini
[mysqld]
# Optimisations pour Sage X3
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
max_connections = 200
query_cache_size = 64M
query_cache_type = 1

# Charset
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# Logs
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2
```

### Index recommandés

Les index sont automatiquement créés par les modèles SQLAlchemy :

- `sessions`: index sur `status`, `created_at`, `last_accessed`
- `inventory_items`: index sur `session_id`, `code_article`, `numero_lot`, `created_at`

## Sauvegarde et restauration

### Sauvegarde

```bash
# Sauvegarde complète
mysqldump -u sage_x3_user -p sage_x3_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Sauvegarde avec Docker
docker exec sage_x3_mysql mysqldump -u sage_x3_user -psage_x3_password sage_x3_db > backup.sql
```

### Restauration

```bash
# Restauration
mysql -u sage_x3_user -p sage_x3_db < backup.sql

# Restauration avec Docker
docker exec -i sage_x3_mysql mysql -u sage_x3_user -psage_x3_password sage_x3_db < backup.sql
```

## Monitoring

### Vérification de l'état

```bash
# Test de connexion
python -c "from database import db_manager; print('OK' if db_manager.health_check() else 'ERROR')"

# Statistiques MySQL
mysql -u sage_x3_user -p -e "SHOW STATUS LIKE 'Connections'; SHOW STATUS LIKE 'Queries';"
```

### Logs

- Application: `logs/inventory_processor.log`
- MySQL: `/var/log/mysql/error.log`
- Docker: `docker-compose logs mysql`

## Dépannage

### Erreurs courantes

1. **Connection refused**
   - Vérifiez que MySQL est démarré
   - Vérifiez les paramètres de connexion dans `.env`

2. **Access denied**
   - Vérifiez les identifiants MySQL
   - Vérifiez les privilèges de l'utilisateur

3. **Character set issues**
   - Assurez-vous d'utiliser `utf8mb4`
   - Vérifiez la configuration MySQL

4. **Performance lente**
   - Vérifiez les index
   - Augmentez `innodb_buffer_pool_size`
   - Analysez les requêtes lentes

### Commandes utiles

```bash
# Voir les processus MySQL
mysql -u root -p -e "SHOW PROCESSLIST;"

# Voir les variables de configuration
mysql -u root -p -e "SHOW VARIABLES LIKE 'innodb%';"

# Voir l'utilisation des index
mysql -u sage_x3_user -p sage_x3_db -e "SHOW INDEX FROM sessions;"
```
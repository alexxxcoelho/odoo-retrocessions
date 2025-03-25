#!/bin/bash

DB_CONTAINER="odoo_db"
ODOO_CONTAINER="odoo"
DB_NAME="odoo"
DB_USER="odoo"
FILESTORE_PATH="/home/odoo/.local/share/Odoo/filestore/$DB_NAME"

# Vérifie si les conteneurs existent
for container in "$DB_CONTAINER" "$ODOO_CONTAINER"; do
    if ! docker ps -a --format '{{.Names}}' | grep -q "^$container$"; then
        echo "❌ Conteneur $container introuvable" >&2
        exit 1
    fi
done

echo "🧨 Suppression des assets cassés en DB..."
for query in \
    "DELETE FROM ir_asset;" \
    "DELETE FROM ir_attachment WHERE url LIKE '/web/assets/%';" \
    "DELETE FROM ir_attachment WHERE url LIKE '%.[cj]s[s]?' OR name LIKE '%.[cj]s[s]?';" \
    "DELETE FROM ir_attachment WHERE name='web_icon_data';"; do
    if ! docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "$query"; then
        echo "❌ Erreur lors de l'exécution de '$query'" >&2
        exit 1
    fi
done

echo "🧹 Suppression complète du filestore..."
if [ -d "$FILESTORE_PATH" ]; then
    docker exec -u root $ODOO_CONTAINER bash -c "rm -rf $FILESTORE_PATH/*"
    docker exec -u root $ODOO_CONTAINER bash -c "chown -R odoo:odoo /home/odoo/.local/share/Odoo"
else
    echo "⚠️ Filestore introuvable à $FILESTORE_PATH" >&2
fi

echo "🔁 Recompilation des assets (dev mode activé)..."
if ! docker exec -i $ODOO_CONTAINER odoo -u base -d $DB_NAME --stop-after-init --dev=all; then
    echo "❌ Échec de la recompilation des assets" >&2
    exit 1
fi

echo "🚀 Redémarrage propre du conteneur..."
docker restart $ODOO_CONTAINER
sleep 5
if [ "$(docker inspect -f '{{.State.Running}}' $ODOO_CONTAINER)" != "true" ]; then
    echo "❌ Le conteneur $ODOO_CONTAINER n'a pas redémarré correctement" >&2
    exit 1
fi

echo "✅ Fini ! Recharge avec Ctrl+Shift+R en navigation privée pour tester."
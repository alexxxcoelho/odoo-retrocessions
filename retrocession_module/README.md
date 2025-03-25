# Retrocession Module (Odoo 18)

## 📦 Installation
1. Déposez le dossier `retrocession_module` dans votre dossier `/mnt/extra-addons`.
2. Redémarrez Odoo.
3. Activez le mode développeur.
4. Allez dans **Apps** > **Update App List** puis installez **Retrocession Management**.

## 📥 Importation Excel
1. Accédez à **Rétrocessions > Importations**
2. Cliquez sur **Créer** et remplissez :
   - Le **client** avec un taux de commission défini (dans sa fiche)
   - Le **distributeur** (facultatif)
   - Le **fichier Excel**
3. Cliquez sur **Importer le fichier**

## 📦 Mise a jour du dockerfile
docker build -t odoo-custom .
docker tag odoo-custom byterrr/odoo-custom:18.0
docker push byterrr/odoo-custom:18.0
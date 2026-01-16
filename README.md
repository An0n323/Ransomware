# Projet Ransomware Mathys Maréchal

Ce projet est un outil de simulation développé dans un cadre académique pour illustrer les mécanismes d'infection, d'exfiltration et de contrôle à distance d'un malware.

## 🛠️ Fonctionnalités implémentées

### Client (Malware)
* **Identification Unique** : Récupère l'UUID machine via `/proc/sys/kernel/random/uuid`.
* **Génération de Clé** : Création d'une clé de 32 caractères (A-Z) via `/dev/urandom`.
* **Chiffrement XOR Récursif** : Chiffre les fichiers du dossier cible de manière réversible.
* **Persistance Réseau** : Maintient une connexion TCP avec le serveur pour recevoir des ordres en temps réel.
* **Exécution de Commandes** : Exécute des commandes système (non-privilégiées) et renvoie la sortie au serveur.
* **Transferts de Fichiers** : Upload/Download optimisés par morceaux (chunks) avec gestion du symbole `~`.

### Serveur (C2)
* **Gestion Multi-victimes** : Utilisation du multithreading pour piloter plusieurs machines simultanément.
* **Stockage Persistant** : Sauvegarde des clés et IDs dans `victims.json`.
* **Console d'Administration** : Interface interactive pour envoyer des commandes spécifiques à chaque UUID.

## 🏗️ Architecture Globale
Le projet utilise une architecture **Client-Serveur** basée sur des sockets TCP. Le client initie la connexion (Reverse Shell) pour contourner les pare-feu standards.



## 📡 Protocole de Communication
Le protocole est structuré en trois types d'échanges :
1. **Exfiltration initial** : JSON contenant l'ID et la clé.
2. **Commandes Textes** : Format `COMMANDE|ARGUMENT`.
3. **Flux Binaires** : Transfert par blocs de 4 Ko précédé d'un en-tête de taille pour la fiabilité.

## 🚀 Comment lancer le projet
1. Lancez le serveur sur votre machine de contrôle : `python3 c2_server.py`
2. Lancez le malware sur la machine cible : `python3 malware.py`

## 🚀 Utilisation de la Console C2
Une fois le serveur et le client lancés, les commandes suivantes sont disponibles sur le serveur :

* **`list`** : Affiche la liste des UUID des machines actuellement connectées.
* **`crypt <uuid>`** : Lance le chiffrement XOR du dossier cible sur la machine spécifiée.
* **`decrypt <uuid>`** : Lance le déchiffrement XOR pour restaurer les fichiers.
* **`exec <uuid> <commande>`** : Exécute une commande système (ex: `whoami`, `ls -la`) et affiche le retour.
* **`upload <uuid> <chemin_distant>`** : Vole un fichier de la victime et l'enregistre dans `./exfiltrated_files/`.
* **`download <uuid> <chemin_local>`** : Envoie un fichier de votre serveur vers le dossier du client.
* **`exit`** : Ferme le serveur.

## ⚠️ Limites et Faiblesses
* **Algorithme XOR** : Vulnérable à l'attaque par clair connu (Known Plaintext Attack). Si $A \oplus B = C$, alors $C \oplus A = B$.
* **Flux en clair** : Absence de TLS/SSL, les données sont visibles via Wireshark.
* **Détection** : L'utilisation de `/dev/urandom` et de sockets bruts est facilement repérable par des outils d'analyse comportementale (EDR).

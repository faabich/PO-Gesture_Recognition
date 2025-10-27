# POO - Gesture-Recognition

## Description
Application de reconnaissance des mains et simulation de clicks / touche tacticle pour les portes ouvertes

## Démarrer le projet

### Pré-requis
* IDE utilisé (PyCharm)
* Package manager (pip)
* OS supporté (Windows 10 et Windows 11)
* Python v3.12.9

### Packets
* opencv-python
* customtkinter
* mediapipe
* ctypes
* pillow
* threading
* queue
* os

### Configuration
`pip install -r requirements.txt`


### Matériel requis
- 2 écrans (un pour l'affichage du jeux, un pour l'affichage de la webcam) 
- 1 caméra webcam
- 1 ordinateur

## Utilisation
### Mode "touchscreen"
Déplacer l'emplacement du "curseur" avec la main ouverte et appui tactile en fermant la main.

### Mode "souris"
Déplacer l'emplacement du curseur avec la main ouverte et appui tactile en fermant la main.

### Mode "volant"
Tourner à gauche ou à droite en simulant un volant et tourant dans le sens voulu. (accélération automatique)

### Mode "pong"
- Déplacer l'emplacement du curseur vers le haut en pointant l'index vers le haut et le reste de la main fermée
- Déplacer l'emplacement du curseur vers le bas en fermant la main
- Arrêter le déplacement du curseur et montrant la paume de la main

"""
Name:         main.py
Author:       Alex Kamano, Kilian Testard, Alexandre Ramirez, Nathan Filipowitz et Fabian Rostello
Date:         27.10.2025
Version:      0.1
Description:  Main file to launch the application
"""

from utils.hub import Hub

# Window resolution
width = 1600
height = 900

# Default camera resolution
cam_width = 1600
cam_height = 900

# Créer le hub principal
hub = Hub(width, height)

# lancer le hub
hub.mainloop()

# Fermer la caméra à la fin du programme
hub.camera.release()
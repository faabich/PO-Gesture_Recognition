from ui.hub import Hub

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
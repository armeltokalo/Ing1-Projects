import numpy as np
from pylab import *


L = 50  # Longueur de la grille en x
H = 20  # Hauteur de la grille en y
NbrePas = 10000  # Nombre de pas pour chaque particule
NbreParticles = 5000  # Nombre de particules

# Grille pour compter le nombre de passages à chaque point
grille = np.zeros((L, H))

def random_walk(x, y):
    # Choix aléatoire de direction : 0=haut, 1=bas, 2=droite, 3=gauche
    direction = np.random.randint(4)
    if direction == 0 and y < H - 1:  # haut
        y += 1
    elif direction == 1 and y > 0:  # bas
        y -= 1
    elif direction == 2 and x < L - 1:  # droite
        x += 1
    elif direction == 3 and x > 0:  # gauche
        x -= 1
    return x, y

for i in range(NbreParticles):
    # Initialisation de chaque particule au bord gauche (x = 0, y = position aléatoire)
    x, y = 0, np.random.randint(0, H)
    for i in range(NbrePas):
        # Enregistrement du passage dans la grille
        grille[x, y] += 1
        
        # Effectuer un pas aléatoire
        x, y = random_walk(x, y)
        
        
        # Bord gauche (x=0): Réinjection de particules
        if x == 0:
            grille[x, y] += 1  # Compte pour la réinjection
        # Bord droit (x=L): Absorption
        if x == L - 1:
            break  # La particule est absorbée et arrête de marcher
        # Bords supérieur (y=H-1) et inférieur (y=0): Réflexion
        if y == 0:
            y = 1  # Réflexion vers l'intérieur
        elif y == H - 1:
            y = H - 2  # Réflexion vers l'intérieur

# Normalisation de la grille pour obtenir une carte de probabilité
CarteProb = grille / np.sum(grille)

imshow(CarteProb.T, origin="lower", cmap="hot", aspect="auto")
colorbar(label="Probabilité Stationnaire")
title("Carte de Probabilité Stationnaire par Marche Aléatoire")
xlabel("Position x")
ylabel("Position y")
show()
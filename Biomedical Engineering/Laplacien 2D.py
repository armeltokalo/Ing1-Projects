#!/usr/bin/env python
# coding: utf-8

# In[12]:


import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import numpy as np

def create_matrix_A(M, N, dx, dy):
    """
    Crée la matrice A pour une grille de dimensions (M) x (N).
    
    Paramètres :
    - M : Nombre de divisions en direction x (i variant de 0 à M-1)
    - N : Nombre de divisions en direction y (j variant de 0 à N-1)
    - dx : Pas en x
    - dy : Pas en y
    
    Retourne :
    - A : Matrice de taille ((M) * (N)) x ((M) * (N))
    """
    # Taille de la matrice
    mat_size = (M) * (N)
    A = np.zeros((mat_size, mat_size))

    # Remplissage de la matrice A
    for i in range(0, M):
        for j in range(0, N):
            idx = i * (N ) + j  # Transformation (i, j) -> idx

            # Conditions de bord
            if i == 0 or i == M-1 :
                A[idx, idx] = 1
            elif  j==0 and i!=0 and i!=M-1 :
                A[idx,idx] = 1
                A[idx,idx+1] = -1
            elif  j==N-1 and i!=0 and i!=M-1 :
                A[idx,idx] = 1
                A[idx,idx-1] = -1
            else:
                # Coefficients internes selon les équations fournies
                A[idx, idx] = -2 * (1 / dx**2 + 1 / dy**2)
                A[idx, idx + 1] = 1 / dy**2  # Voisin de droite (i, j+1)
                A[idx, idx - 1] = 1 / dy**2  # Voisin de gauche (i, j-1)
                A[idx, idx + (N)] = 1 / dx**2  # Voisin en haut (i+1, j)
                A[idx, idx - (N)] = 1 / dx**2  # Voisin en bas (i-1, j)
    
    return A

def create (M,N,a,b,c,d):
    B=np.zeros(M*N)
    
    for i in range(0, M):
        for j in range(0, N):
            idx = i * (N ) + j
           
            if j== 0 and i!=0 and i!=M-1 :
                 B[idx]=c
            if j== N-1  and i!=0 and i!=M-1:
                 B[idx]=d
            if i==0:
                B[idx]=a
            if i== M-1:
                 B[idx]=b
    return B

L=50
D=60
M=100
N=100
a=0
b=1
c=0
d=0

dx=L/(M-1)
dy=D/(N-1)
R=create_matrix_A(M, N,dx , dy)
B=create (M,N,a,b,c,d)
F=np.linalg.solve(R,B)



x = np.linspace(0,L , M)  # Plage de valeurs pour x
y = np.linspace(0, D, N)  # Plage de valeurs pour y
X, Y = np.meshgrid(x, y)     # Crée une grille 2D à partir de x et y
    
Z = np.zeros((M, N))

for i in range(0, M):
        for j in range(0, N):
            Z[i,j]=F[i*N+j]
# Créer une figure 3D
fig = plt.figure(figsize=(12, 20))
ax = fig.add_subplot(111, projection='3d')

# Tracer la surface
ax.plot_surface(X, Y, Z.T, cmap='viridis')

# Ajouter des étiquettes
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('f(X, Y)')
ax.set_title('placien de f=0')

# Afficher le graphique
plt.show()


# In[13]:


plt.figure(figsize=(8, 6))
plt.contourf(X, Y, Z.T, 20, cmap='viridis')
plt.colorbar(label="Potentiel f(x, y)")
plt.title("Résolution de l'équation de Laplace en 2D")
plt.xlabel("x")
plt.ylabel("y")
plt.show()


# In[ ]:





# In[ ]:





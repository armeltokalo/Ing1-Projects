import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math


# creation de la fonction qui deforme des bloc de la matrice
def deformerb(A, h, li, lf, M, N, dx, dy, n):
    a = 1 / (dx * n)
    b = 1 / dx ** 2
    c = 1 / dy ** 2
    d = 1 / dx
    e = 1 / dy
    f = 1 / (dy * n)
    for i in range(M):
        for j in range(N):
            # Calcul de l'indice linéaire correspondant à la position (i, j)
            idx = i * N + j
            if j == h and li < i < lf:
                for m in range(3 * M * N):
                    A[idx, m] = 0
                    A[idx + M * N, m] = 0
                    A[idx + 2 * M * N, m] = 0
                A[idx, idx] = 1  # ux=0

                A[idx + M * N, idx + M * N] = 1  # uy=0

                A[idx + 2 * M * N, idx + M * N] = 1
                A[idx + 2 * M * N, i * N + j + 1 + M * N] = -1

            if j == h and (i == li):
                for m in range(3 * M * N):
                    A[idx, m] = 0
                    A[idx + M * N, m] = 0
                    A[idx + 2 * M * N, m] = 0
                A[idx, idx] = 1
                A[idx + M * N, idx + M * N] = 1

                A[2 * M * N + i * N + j, (i) * N + j] = -d
                A[2 * M * N + i * N + j, (i + 1) * N + j] = d

                A[2 * M * N + i * N + j, M * N + i * N + j + 1] = e
                A[2 * M * N + i * N + j, M * N + i * N + j] = -e
            if j == h and (i == lf):
                for m in range(3 * M * N):
                    A[idx, m] = 0
                    A[idx + M * N, m] = 0
                    A[idx + 2 * M * N, m] = 0
                A[idx, idx] = 1
                A[idx + M * N, idx + M * N] = 1

                A[2 * M * N + i * N + j, (i) * N + j] = -d
                A[2 * M * N + i * N + j, (i - 1) * N + j] = d

                A[2 * M * N + i * N + j, M * N + i * N + j + 1] = e
                A[2 * M * N + i * N + j, M * N + i * N + j] = -e
            if j == 0 and (i == li):
                for m in range(3 * M * N):
                    A[idx, m] = 0
                    A[idx + M * N, m] = 0
                    A[idx + 2 * M * N, m] = 0

                A[idx, idx] = 1
                A[idx + M * N, idx + M * N] =1
                # ns
                A[2 * M * N + i * N + j, M * N + i * N + j] = -2 * (b)
                A[2 * M * N + i * N + j, M * N + i * N + j + 2] = c
                A[2 * M * N + i * N + j, M * N + i * N + j] = c
                A[2 * M * N + i * N + j, M * N + (i + 1) * N + j] = b
                A[2 * M * N + i * N + j, M * N + (i - 1) * N + j] = b
                A[2 * M * N + i * N + j, 2 * N * M + i * N + j] = f
                A[2 * M * N + i * N + j, 2 * N * M + (i) * N + (j + 1)] = -f
                A[2 * M * N + i * N + j, M * N + i * N + j + 1] = -2 * (c)
            if j == 0 and (i == lf):
                for m in range(3 * M * N):
                    A[idx, m] = 0
                    A[idx + M * N, m] = 0
                    A[idx + 2 * M * N, m] = 0

                A[idx, idx] = 1
                A[idx + M * N, idx + M * N] = 1
                #ns
                A[2 * M * N + i * N + j, M * N + i * N + j] = -2 * (b)
                A[2 * M * N + i * N + j, M * N + i * N + j + 2] = c
                A[2 * M * N + i * N + j, M * N + i * N + j] = c
                A[2 * M * N + i * N + j, M * N + (i + 1) * N + j] = b
                A[2 * M * N + i * N + j, M * N + (i - 1) * N + j] = b
                A[2 * M * N + i * N + j, 2 * N * M + i * N + j] = f
                A[2 * M * N + i * N + j, 2 * N * M + (i) * N + (j + 1)] = -f
                A[2 * M * N + i * N + j, M * N + i * N + j + 1] = -2 * (c)

            if i == li and 0 < j < h:
                for m in range(3 * M * N):
                    A[idx, m] = 0
                    A[idx + M * N, m] = 0
                    A[idx + 2 * M * N, m] = 0
                A[idx, idx] = 1
                A[idx + M * N, idx + M * N] = 1

                A[idx + 2 * M * N, idx] = 1
                A[idx + 2 * M * N, (i - 1) * N + j] = -1

            if i == lf and 0 < j < h:
                for m in range(3 * M * N):
                    A[idx, m] = 0
                    A[idx + M * N, m] = 0
                    A[idx + 2 * M * N, m] = 0

                A[idx, idx] = 1
                A[idx + M * N, idx + M * N] = 1

                A[idx + 2 * M * N, idx] = 1
                A[idx + 2 * M * N, (i + 1) * N + j] = -1

            if li < i < lf and j < h:
                for m in range(3 * M * N):
                    A[idx, m] = 0
                    A[idx + M * N, m] = 0
                    A[idx + 2 * M * N, m] = 0

                A[idx, idx] = 1
                A[idx + M * N, idx + M * N] = 1
                A[idx + 2 * M * N, idx + 2 * M * N] = 1

    return A


def deformerh(A, h, li, lf, M, N, dx, dy, n):
    a = 1 / (dx * n)
    b = 1 / dx ** 2
    c = 1 / dy ** 2
    d = 1 / dx
    e = 1 / dy
    f = 1 / (dy * n)
    for i in range(M):
        for j in range(N):
            # Calcul de l'indice linéaire correspondant à la position (i, j)
            idx = i * N + j
            if j == N - 1 - h and li < i < lf:
                for m in range(3 * M * N):
                    A[idx, m] = 0
                    A[idx + M * N, m] = 0
                    A[idx + 2 * M * N, m] = 0
                A[idx, idx] = 1  # ux=0

                A[idx + M * N, idx + M * N] = 1  # uy=0

                A[idx + 2 * M * N, idx + M * N] = 1
                A[idx + 2 * M * N, i * N + j - 1 + M * N] = -1

            if j == N - 1 - h and (i == li):
                for m in range(3 * M * N):
                    A[idx, m] = 0
                    A[idx + M * N, m] = 0
                    A[idx + 2 * M * N, m] = 0
                A[idx, idx] = 1
                A[idx + M * N, idx + M * N] = 1

                A[2 * M * N + i * N + j, (i) * N + j] = -d
                A[2 * M * N + i * N + j, (i + 1) * N + j] = d

                A[2 * M * N + i * N + j, M * N + i * N + j - 1] = e
                A[2 * M * N + i * N + j, M * N + i * N + j] = -e
            if j == N - 1 - h and (i == lf):
                for m in range(3 * M * N):
                    A[idx, m] = 0
                    A[idx + M * N, m] = 0
                    A[idx + 2 * M * N, m] = 0
                A[idx, idx] = 1
                A[idx + M * N, idx + M * N] = 1

                A[2 * M * N + i * N + j, (i) * N + j] = -d
                A[2 * M * N + i * N + j, (i - 1) * N + j] = d

                A[2 * M * N + i * N + j, M * N + i * N + j - 1] = e
                A[2 * M * N + i * N + j, M * N + i * N + j] = -e
            if j == N - 1 and (i == li):
                for m in range(3 * M * N):
                    A[idx, m] = 0
                    A[idx + M * N, m] = 0
                    A[idx + 2 * M * N, m] = 0
                A[idx, idx] = 1
                A[idx + M * N, idx + M * N] = 1
                #ns
                A[2 * M * N + i * N + j, M * N + i * N + j] = -2 * (b)
                A[2 * M * N + i * N + j, M * N + i * N + j - 2] = c
                A[2 * M * N + i * N + j, M * N + i * N + j] = c
                A[2 * M * N + i * N + j, M * N + (i + 1) * N + j] = b
                A[2 * M * N + i * N + j, M * N + (i - 1) * N + j] = b
                A[2 * M * N + i * N + j, 2 * N * M + i * N + j] = f
                A[2 * M * N + i * N + j, 2 * N * M + (i) * N + (j + 1)] = -f
                A[2 * M * N + i * N + j, M * N + i * N + j - 1] = -2 * (c)

            if j == N - 1 and (i == lf):
                for m in range(3 * M * N):
                    A[idx, m] = 0
                    A[idx + M * N, m] = 0
                    A[idx + 2 * M * N, m] = 0
                A[idx, idx] = 1
                A[idx + M * N, idx + M * N] = 1
                #ns
                A[2 * M * N + i * N + j, M * N + i * N + j] = -2 * (b)
                A[2 * M * N + i * N + j, M * N + i * N + j - 2] = c
                A[2 * M * N + i * N + j, M * N + i * N + j] = c
                A[2 * M * N + i * N + j, M * N + (i + 1) * N + j] = b
                A[2 * M * N + i * N + j, M * N + (i - 1) * N + j] = b
                A[2 * M * N + i * N + j, 2 * N * M + i * N + j] = f
                A[2 * M * N + i * N + j, 2 * N * M + (i) * N + (j + 1)] = -f
                A[2 * M * N + i * N + j, M * N + i * N + j - 1] = -2 * (c)

            if i == li and N - 1 - h < j < N - 1:
                for m in range(3 * M * N):
                    A[idx, m] = 0
                    A[idx + M * N, m] = 0
                    A[idx + 2 * M * N, m] = 0
                A[idx, idx] = 1
                A[idx + M * N, idx + M * N] = 1

                A[idx + 2 * M * N, idx] = 1
                A[idx + 2 * M * N, (i - 1) * N + j] = -1

            if i == lf and N - 1 - h < j < N - 1:
                for m in range(3 * M * N):
                    A[idx, m] = 0
                    A[idx + M * N, m] = 0
                    A[idx + 2 * M * N, m] = 0

                A[idx, idx] = 1
                A[idx + M * N, idx + M * N] = 1

                A[idx + 2 * M * N, idx] = 1
                A[idx + 2 * M * N, (i + 1) * N + j] = -1

            if li < i < lf and N - 1 - h < j:
                for m in range(3 * M * N):
                    A[idx, m] = 0
                    A[idx + M * N, m] = 0
                    A[idx + 2 * M * N, m] = 0

                A[idx, idx] = 1
                A[idx + M * N, idx + M * N] = 1
                A[idx + 2 * M * N, idx + 2 * M * N] = 1

    return A


def matrice_A(M, N, dx, dy, n, h, li, lf):
    a = 1 / (dx * n)
    b = 1 / dx ** 2
    c = 1 / dy ** 2
    d = 1 / dx
    e = 1 / dy
    f = 1 / (dy * n)

    """
    Crée la matrice A d'ordre 3*M*N pour une discrétisation en 2D.

    Paramètres :
    M (int): Nombre de lignes de la grille.
    N (int): Nombre de colonnes de la grille.

    Retourne :
    np.ndarray: La matrice A d'ordre 3*M*N.

    """

    # creation de la fonction qui deforme des bloc de la matrice

    # Création de la matrice A de taille 3*M*N x 3*M*N initialisée à zéro
    A = np.zeros((3 * M * N, 3 * M * N))

    # Boucle pour remplir la matrice A
    for i in range(M):
        for j in range(N):
            # Calcul de l'indice linéaire correspondant à la position (i, j)
            idx = i * N + j
            # Conditions aux bords pour la discrétisation
            # deformation creer un ensemble de
            # deformer(A,h,li,lf,M,N,dx,dy,n)
            # deformer(A,h+1,lf,lf+3,M,N,dx,dy,n)

            if j == 0:
                A[idx, idx] = 1
                A[idx + M * N, idx + M * N] = 1
                A[idx + 2 * M * N, idx + M * N] = 1
                A[idx + 2 * M * N, i * N + j + 1 + M * N] = -1
            if j == N - 1:
                A[idx, idx] = 1
                A[idx + M * N, idx + M * N] = 1
                A[idx + 2 * M * N, idx + M * N] = 1
                A[idx + 2 * M * N, i * N + j - 1 + M * N] = -1

            if i == 0 or (j == 0 and i == 0) or (j == N - 1 and i == 0):
                #
                A[idx, idx] = 1
                A[idx, (M - 1) * N + j] = -1

                A[idx + M * N, idx + M * N] = 1
                A[idx + M * N, (M - 1) * N + j + M * N] = -1

                A[idx + 2 * M * N, idx + 2 * M * N] = 1
            if i == M - 1 or (j == 0 and i == M - 1) or (j == N - 1 and i == M):
                A[idx, idx] = 1
                A[idx, (i - 1) * N + j] = -1
                A[idx, j] = 1
                A[idx, N + j] = -1

                A[idx + M * N, idx + M * N] = 1
                A[idx + M * N, (i) * N + (j - 1) + M * N] = -1
                A[idx + M * N, j + M * N] = 1
                A[idx + M * N, (j - 1) + M * N] = -1
                # A[idx, idx ] = 1
                # A[idx, j ] = -1
                A[idx + 2 * M * N, idx + 2 * M * N] = 1
            if j != 0 and j != N - 1 and i != 0 and i != M - 1:  # and not( (li<=i<=lf and j<=h) or () or () ): #navier stokes l'interieur

                A[i * N + j, i * N + j] = -2 * (b + c)
                A[i * N + j, i * N + j + 1] = c
                A[i * N + j, i * N + j - 1] = c
                A[i * N + j, (i + 1) * N + j] = b
                A[i * N + j, (i - 1) * N + j] = b
                A[i * N + j, 2 * N * M + (i - 1) * N + j] = a / 2
                A[i * N + j, 2 * N * M + (i + 1) * N + j] = -a / 2

                A[M * N + i * N + j, M * N + i * N + j] = -2 * (b + c)
                A[M * N + i * N + j, M * N + i * N + j + 1] = c
                A[M * N + i * N + j, M * N + i * N + j - 1] = c
                A[M * N + i * N + j, M * N + (i + 1) * N + j] = b
                A[M * N + i * N + j, M * N + (i - 1) * N + j] = b
                A[M * N + i * N + j, 2 * N * M + i * N + j - 1] = f / 2
                A[M * N + i * N + j, 2 * N * M + (i) * N + (j + 1)] = -f / 2

                A[2 * M * N + i * N + j, 2 * M * N + i * N + j] = -2 * (1 / dx ** 2 + 1 / dy ** 2)
                A[2 * M * N + i * N + j, 2 * M * N + i * N + j + 1] = 1 / dy ** 2  # Voisin de droite (i, j+1)
                A[2 * M * N + i * N + j, 2 * M * N + i * N + j - 1] = 1 / dy ** 2  # Voisin de gauche (i, j-1)
                A[2 * M * N + i * N + j, 2 * M * N + (i + 1) * N + j] = 1 / dx ** 2  # Voisin en haut (i+1, j)
                A[2 * M * N + i * N + j, 2 * M * N + (i - 1) * N + j] = 1 / dx ** 2

    # déformations basses
    deformerb(A,h+4,lf+3,lf+5,M,N,dx,dy,n)
    deformerb(A, h + 6, lf + 8, lf + 10, M, N, dx, dy, n)
    deformerb(A,h+2,li,lf,M,N,dx,dy,n)

    # déformations hautes
    deformerh(A,h+4,lf+3,lf+5,M,N,dx,dy,n)
    deformerh(A,h+6,lf+8,lf+10,M,N,dx,dy,n)
    deformerh(A,h+2,li,lf,M,N,dx,dy,n)

    return A


def create(M, N, P1, P2):
    B = np.zeros(3 * M * N)

    for i in range(0, M):
        for j in range(0, N):
            idx = i * N + j

            if i == 0:
                B[idx + 2 * M * N] = P1

            elif i == M - 1:
                B[idx + 2 * M * N] = P2
    return B


L = 5.32 * 1e-2
D = 7.54 * 1e-3
M = 40
N = 40
h = 2  # paire
li = 4
lf = 6
P1 = 10 * 1e-2
P2 = 0

n = 1.81 # n=1.81*1e-5
dx = L / (M - 1)
dy = D / (N - 1)
R = matrice_A(M, N, dx, dy, n, h, li, lf)
B = create(M, N, P1, P2)

# F= np.linalg.pinv(R).dot(B)
F = np.linalg.solve(R, B)
x = np.linspace(0, L, M)  # Plage de valeurs pour x
y = np.linspace(0, D, N)  # Plage de valeurs pour y
X, Y = np.meshgrid(x, y)  # Crée une grille 2D à partir de x et y

Zux = np.zeros((M, N))
Zuy = np.zeros((M, N))
Zp = np.zeros((M, N))

for i in range(0, M):
    for j in range(0, N):
        Zux[i, j] = F[i * N + j]

for i in range(0, M):
    for j in range(0, N):
        Zuy[i, j] = F[N * M + i * N + j]

for i in range(0, M):
    for j in range(0, N):
        Zp[i, j] = F[2 * N * M + i * N + j]


def d(Zux, Zuy, M):
    d = np.zeros(M)
    for i in range(M):
        for j in range(N):
            d[i] += np.sqrt(Zux[i, j] ** 2 + Zuy[i, j] ** 2) * D / (N - 1)
    return d


def cad(values):
    # Calcul de la moyenne
    mean = sum(values) / len(values)

    # Calcul de l'écart type
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    std_dev = math.sqrt(variance)

    return (mean, std_dev)


# Créer une figure 3D placien
fig = plt.figure(figsize=(12, 20))
ax = fig.add_subplot(111, projection='3d')

# Tracer la surface
ax.plot_surface(X, Y, Zp.T, cmap='viridis')

# Ajouter des étiquettes
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('f(X, Y)')
ax.set_title('pression')

# Afficher le graphique direction noire
plt.figure(figsize=(10, 8))
plt.show()
plt.pcolormesh(X, Y, Zp.T * 1e2)
plt.colorbar(label="Pression en 10**(2) Pa")
plt.quiver(X, Y, Zux.T, Zuy.T)
plt.title(f"P1={P1}, P2={P2},ε={cad(d(Zux, Zuy, M))[0]} , Dmoy={cad(d(Zux, Zuy, M))[1]} ")
plt.xlabel(f"M={M},  L={L}")
plt.ylabel(f"N={N},  D={D}")
plt.show()
# Calculer la magnitude de la vitesse
velocity_magnitude = np.sqrt(Zux ** 2 + Zuy ** 2)

# Tracer le champ de la magnitude de la vitesse
plt.figure(figsize=(10, 8))
plt.pcolormesh(X, Y, velocity_magnitude.T, cmap='plasma')
plt.colorbar(label="Magnitude de la vitesse (m/s)")
plt.title("Champ de la magnitude de la vitesse")
plt.xlabel('Distance en m')
plt.ylabel('Distance en m')

# Afficher la direction de la vitesse avec des vecteurs
plt.quiver(X, Y, Zux.T, Zuy.T, color='white', scale=10, label="Direction de la vitesse")
plt.legend()
plt.show()

# Courbe de débit le long du conduit
def debit(Zux, Zuy, M):
    d = np.zeros(M)
    for i in range(M):
        for j in range(N):
            d[i] += np.sqrt(Zux[i, j] ** 2 + Zuy[i, j] ** 2) * D / (N - 1)
    return d


d = debit(Zux, Zuy, M)
plt.figure(figsize=(10, 6))
plt.plot(x, debit(Zux, Zuy, M), label='Debit', color='b')
plt.title('Distribution du debit ')
plt.xlabel('Longueur du Conduit (m)')
plt.ylabel('Debit (m³/s)')
plt.axhline(y=d[M - 1], color='r', linestyle='--', label='Pression à la Sortie (D2)')
plt.axhline(y=d[0], color='g', linestyle='--', label='Pression à l\'Entrée (D1)')
plt.legend()
plt.grid()
plt.show()

# Courbe de la résistance hydraulique le long du conduit





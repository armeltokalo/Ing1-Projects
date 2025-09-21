#!/usr/bin/env python
# coding: utf-8

# In[95]:


import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D



def matrice_A(M, N,dx,dy,n,h,li,lf):
    a=1/(dx*n)
    b=1/dx**2
    c=1/dy**2
    d=1/dx
    e=1/dy
    f=1/(dy*n)

    """
    Crée la matrice A d'ordre 3*M*N pour une discrétisation en 2D.

    Paramètres :
    M (int): Nombre de lignes de la grille.
    N (int): Nombre de colonnes de la grille.

    Retourne :
    np.ndarray: La matrice A d'ordre 3*M*N.
    """
    # Création de la matrice A de taille 3*M*N x 3*M*N initialisée à zéro
    A = np.zeros((3*M *N, 3*M*N))
    
    # Boucle pour remplir la matrice A
    for i in range(M):
        for j in range(N):
            # Calcul de l'indice linéaire correspondant à la position (i, j)
            idx = i * N + j
            # Conditions aux bords pour la discrétisation
           
            if j==0 :
                A[idx, idx ] = 1   
                A[idx+M*N, idx+M*N ] = 1 
                A[idx+2*M*N, idx+M*N ] = 1 
                A[idx+2*M*N, i*N+j+1+M*N ] = -1 
            if   j==N-1: 
                A[idx, idx ] = 1   
                A[idx+M*N, idx+M*N ] = 1 
                A[idx+2*M*N, idx+M*N ] = 1 
                A[idx+2*M*N, i*N+j-1+M*N ] = -1 
            
            if i ==0 or (j==0 and i==0) or (j==N-1 and i==0):
                #
                A[idx, idx ] = 1
                A[idx, (M-1)*N+j ] = -1
               
                A[idx+M*N, idx+M*N ] = 1
                A[idx+M*N, (M-1)*N+j+M*N ] = -1

                A[idx+2*M*N, idx+2*M*N ] = 1
            if i== M-1 or (j==0 and i==M-1) or (j==N-1 and i==M) :
                A[idx,idx] = 1
                A[idx, (i-1)*N+j ] = -1 
                A[idx, j ] = 1
                A[idx, N+j ] = -1
                
                A[idx+M*N, idx+M*N ] = 1
                A[idx+M*N, (i-1)*N+j+M*N ] = -1
                A[idx+M*N, j+M*N ] = 1
                A[idx+M*N, N+j+M*N ] = -1
                #A[idx, idx ] = 1
                #A[idx, j ] = -1
                A[idx+2*M*N, idx+2*M*N ] = 1
            if   j!=0 and j!=N-1 and i!=0 and i!=M-1: 
                if    i ==M-2  :
                    A[i*N+j,i*N+j]=-2*(b+c)
                    A[i*N+j,i*N+j+1]=c
                    A[i*N+j,i*N+j-1]=c
                    A[i*N+j,(i+1)*N+j]=b 
                    A[i*N+j,(i-1)*N+j]=b 
                    A[i*N+j,2*N*M+(i-1)*N+j]=a
                    A[i*N+j,2*N*M+(i)*N+j]=-a
    
                    A[M*N+i*N+j,M*N+i*N+j]=-2*(b+c)
                    A[M*N+i*N+j,M*N+i*N+j+1]=c
                    A[M*N+i*N+j,M*N+i*N+j-1]=c
                    A[M*N+i*N+j,M*N+(i+1)*N+j]=b 
                    A[M*N+i*N+j,M*N+(i-1)*N+j]=b 
                    A[M*N+i*N+j,2*N*M+i*N+j-1]=f/2
                    A[M*N+i*N+j,2*N*M+(i)*N+(j+1)]=-f/2
                    
                    
                    #periodicite de pression
                    A[2*M*N+i*N+j,2*M*N+(i)*N+j]=-1
                    A[2*M*N+i*N+j,2*M*N+(i+1)*N+j]=1
                    A[2*M*N+i*N+j,2*M*N+(0)*N+j]=1
                    A[2*M*N+i*N+j,2*M*N+(1)*N+j]=-1
                
    
                    A[2*M*N+i*N+j,(i-1)*N+j]=-d/2
                    A[2*M*N+i*N+j,(i+1)*N+j]=d/2
            
                    A[2*M*N+i*N+j,M*N+i*N+j+1]=e/2
                    A[2*M*N+i*N+j,M*N+i*N+j-1]=-e/2
                
                else:
                    A[i*N+j,i*N+j]=-2*(b+c)
                    A[i*N+j,i*N+j+1]=c
                    A[i*N+j,i*N+j-1]=c
                    A[i*N+j,(i+1)*N+j]=b 
                    A[i*N+j,(i-1)*N+j]=b 
                    A[i*N+j,2*N*M+(i-1)*N+j]=a/2
                    A[i*N+j,2*N*M+(i+1)*N+j]=-a/2
    
                    A[M*N+i*N+j,M*N+i*N+j]=-2*(b+c)
                    A[M*N+i*N+j,M*N+i*N+j+1]=c
                    A[M*N+i*N+j,M*N+i*N+j-1]=c
                    A[M*N+i*N+j,M*N+(i+1)*N+j]=b 
                    A[M*N+i*N+j,M*N+(i-1)*N+j]=b 
                    A[M*N+i*N+j,2*N*M+i*N+j-1]=f/2
                    A[M*N+i*N+j,2*N*M+(i)*N+(j+1)]=-f/2
    
    
                    A[2*M*N+i*N+j,(i-1)*N+j]=-d/2
                    A[2*M*N+i*N+j,(i+1)*N+j]=d/2
            
                    A[2*M*N+i*N+j,M*N+i*N+j+1]=e/2
                    A[2*M*N+i*N+j,M*N+i*N+j-1]=-e/2
                    
                    
             #deformation       
            if j==h and  li<i<lf :
                A[idx, idx ] = 1   
                
                A[idx+M*N, idx+M*N ] = 1 
                
                A[idx+2*M*N, idx+M*N ] = 1 
                A[idx+2*M*N, i*N+j+1+M*N ] = -1 
            if j==h and  (i==li or i==lf) :   
                 A[2*M*N+i*N+j,(i)*N+j]=-d
                 A[2*M*N+i*N+j,(i+1)*N+j]=d
            
                 A[2*M*N+i*N+j,M*N+i*N+j+1]=e
                 A[2*M*N+i*N+j,M*N+i*N+j]=-e
            if j==0 and   (i==lf) : 
                
                 A[idx+2*M*N, idx+2*M*N ] = 1  
                 A[idx+2*M*N, (i+1)*N+j+2*M*N ] = -1
            if j==0 and   (i==lf) : 
                
                 A[idx+2*M*N, idx+2*M*N ] = 1  
                 A[idx+2*M*N, (i-1)*N+j+2*M*N ] = -1    
            #if   j==0 and  li<i<lf:
                
                 #A[idx, idx ] = 1   
                 #A[idx+M*N, idx+M*N ] = 1 
                 #A[idx+2*M*N, idx+M*N ] = 1 
                # A[idx+2*M*N, i*N+j-1+M*N ] = -1 
                
            if i ==lf and j<=h :
                
                A[idx, idx ] = 1
                A[idx, (i+1)*N+j ] = -1
    
                A[idx+M*N, idx+M*N ] = 1
                A[idx+M*N, (i+1)*N+j+M*N ] = -1

                A[idx+2*M*N, idx+2*M*N ] = 1 
            
            if i== li and j<=h :
                
                A[idx,idx] = 1
                A[idx, (i-1)*N+j ] = -1
                
                #A[idx, j ] = 1
                #A[idx, N+j ] = -1
                
                A[idx+M*N, idx+M*N ] = 1
                A[idx+M*N, (i-1)*N+j+M*N ] = -1
                #A[idx+M*N, j+M*N ] = 1
                #A[idx+M*N, N+j+M*N ] = -1
                
                #A[idx, idx ] = 1
                #A[idx, j ] = -1
                A[idx+2*M*N, idx+2*M*N ] = 1  
                  
            if  li<=i<=lf and j<h:
                
                A[idx,idx] = 1
                A[idx+2*M*N,idx+2*M*N] = 1
                A[idx+M*N,idx+M*N] = 1
                
    return A
def create (M,N,P1,P2):
    B = np.zeros(3*M*N)

    for i in range(0, M):
        for j in range(0, N):
            idx = i*N +j
           
            if i== 0  :
                 B[idx+2*M*N]=P1
                 
            elif i==M-1: 
                 B[idx+2*M*N]=P2
               

    return B

L=5.32*1e-2
u=1
D=7.54*1e-3
M=20
N=15
h=2#paire
li=10
lf=12
P1=10*1e-2
P2=1*1e-2
n=1.81*1e-5
dx=L/(M-1)
dy=D/(N-1)
R=matrice_A(M, N,dx,dy,n,h,li,lf)
B=create(M,N,P1,P2)

#F= np.linalg.pinv(R).dot(B)  
F=np.linalg.solve(R,B)
x = np.linspace(0,L , M)  # Plage de valeurs pour x
y = np.linspace(0, D, N)  # Plage de valeurs pour y
X, Y = np.meshgrid(x, y)     # Crée une grille 2D à partir de x et y
    
Zux = np.zeros((M, N))
Zuy = np.zeros((M, N))
Zp = np.zeros((M, N))


for i in range(0, M):
        for j in range(0, N):
            Zux[i,j]=F[i*N+j]
            
for i in range(0, M):
        for j in range(0, N):
            Zuy[i,j]=F[N*M+i*N+j]

for i in range(0, M):
        for j in range(0, N):
            Zp[i,j]=F[2*N*M+i*N+j]
            
# Créer une figure 3D
fig = plt.figure(figsize=(12, 20))
ax = fig.add_subplot(111, projection='3d')

# Tracer la surface
ax.plot_surface(X, Y, Zp.T, cmap='viridis')

# Ajouter des étiquettes
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('f(X, Y)')
ax.set_title('pression')

# Afficher le graphique
plt.show()
plt.pcolormesh(X, Y, Zp.T*1e2)

plt.colorbar(label="Pression en 10**(2) Pa")
plt.quiver(X,Y,Zux.T,Zuy.T)

plt.title("Allure de solution de l'équation STOKES avec déformation: ")
plt.xlabel('Distance en m')
plt.ylabel('Distance en m')
plt.show()


# In[80]:


print( Zux[7,1], Zuy[7,1])


# In[81]:


print( Zux[7,2], Zuy[7,2])


# In[82]:


print( Zux[6,2], Zuy[6,2])


# In[83]:


print( Zux[0,0], Zuy[0,0])


# In[ ]:





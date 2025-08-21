# pip install pulp

import pulp

# 1. Paramètres
products = ['A', 'B', 'C']
months   = list(range(1, 7))
D = {
    'A': {1:100, 2:120, 3:130, 4:110, 5:115, 6:105},
    'B': {1: 80, 2: 90, 3: 85, 4: 95, 5:100, 6: 90},
    'C': {1: 60, 2: 70, 3: 65, 4: 75, 5: 80, 6: 70},
}
c_prod  = {'A':10, 'B':12, 'C':9}
c_stock = {'A':2,  'B':1.5, 'C':1}
c_delay = {'A':5,  'B':4,   'C':3}
cap_labor    = 1000
cap_material =  500
cap_machine  =  600
coef_labor    = {'A':2,   'B':1.5, 'C':1}
coef_material = {'A':1,   'B':0.8, 'C':0.5}
coef_machine  = {'A':1.5, 'B':1,   'C':0.8}

# 2. Modèle (minimisation)
model = pulp.LpProblem("Projet1", pulp.LpMinimize)

# 3. Variables
x = pulp.LpVariable.dicts("prod",   (products, months), lowBound=0)
S = pulp.LpVariable.dicts("stock",  (products, months), lowBound=0)
P = pulp.LpVariable.dicts("delay",  (products, months), lowBound=0)
k = pulp.LpVariable.dicts("is_pos", (products, months), cat='Binary')

# 5. Fonction objectif (coûts totaux)
model += (
    pulp.lpSum(c_prod[i]  * x[i][j] for i in products for j in months)
  + pulp.lpSum(c_stock[i] * S[i][j] for i in products for j in months)
  + pulp.lpSum(c_delay[i] * P[i][j] for i in products for j in months)
), "Cout_total"

# 6. Contraintes capacitaires (sans virgules !)
for j in months:
    model += pulp.lpSum(coef_labor   [i] * x[i][j] for i in products) <= cap_labor
    model += pulp.lpSum(coef_material[i] * x[i][j] for i in products) <= cap_material
    model += pulp.lpSum(coef_machine [i] * x[i][j] for i in products) <= cap_machine

# 7. Stockage & pénalités — j ∈ IN5 = {1,…,5}
for i in products:
    for j in range(1, 6):
        # conservation cumulative
        model += (
            pulp.lpSum(x[i][k] for k in range(1, j+1))
          - pulp.lpSum(D[i][k] for k in range(1, j+1))
          == S[i][j] - P[i][j]
        ), f"cum_flux_{i}_{j}"
        # exclusivité stock/retard
        model += S[i][j] <= 1000 * k[i][j]
        model += P[i][j] <= D[i][j] * (1 - k[i][j])

    # aucun retard pour A
    for j in range(1, 6):
        model += P['A'][j] == 0

# 8. Satisfaction globale (tous mois)
for i in products:
    model += pulp.lpSum(x[i][j] for j in months) >= pulp.lpSum(D[i][j] for j in months)

# 9. Résolution
model.solve(pulp.PULP_CBC_CMD(msg=0))

# 10. Affichage simplifié
print("Statut :", pulp.LpStatus[model.status])
print("Coût total optimal =", pulp.value(model.objective))
for i in products:
    print(f"Produit {i} :", [x[i][j].varValue for j in months])
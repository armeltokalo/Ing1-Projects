# Projet d’Optimisation

Ce dépôt contient deux projets d’optimisation, portant respectivement sur la planification de la production multi-produits et sur la planification des médecins dans un service pédiatrique hospitalier.  

---

## Projet 1 : Planification de la Production Multi-Produits sur Plusieurs Périodes

### Objectif
Déterminer le **plan de production optimal** pour plusieurs produits sur un horizon de 6 mois, en minimisant les coûts totaux (production, stockage, pénalités de retard), tout en respectant les contraintes de capacité, de ressources, de stockage et de priorités clients.

### Description du problème
Une entreprise fabrique trois produits : **A, B et C**. La demande mensuelle pour chaque produit est connue pour les 6 prochains mois. Chaque produit consomme différentes ressources (main-d'œuvre, matières premières, machines), avec des capacités limitées.  

L’entreprise souhaite :  
- Satisfaire la demande mensuelle de chaque produit.  
- Minimiser les coûts totaux : production, stockage et pénalités pour retards.  
- Respecter les contraintes de capacité de production et les priorités clients.  

### Données fournies

- **Produits** : A, B, C  
- **Périodes** : Mois 1 à 6  
- **Demandes mensuelles** :  
  - Produit A : [100, 120, 130, 110, 115, 105]  
  - Produit B : [80, 90, 85, 95, 100, 90]  
  - Produit C : [60, 70, 65, 75, 80, 70]  
- **Coûts de production par unité** : A = 10€, B = 12€, C = 9€  
- **Coûts de stockage par unité et par mois** : A = 2€, B = 1.5€, C = 1€  
- **Pénalités de retard par unité** : A = 5€, B = 4€, C = 3€  

- **Capacités mensuelles des ressources** :  
  - Main-d'œuvre : 1000 heures  
  - Matières premières : 500 kg  
  - Machines : 600 heures  

- **Consommation des ressources par unité produite** :  
  - Produit A : Main-d'œuvre 2h, Matières premières 1kg, Machines 1.5h  
  - Produit B : Main-d'œuvre 1.5h, Matières premières 0.8kg, Machines 1h  
  - Produit C : Main-d'œuvre 1h, Matières premières 0.5kg, Machines 0.8h  

- **Priorités clients** :  
  - Produit A : livraison sans retard autorisé (contrainte stricte)  
  - Produits B et C : retards autorisés avec pénalités  

---

## Projet 2 : Planification Optimale des Médecins d’un Service Pédiatrique Hospitalier

### Objectif
Planifier les affectations des médecins sur une semaine, un mois et un trimestre, en assurant la couverture de tous les créneaux nécessaires pour les activités médicales (consultation, astreinte, etc.), tout en respectant disponibilités, spécialisations et contraintes de repos.  

L’objectif est de minimiser le recours aux remplaçants et de maximiser l’équilibre de charge entre médecins, tout en maintenant une flexibilité pour planifier les vacances et jours de RTT.

### Description du problème
L’hôpital doit couvrir chaque créneau horaire par spécialité (matin, après-midi, garde), en tenant compte des médecins disponibles et de leurs compétences, tout en respectant les contraintes de repos et les priorités pour certains postes critiques.  

### Données disponibles
1. Besoins par spécialité et créneau horaire (feuille 1 : Besoins)  
2. Effectif disponible avec spécialité, nom et compétences (feuille 2 : Effectifs)  
3. Vacances ou absences planifiées par médecin (feuille 3 : Contraintes)  
4. Activités à couvrir et types d’affectation médicale (feuille 0 : Inputs)  

### Contraintes à respecter
- Chaque créneau doit être couvert par le nombre exact de médecins requis pour chaque activité.  
- Les médecins ne peuvent travailler que dans les créneaux pour lesquels ils sont disponibles.  
- Chaque médecin ne peut travailler qu’un seul créneau par jour.  
- Limitation du nombre de créneaux par semaine/mois.  
- Les médecins en vacances ou absences ne peuvent être affectés.  
- Priorisation pour certains postes : urgences, néonat, salle, astreinte, maternité.  
- Minimiser l’utilisation de remplaçants, surtout en cas de changements imprévus.  

---

## Instructions d’utilisation

1. **Installation** :  
   - Cloner le dépôt :  
     ```bash
     git clone <URL_DU_DEPOT>
     ```  
   - Installer les dépendances (si nécessaire pour les scripts d’optimisation) :  
     ```bash
     pip install -r requirements.txt
     ```

2. **Exécution** :  
   - Projet 1 :  
     ```bash
     python projet1.py
     ```  
   - Projet 2 :  
     ```bash
     python projet2.py
     ```

3. **Résultats** :  
   - Les fichiers de sortie contiennent les plans optimaux de production et les plannings de médecins, au format CSV ou Excel, selon les scripts.

---

## Structure du dépôt

```
/Optimization
│
├─ data/                      # Fichiers de données (demandes, coûts, ressources)
├─ Projet1_Production
├─ scripts/           # Scripts Python pour l’optimisation
├─  results/        # Résultats générés
│
├─ Projet2_Medecins
├─ scripts/        # Scripts Python pour la planification
├─ results/        # Plannings générés
│
└─ README.md
```


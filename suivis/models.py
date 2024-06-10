from django.db import models
from django.urls import reverse
from django.utils import timezone
from datetime import datetime

from plateforme.settings import AUTH_USER_MODEL

# Create your models here.
class Langue(models.Model):
    id_langue = models.AutoField(primary_key=True)
    langage = models.CharField(max_length=50) 
    
class Formation(models.Model):
    id_formation = models.AutoField(primary_key=True)
    ecole = models.CharField(max_length=150)
    date_debut_for = models.DateField()
    date_fin_for = models.DateField()
    resultat_obtenu = models.CharField(max_length=50)
    activite_association = models.CharField(max_length=150)
    domaine_d_etude = models.CharField(max_length=50)
    diplome = models.CharField(max_length=150) 
    
class Experience(models.Model):
    id_exp = models.AutoField(primary_key=True)
    intituler_d_poste = models.CharField(max_length=150)
    type_d_emploi = models.CharField(max_length=50)
    nom_entreprise = models.CharField(max_length=150)
    lieu = models.CharField(max_length=150)
    date_debut_exp = models.DateField()
    date_fin_exp = models.DateField()
    titre = models.CharField(max_length=50)
    
class Competence(models.Model):
    id_competence = models.AutoField(primary_key=True)
    competence = models.CharField(max_length=50) 
    
class Offre(models.Model):
    id_offre = models.AutoField(primary_key=True)
    nom_poste = models.CharField(max_length=100)
    genre = models.CharField(max_length=50)
    date_limite = models.DateField()
    reference_poste = models.CharField(max_length=50, unique=True)
    heure_de_travail = models.CharField(max_length=50)
    mission = models.TextField()
    profil_requis = models.TextField()
    nombre_poste = models.CharField(max_length=50)
    id = models.ForeignKey('comptes.Utilisateurs', on_delete=models.PROTECT)
    id_projet = models.ForeignKey('Projet', on_delete=models.PROTECT)   
    
class Postulant(models.Model):
    id_postulant = models.CharField(max_length=10, primary_key=True)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=150)
    date_de_naissance = models.DateField()
    adresse = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    code_postal = models.CharField(max_length=50)
    telephone = models.CharField(max_length=50)
    copie_diplome = models.FileField(upload_to="copie_diplome", max_length=150, null=True, blank=True)
    date_d_postule = models.DateField(auto_now_add=True)
    CV = models.FileField(upload_to="cv", max_length=150, null=True, blank=True)
    LM = models.FileField(upload_to="lm", max_length=150, null=True, blank=True)
    is_collaborateur = models.BooleanField(default=False)
    id_offre = models.ForeignKey('Offre', on_delete=models.PROTECT)
    langues = models.ManyToManyField(Langue, related_name='postulants')
    formations = models.ManyToManyField(Formation, related_name='postulants')
    experiences = models.ManyToManyField(Experience, related_name='postulants')
    competences = models.ManyToManyField(Competence, related_name='postulants')
    
    def save(self, *args, **kwargs):
        if not self.id_postulant:
            # Si aucun ID n'est défini, en créer un nouveau
            last_id = Postulant.objects.order_by('id_postulant').last()
            if last_id:
                last_id_number = int(last_id.id_postulant.split('-')[1])
            else:
                last_id_number = 0
            new_id_number = last_id_number + 1
            new_id = 'P-%04d' % new_id_number
            self.id_postulant = new_id
        
        super(Postulant, self).save(*args, **kwargs)

class Collaborateur(models.Model):
    # Champs communs avec les postulants
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=150)
    date_de_naissance = models.DateField()
    adresse = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    code_postal = models.CharField(max_length=50)
    telephone = models.CharField(max_length=50)
    copie_diplome = models.FileField(upload_to="copie_diplome", max_length=150, null=True, blank=True)
    date_d_postule = models.DateField(auto_now_add=True)
    CV = models.FileField(upload_to="cv", max_length=150, null=True, blank=True)
    LM = models.FileField(upload_to="lm", max_length=150, null=True, blank=True)
    
    # Champs spécifiques aux collaborateurs
    id_offre = models.ForeignKey('Offre', on_delete=models.PROTECT)
    langues = models.ManyToManyField(Langue, related_name='collaborateurs')
    formations = models.ManyToManyField(Formation, related_name='collaborateurs')
    experiences = models.ManyToManyField(Experience, related_name='collaborateurs')
    competences = models.ManyToManyField(Competence, related_name='collaborateurs')

    # Champ pour indiquer si c'est un postulant ou un collaborateur
    est_postulant = models.BooleanField(default=True)

        
class Projet(models.Model):
    STATUT_ATTENTE = 'en_attente'
    STATUT_EN_COURS = 'en_cours'
    STATUT_TERMINE = 'termine'
    
    CHOIX_STATUTS = [
            (STATUT_ATTENTE, 'En attente'),
            (STATUT_EN_COURS, 'En cours'),
            (STATUT_TERMINE, 'Terminé')
        ]
    
    id_projet = models.AutoField(primary_key=True)
    intituler = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    cible = models.CharField(max_length=100)
    objectif = models.CharField(max_length=100)
    duree_reelle = models.CharField(max_length=100)
    date_debut_p = models.DateField()
    date_fin_p = models.DateField()
    date_debut_r = models.DateField()
    date_fin_r = models.DateField()
    observation = models.TextField()
    statuts = models.CharField(max_length=25, choices=CHOIX_STATUTS)
    id = models.ForeignKey('comptes.Utilisateurs', on_delete=models.PROTECT)

class Evaluer(models.Model):
    id_evaluation = models.AutoField(primary_key=True)
    id_projet = models.ForeignKey('Projet', on_delete=models.PROTECT)
    id = models.ForeignKey('comptes.Utilisateurs', on_delete=models.PROTECT)
    id_postulant = models.ForeignKey('Postulant', on_delete=models.PROTECT)
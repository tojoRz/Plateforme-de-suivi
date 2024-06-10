# pylint: disable=E1101

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models.signals import post_save
from django.dispatch import receiver
from suivis.models import Projet, Offre, Formation, Postulant, Experience, Competence, Langue, Collaborateur
from comptes.models import Utilisateurs
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timezone
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import Group
from django.db.models import Count
from django.db.models.functions import ExtractMonth
from .decorators import user_in_group_required
from django.urls import reverse


from .forms import ProjetForm

from datetime import datetime, date


import pytz
import sys
import schedule
import time
import json
import re


n=10000
sys.setrecursionlimit(n)


now = datetime.now(pytz.utc)

# Create your views here.

@login_required
def dashboard(request):
    
    p_projet = 1000
    p_projets_termines = 1000
    p_postulant = 1000
    p_offre = 100000
    
    user_belongs_to_admin_group = request.user.groups.filter(name='Administrateur').exists()
    count = Utilisateurs.objects.filter(is_active=False).count()
    group_count = Group.objects.count()
    projet_count = Projet.objects.count()
    offre_count = Offre.objects.count()
    utilisateur_count = Utilisateurs.objects.count()
    postulant_count = Postulant.objects.count()
    projets_termines_count = Projet.objects.filter(statuts=Projet.STATUT_TERMINE).count()
    
    pourcentage_projet = round((projet_count/p_projet)*100, 2)
    pourcentage_postulant = round((postulant_count/p_postulant)*100, 2)
    pourcentage_offre = round((offre_count/p_offre)*100, 2)
    pourcentage_projets_termines = round((projets_termines_count/p_projets_termines)*100, 2)
    
    
    # Query pour compter le nombre de postulants par mois
    donnees = Postulant.objects.annotate(mois=ExtractMonth('date_d_postule')).values('mois').annotate(nombre=Count('id_postulant'))
    
    # Créer une liste pour stocker le nombre de postulants par mois
    nombres_par_mois = [0] * 12

    # Remplir la liste avec les données de la base de données
    for entree in donnees:
        mois_index = entree['mois'] - 1
        nombres_par_mois[mois_index] = entree['nombre']

    # Convertir la liste en une chaîne JSON
    nombres_par_mois_json = json.dumps(nombres_par_mois)
    
    context = {
        'count': count,
        'user_belongs_to_admin_group': user_belongs_to_admin_group,
        'group_count': group_count,
        'projet_count': projet_count,
        'offre_count': offre_count,
        'utilisateur_count': utilisateur_count,
        'pourcentage_projet': pourcentage_projet,
        'postulant_count': postulant_count,
        'pourcentage_postulant': pourcentage_postulant,   
        'pourcentage_offre': pourcentage_offre,    
        'projets_termines_count': projets_termines_count,
        'pourcentage_projets_termines': pourcentage_projets_termines,
        'nombres_par_mois_json': nombres_par_mois_json,
        
        }
    
    return render(request, 'suivis/dashboard.html',context)


def projects_data(request):
    # Récupérer les données des projets depuis la base de données
    projects = Projet.objects.all()

    # Préparer les listes pour les labels et les données des projets
    labels = ["Jan", "Feb", "Mar","Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    data_en_cours = [0] * len(labels)
    data_en_attente = [0] * len(labels)
    data_termine = [0] * len(labels)

    # Compter les projets par mois et par statut
    for project in projects:
        mois_index = project.date_debut_p.month - 1  # Pour correspondre à l'index dans les labels
        if project.statuts == Projet.STATUT_EN_COURS:
            data_en_cours[mois_index] += 1
        elif project.statuts == Projet.STATUT_ATTENTE:
            data_en_attente[mois_index] += 1
        elif project.statuts == Projet.STATUT_TERMINE:
            data_termine[mois_index] += 1

    # Créer un dictionnaire contenant les données des projets
    projects_data = {
        'labels': labels,
        'en_cours': data_en_cours,
        'en_attente': data_en_attente,
        'termine': data_termine,
    }

    return JsonResponse(projects_data)


@login_required
def projet_list(request):
    user_belongs_to_admin_group = request.user.groups.filter(name='Administrateur').exists()
    count = Utilisateurs.objects.filter(is_active=False).count()
    projets = Projet.objects.all().order_by('id_projet')
    statuts = request.GET.get('statuts')
    if statuts:
        projets = projets.filter(statuts=statuts)
    
    paginator = Paginator(projets, 4)
    numero_page = request.GET.get('page')
    projets = paginator.get_page(numero_page)
    
    return render(request, 'suivis/projet_list.html', {'projets': projets,'count':count, 'user_belongs_to_admin_group': user_belongs_to_admin_group})

@login_required
@user_in_group_required('Responsable Terrain')
def add_projet(request):
    user_belongs_to_admin_group = request.user.groups.filter(name='Administrateur').exists()
    count = Utilisateurs.objects.filter(is_active=False).count()
    if request.method == 'POST':
        # traiter le formulaire
        intituler = request.POST.get("sai_intituler_projet")
        type = request.POST.get("sai_type_projet")
        cible = request.POST.get("sai_cible_projet")
        objectif = request.POST.get("sai_objectif_projet")
        duree_reelle = request.POST.get("sai_duree_reelle")
        date_debut_p = request.POST.get("sai_date_debut_p")
        date_fin_p = request.POST.get("sai_date_fin_p")
        date_debut_r = request.POST.get("sai_date_debut_r")
        date_fin_r = request.POST.get("sai_date_fin_r")
        observation = request.POST.get("sai_obs")
        
        STATUT_ATTENTE = 'en_attente'
        STATUT_EN_COURS = 'en_cours'
        STATUT_TERMINE = 'termine'
        CHOIX_STATUTS = [
            (STATUT_ATTENTE, 'En attente'),
            (STATUT_EN_COURS, 'En cours'),
            (STATUT_TERMINE, 'Terminé')
        ]
     
        now = datetime.now(pytz.UTC)
        date_debut_r_obj = pytz.utc.localize(datetime.strptime(date_debut_r, '%Y-%m-%d'))
        date_fin_r_obj = pytz.utc.localize(datetime.strptime(date_fin_r, '%Y-%m-%d'))

        
        if date_debut_r_obj > now:
            statuts = STATUT_ATTENTE
        elif date_debut_r_obj <= now and date_fin_r_obj >= now:
            statuts = STATUT_EN_COURS
        elif date_fin_r_obj < now:
            statuts = STATUT_TERMINE

        # Obtenir l'ID de l'utilisateur actuel
        id_utilisateur = request.user.id
        
        projet = Projet.objects.create(
            intituler=intituler,
            type=type,
            cible=cible,
            objectif=objectif,
            duree_reelle=duree_reelle,
            date_debut_p=date_debut_p,
            date_fin_p=date_fin_p,
            date_debut_r=date_debut_r,
            date_fin_r=date_fin_r,
            observation=observation,
            statuts=statuts,
            id_id=id_utilisateur,
        )
        messages.success(request, "Le projet a été ajouté avec succès !")
        return redirect('projet')
    
    else:
        return render(request, 'suivis/add_projet.html', {'count':count, 'user_belongs_to_admin_group': user_belongs_to_admin_group})


@login_required
@user_in_group_required('Responsable Terrain')
def update_projet_view(request, id):
    projet = get_object_or_404(Projet, id_projet=id)
    user_belongs_to_admin_group = request.user.groups.filter(name='Administrateur').exists()
    count = Utilisateurs.objects.filter(is_active=False).count()

    date_debut_r = None
    
    if request.method == 'POST':
        # Traiter le formulaire
        intituler = request.POST.get("sai_intituler_projet")
        type = request.POST.get("sai_type_projet")
        cible = request.POST.get("sai_cible_projet")
        objectif = request.POST.get("sai_objectif_projet")
        duree_reelle_str = request.POST.get("sai_duree_reelle")
        date_debut_p = request.POST.get("sai_date_debut_p")
        date_fin_p = request.POST.get("sai_date_fin_p")
        date_debut_r_str = request.POST.get("sai_date_debut_r")
        date_fin_r_str = request.POST.get("sai_date_fin_r")
        observation = request.POST.get("sai_obs")
        
        STATUT_ATTENTE = 'en_attente'
        STATUT_EN_COURS = 'en_cours'
        STATUT_TERMINE = 'termine'
        CHOIX_STATUTS = [
            (STATUT_ATTENTE, 'En attente'),
            (STATUT_EN_COURS, 'En cours'),
            (STATUT_TERMINE, 'Terminé')
        ]
     
        now = datetime.now(pytz.UTC)
        if date_debut_r_str and date_fin_r_str:
            # Convertir les dates en objets datetime
            date_debut_r_obj = pytz.utc.localize(datetime.strptime(date_debut_r_str, '%Y-%m-%d'))
            date_fin_r_obj = pytz.utc.localize(datetime.strptime(date_fin_r_str, '%Y-%m-%d'))


        if date_debut_r_obj > now:
            statuts = STATUT_ATTENTE
        elif date_debut_r_obj <= now and date_fin_r_obj >= now:
            statuts = STATUT_EN_COURS
        else:
            statuts = STATUT_TERMINE

        # Obtenir l'ID de l'utilisateur actuel
        id_utilisateur = request.user.id
        
        # Initialiser date_debut_r
        date_debut_r = date_debut_r_str

        # Mettre à jour le projet
        projet.intituler = intituler
        projet.type = type
        projet.cible = cible
        projet.objectif = objectif

        try:
            duree_reelle = int(duree_reelle_str)
            projet.duree_reelle = duree_reelle
        except ValueError:
            # Gérez le cas où la valeur n'est pas un nombre valide
            projet.duree_reelle = 0  # Affectez une valeur par défaut ou gérez l'erreur autrement

        projet.date_debut_p = date_debut_p
        projet.date_fin_p = date_fin_p
        projet.date_debut_r = date_debut_r_str
        projet.date_fin_r = date_fin_r_str
        projet.observation = observation
        projet.statuts = statuts
        projet.id_id = id_utilisateur

        projet.save()  # Sauvegardez l'objet Projet après les modifications

        messages.success(request, "Le projet a été mis à jour avec succès !")
        return redirect('projet')

    else:
        return render(request, 'suivis/update_projet.html', {'projet': projet, 'count': count, 'user_belongs_to_admin_group': user_belongs_to_admin_group})


@login_required
def voir_projet(request, id):
    # Récupération de la projet correspondant à l'ID fourni
    projet = Projet.objects.get(id=id)
    data = {
            'id': projet.id_projet,
            'intituler': projet.intituler,
            'type': projet.type,
            'cible': projet.cible,
            'objectif': projet.objectif,
            'duree_reelle': projet.duree_reelle,
            'date_debut_p': projet.date_debut_p,
            'date_fin_p': projet.date_fin_r,
            'date_debut_r': projet.date_debut_r,
            'date_fin_r': projet.date_fin_r,
            'observation': projet.observation,
            'statuts': projet.statuts,
        }
    return JsonResponse({'projet': data})


@login_required
def delete_projet(request, id):
    # Récupère l'utilisateur par ID
    projet = Projet.objects.get(pk=id)

    # Supprime l'utilisateur
    projet.delete()

    # Redirige vers la page d'accueil ou toute autre page souhaitée
    return redirect('projet')


@login_required
def run_update_proj_statuts(request):
    now = datetime.now(pytz.UTC)
    date_debut_r = Projet.objects.first().date_debut_r
    date_fin_r = Projet.objects.first().date_fin_r
    
    date_debut_r_obj = pytz.utc.localize(datetime.strptime(str(date_debut_r), '%Y-%m-%d'))
    date_fin_r_obj = pytz.utc.localize(datetime.strptime(str(date_fin_r), '%Y-%m-%d'))
    
    STATUT_ATTENTE = 'en_attente'
    STATUT_EN_COURS = 'en_cours'
    STATUT_TERMINE = 'termine'

    if date_debut_r_obj > now:
        statuts = STATUT_ATTENTE
    elif date_debut_r_obj <= now and date_fin_r_obj >= now:
        statuts = STATUT_EN_COURS
    elif date_fin_r_obj < now:
        statuts = STATUT_TERMINE

    Projet.objects.update(statuts=statuts)
    
    return redirect('projet')


def update_proj_statuts():
    run_update_proj_statuts()

schedule.every(60).seconds.do(update_proj_statuts)

# while True:
#     schedule.run_pending()
#     time.sleep(1)


#############################################################
@login_required
def voir_offre(request, id):
    # Récupération de l'offre correspondant à l'ID fourni
    offre = Offre.objects.get(id=id)
    data = {
            'id_offre': offre.id_offre,
            'date_limite': offre.date_limite,
            'reference_poste': offre.reference_poste,
            'heure_de_travail': offre.heure_de_travail,
            'mission': offre.mission,
            'profil_requis': offre.profil_requis,
            'id_projet_id': offre.id_projet_id,
            'genre': offre.genre,
            'nom_poste': offre.nom_poste,
            'nombre_poste': offre.nombre_poste,
        }
    return JsonResponse({'offre': data})

@login_required
def offres_views(request):
    user_belongs_to_admin_group = request.user.groups.filter(name='Administrateur').exists()
    countOffre = Offre.objects.all().count()

    # Toutes les offres triées par id_offre croissant
    offres = Offre.objects.all().order_by('id_offre')

    paginator = Paginator(offres, 10)
    numero_page = request.GET.get('page')
    offres = paginator.get_page(numero_page)

    # Rendu du template 'suivis/offres_list.html' avec les données passées en contexte
    return render(request, 'suivis/list_offres.html', {
        'offres': offres,
        'countOffre': countOffre,
        'user_belongs_to_admin_group': user_belongs_to_admin_group,
    })
    
  
def offres_list(request):
    user_belongs_to_admin_group = request.user.groups.filter(name='Administrateur').exists()
    countOffre = Offre.objects.all().count()

    # Toutes les offres triées par id_offre croissant
    offres = Offre.objects.all().order_by('id_offre')

    paginator = Paginator(offres, 2)
    numero_page = request.GET.get('page')
    offres = paginator.get_page(numero_page)


    # Rendu du template 'suivis/offres_list.html' avec les données passées en contexte
    return render(request, 'suivis/offres_list.html', {
        'offres': offres,
        'countOffre': countOffre,
        'user_belongs_to_admin_group': user_belongs_to_admin_group,
    })

@login_required
@user_in_group_required('Recruteur Formateur')
def add_offre(request):
    user_belongs_to_admin_group = request.user.groups.filter(name='Administrateur').exists()
    count = Utilisateurs.objects.filter(is_active=False).count()
    projets_sans_offre = Projet.objects.exclude(offre__isnull=False)

    if request.method == 'POST':
        # traiter le formulaire
        nom_poste = request.POST.get("sai_nom_poste")
        genre = request.POST.get("sai_genre")
        nombre_poste = request.POST.get("sai_nombre_poste")
        date_limite = request.POST.get("sai_date_limite")
        reference_poste = request.POST.get("sai_reference_poste")
        heure_de_travail = request.POST.get("sai_heure_de_travail")
        missions = request.POST.get("sai_missions")
        profil_requis = request.POST.get("sai_profil_requis")

        # Récupérer l'ID du projet sélectionné
        id_projet = request.POST.get("sai_projet")

        # Obtenir l'ID de l'utilisateur actuel
        id_utilisateur = request.user.id

        offre = Offre.objects.create(
            nom_poste=nom_poste,
            genre=genre,
            nombre_poste=nombre_poste,
            date_limite=date_limite,
            reference_poste=reference_poste,
            heure_de_travail=heure_de_travail,
            mission=missions,
            profil_requis=profil_requis,
            id_id=id_utilisateur,
            id_projet_id=id_projet
        )

        messages.success(request,"L'offre a été ajoutée avec succès !")
        return redirect('offres_list')

    else:
        return render(request, 'suivis/offres_add.html', {'count': count, 'projets_sans_offre': projets_sans_offre, 'user_belongs_to_admin_group': user_belongs_to_admin_group})
    
@login_required
@user_in_group_required('Recruteur Formateur')
def update_offre_view(request, id):
    offre = get_object_or_404(Offre, id_offre=id)
    user_belongs_to_admin_group = request.user.groups.filter(name='Administrateur').exists()
    count = Utilisateurs.objects.filter(is_active=False).count()
    projets_sans_offre = Projet.objects.exclude(offre__isnull=False)

    if request.method == "POST":
        # Traiter le formulaire
        nom_poste = request.POST.get("sai_nom_poste")
        genre = request.POST.get("sai_genre")
        nombre_poste = request.POST.get("sai_nombre_poste")
        date_limite = request.POST.get("sai_date_limite")
        reference_poste = request.POST.get("sai_reference_poste")
        heure_de_travail = request.POST.get("sai_heure_de_travail")
        missions = request.POST.get("sai_missions")
        profil_requis = request.POST.get("sai_profil_requis")

        # Récupérer l'ID du projet sélectionné
        id_projet = request.POST.get("sai_projet")

        # Mettre à jour l'offre
        offre.nom_poste = nom_poste
        offre.genre = genre
        offre.nombre_poste = nombre_poste
        offre.date_limite = date_limite
        offre.reference_poste = reference_poste
        offre.heure_de_travail = heure_de_travail
        offre.mission = missions
        offre.profil_requis = profil_requis
        offre.id_id = request.user.id  # Utilisez le bon nom de champ
        offre.id_projet_id = id_projet

        offre.save()  # Sauvegardez l'objet Offre après les modifications

        messages.success(request, "L'offre a été mise à jour avec succès !")
        return redirect('offres_list')

    else:
        return render(request, 'suivis/update_offre.html', {'offre': offre, 'count': count, 'projets_sans_offre': projets_sans_offre, 'user_belongs_to_admin_group': user_belongs_to_admin_group})

  
def offres_detail(request, offre_id):
    # Récupération de l'offre correspondant à l'ID fourni
    offre = get_object_or_404(Offre, id_offre=offre_id)
    
    # sauvegarder l'ID de l'offre en cours dans la session
    request.session['offre_en_cours'] = offre.id_offre
        
    context = {'offre': offre}
    return render(request, 'suivis/offres_detail.html', context)

@login_required
@user_in_group_required('Recruteur Formateur')
def delete_offre(request, id):
    # Récupère l'utilisateur par ID
    offre = Offre.objects.get(pk=id)

    # Supprime l'utilisateur
    offre.delete()

    # Redirige vers la page d'accueil ou toute autre page souhaitée
    return redirect('offres_list')

def search_offre_view(request):
    count = Utilisateurs.objects.filter(is_active=False).count()
    user_belongs_to_admin_group = request.user.groups.filter(name='Administrateur').exists()
    
    if request.method == 'POST':
        query = request.POST.get("sai_search")
        if query:
            results = Offre.objects.filter(nom_poste__contains=query)
            return render(request, 'suivis/search.html', {'results': results,'count':count, 'user_belongs_to_admin_group': user_belongs_to_admin_group})
    return render(request, 'suivis/search.html',{'count':count, 'user_belongs_to_admin_group': user_belongs_to_admin_group})

def create_langue(langage):
    if langage:
        langue, created = Langue.objects.get_or_create(langage=langage)
        print(f"Champ 'sai_langage': {langage}")
        return langue
    else:
        print("Le champ 'sai_langage' est vide ou n'existe pas dans la requête POST.")
        return None

def create_formation(data):
    if data['ecole']:
        formation, created = Formation.objects.get_or_create(**data)
        return formation
    return None

def create_experience(data):
    if data['intituler_d_poste']:
        experience, created = Experience.objects.get_or_create(**data)
        return experience
    return None

def create_competence(competence_p):
    if competence_p:
        competence, created = Competence.objects.get_or_create(competence=competence_p)
        return competence
    return None
  
def add_postulant(request, offre_id):
    if request.method == 'POST':
        existe_deja = Postulant.objects.filter(email=request.POST.get("sai_email"), id_offre=offre_id).exists()
        if existe_deja:
            messages.error(request, 'Vous avez déjà postulé à cette offre.')
            return redirect('offre')
        else:
            # Récupération des données personnelles du postulant
            nom = request.POST.get("sai_nom")
            prenom = request.POST.get("sai_prenom")
            date_de_naissance = request.POST.get("sai_date_de_naissance")
            adresse = request.POST.get("sai_adresse")
            email = request.POST.get("sai_email")
            code_postal = request.POST.get("sai_code_postal")
            telephone = request.POST.get("sai_telephone")
            copie_diplome = request.FILES.get("sai_copie_diplome")
            CV = request.FILES.get("sai_CV")
            LM = request.FILES.get("sai_LM")

            offre_id = request.session.get('offre_en_cours')

            # Créez les listes en dehors des boucles
            langages = []
            formations = []
            experiences = []
            competences = []

            # Récupération des langages
            for countL in range(1, 5):
                langage = request.POST.get(f'sai_langage_{countL}')
                langue = create_langue(langage)
                if langue:
                    langages.append(langue)

            # Récupération des formations
            for countF in range(1, 5):
                data = {
                    'ecole': request.POST.get(f'sai_ecole_{countF}'),
                    'date_debut_for': request.POST.get(f'sai_date_debut_for_{countF}'),
                    'date_fin_for': request.POST.get(f'sai_date_fin_for_{countF}'),
                    'resultat_obtenu': request.POST.get(f'sai_resultat_obtenu_{countF}'),
                    'activite_association': request.POST.get(f'sai_activite_association_{countF}'),
                    'domaine_d_etude': request.POST.get(f'sai_domaine_d_etude_{countF}'),
                    'diplome': request.POST.get(f'sai_diplome_{countF}')
                }
                formation = create_formation(data)
                if formation:
                    formations.append(formation)

            # Récupération des expériences
            for countE in range(1, 5):
                data = {
                    'intituler_d_poste': request.POST.get(f'sai_intituler_d_poste_{countE}'),
                    'type_d_emploi': request.POST.get(f'sai_type_d_emploi_{countE}'),
                    'nom_entreprise': request.POST.get(f'sai_nom_entreprise_{countE}'),
                    'lieu': request.POST.get(f'sai_lieu_{countE}'),
                    'date_debut_exp': request.POST.get(f'sai_date_debut_exp_{countE}'),
                    'date_fin_exp': request.POST.get(f'sai_date_fin_exp_{countE}'),
                    'titre': request.POST.get(f'sai_titre_{countE}')
                }
                experience = create_experience(data)
                if experience:
                    experiences.append(experience)

            # Récupération des compétences
            for countC in range(1, 5):
                competence_p = request.POST.get(f'sai_competence_{countC}')
                competence = create_competence(competence_p)
                if competence:
                    competences.append(competence)

            # Création du postulant avec les données récupérées
            postulant = Postulant.objects.create(
                nom=nom,
                prenom=prenom,
                date_de_naissance=date_de_naissance,
                adresse=adresse,
                email=email,
                code_postal=code_postal,
                telephone=telephone,
                copie_diplome=copie_diplome,
                CV=CV,
                LM=LM,
                id_offre_id=offre_id
            )

            # Ajout des langages au postulant
            postulant.langues.set(langages)

            # Ajout des formations au postulant
            postulant.formations.set(formations)

            # Ajout des expériences au postulant
            postulant.experiences.set(experiences)

            # Ajout des compétences au postulant
            postulant.competences.set(competences)


            # Adresse e-mail de l'expéditeur et du destinataire
            sender = 'noreply@msi.mg'
            recipient_list = [email]

            # Sujet et contenu de l'e-mail
            subject = 'Confirmation de candidature'
            message = '''
            Bonjour,

            Merci d'avoir postulé à notre offre d'emploi. Votre candidature a bien été enregistrée.

            Cordialement,
            L'équipe de recrutement
            '''

            # Envoi de l'e-mail
            send_mail(subject, message, sender, recipient_list)

            return redirect('postulant_remerciement')

    return render(request, 'suivis/postulant.html')


def postulant_remerciement(request):
    return render(request, 'suivis/postulant_remerciement.html')

@login_required
def list_postulant(request):
    user_belongs_to_admin_group = request.user.groups.filter(name='Administrateur').exists()
    count = Utilisateurs.objects.filter(is_active=False).count()
    offres = Offre.objects.all()

    selected_offre_id = request.GET.get('id_offre')

    if selected_offre_id:
        postulants = Postulant.objects.filter(id_offre=selected_offre_id)
    else:
        postulants = Postulant.objects.all()

    elements_par_page = 10

    paginator = Paginator(postulants, elements_par_page)
    numero_page = request.GET.get('page')
    page = paginator.get_page(numero_page)

    return render(request, 'suivis/postulants_list.html', {'postulants': page, 'offres': offres, 'count': count, 'user_belongs_to_admin_group': user_belongs_to_admin_group})

@login_required
@user_in_group_required('Recruteur Formateur')
def delete_postulant(request, id):
    # Récupère la pôstulant par ID
    postulant = Postulant.objects.get(pk=id)

    # Supprime la postulant
    postulant.delete()

    # Redirige vers la liste postulant
    return redirect('list_postulant')


@login_required
def liste_collaborateurs_par_projet(request, id_offre):
    # Récupérez le projet en fonction de l'ID passé en paramètre
    offre = Offre.objects.get(id_offre=id_offre)

    # Récupérez la liste des collaborateurs associés à ce projet
    collaborateurs = Offre.collaborateurs.all()

    # Renvoyez la liste des collaborateurs à un modèle de template pour l'affichage
    return render(request, 'liste_collaborateurs.html', {'offre': offre, 'collaborateurs': collaborateurs})

@login_required
@user_in_group_required('Recruteur Formateur')
def ajouter_collaborateur(request, id_postulant):
    postulant = get_object_or_404(Postulant, id_postulant=id_postulant)

    if request.method == 'POST':# vérifier si l'utilisateur est un superuser
        postulant.is_collaborateur = True
        postulant.save()
        messages.success(request, '{} {} a été ajouté en tant que collaborateur.'.format(postulant.nom, postulant.prenom))
        
        # Adresse e-mail de l'expéditeur et du destinataire
        sender = 'noreply@msi.mg'
        recipient_list = [postulant.email]

        # Sujet et contenu de l'e-mail
        subject = 'Acceptation en tant que collaborateur'
        message = f'''
        Cher {postulant.nom} {postulant.prenom},

        J'espère que ce message vous trouve bien. Je vous remercie vivement d'avoir pris le temps de postuler pour un poste au sein de notre entreprise. Nous avons bien reçu votre demande et souhaitons vous informer que votre candidature a été acceptée.

        Nous avons été impressionnés par votre CV, qui démontre vos compétences et votre intérêt pour notre domaine d'activité. Votre profil semble correspondre parfaitement à ce que nous recherchons pour notre équipe.

        Votre candidature est retenue pour la prochaine étape du processus de sélection. Nous sommes impatients de vous rencontrer et de discuter davantage de votre candidature. Merci encore d'avoir accepté cette invitation.

        Encore une fois, merci pour l'intérêt que vous portez à notre entreprise.

        Cordialement,
        L'équipe de recrutement
        '''
        
        # Envoi de l'e-mail
        send_mail(subject, message, sender, recipient_list)
        
        return redirect('list_postulant')

@login_required
@user_in_group_required('Recruteur Formateur')
def retirer_collaborateur(request, id_postulant):
    postulant = get_object_or_404(Postulant, id_postulant=id_postulant)

    if request.method == 'POST':
        postulant.is_collaborateur = False
        postulant.save()
        messages.success(request, '{} {} a été retiré en tant que collaborateur.'.format(postulant.nom, postulant.prenom))
        
        return redirect('list_postulant')
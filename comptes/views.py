"""
Ce module fournit des vues pour l'authentification d'utilisateurs et la gestion de comptes. Il importe diverses fonctions et classes des modules auth, http et shortcuts de Django et 
les utilise pour définir des vues de connexion, de déconnexion, d'inscription et de tableau de bord pour l'application.
"""
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.decorators import login_required
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.urls import reverse
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from comptes.models import Utilisateurs
from django.views import View
from django.views.generic import TemplateView



import mysql.connector

from plateforme.settings import BASE_DIR, MEDIA_ROOT
from comptes.models import Utilisateurs
from datetime import datetime


User = get_user_model()
date = datetime.today()



# Create your views here.

from django.contrib.auth.backends import ModelBackend


def inactive_view(request):
    count = User.objects.filter(is_active=False).count()
    user_belongs_to_admin_group = request.user.groups.filter(name='Administrateur').exists()
    
    return render(request,  {'count':count, 'user_belongs_to_admin_group': user_belongs_to_admin_group})

@login_required
def delete_user(request, id):
    # Récupère l'utilisateur par ID
    user = User.objects.get(pk=id)

    # Supprime l'utilisateur
    user.delete()

    # Redirige vers la page d'accueil ou toute autre page souhaitée
    return redirect('list_users')


def users_view(request):    
    users = User.objects.all()
    count = User.objects.filter(is_active=False).count()
    user_belongs_to_admin_group = request.user.groups.filter(name='Administrateur').exists()
    
    return render(request, 'suivis/list_utilisateurs.html', {'users':users, 'date':date, 'count':count, 'user_belongs_to_admin_group': user_belongs_to_admin_group})

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
    
    def user_can_authenticate(self, user):
        # Add any custom validation for an account being blocked etc.
        return super().user_can_authenticate(user)

               
def signup_view(request):
    if request.method == 'POST':
        # traiter le formulaire
        username = request.POST.get("sai_username")
        email = request.POST.get("sai_email")
        password = request.POST.get("sai_password")
        confirm = request.POST.get("sai_confirm")

        if username != "":
            try:
                if Utilisateurs.objects.get(email=email):
                    messages.error(request, "Cet utilisateur existe déjà! Veuillez en essayer un autre.")
                    return render(request, 'comptes/signup.html')
            except:
                if email == "":
                    messages.error(request, "Veuillez vérifier votre adresse e-mail. Il ne peut pas être vide.")
                    return render(request, 'comptes/signup.html')
                elif password == "":
                    messages.error(request, "Vous devez définir un mot de passe.") 
                    return render(request, 'comptes/signup.html')

                if password == confirm:
                    try:
                        photo = request.FILES['sai_photo']
                        user = User.objects.create_user(
                            username=username, email=email, password=password, photo=photo)
                        login(request, user)
                        return redirect('login')
                    except:
                        user = User.objects.create_user(
                            username=username, email=email, password=password)
                        login(request, user)

                    return redirect('login')
                else:
                    messages.error(request, "Le mot de passe ne correspond pas ! Veuillez réessayer.")  
                    return render(request, 'comptes/signup.html')
                
        else:
            messages.error(request, "Nom d'utilisateur est nécessaire.") 
            return render(request, 'comptes/signup.html')

    return render(request, 'comptes/signup.html')

def login_view(request):
    """
    Connecte l'utilisateur avec des demandes POST.
    """
    if request.method == 'POST':
        # Récupérer les informations de connexion de l'utilisateur depuis le formulaire de connexion
        email = request.POST.get("sai_email")
        password = request.POST.get("sai_password")
        
        # Authentifier l'utilisateur via l'adresse e-mail et le mot de passe fournis
        user = authenticate(request=request, email=email, password=password)
        
        if user is not None and user.is_active:
            # Si le compte est actif, connecter l'utilisateur
            login(request, user)
            
            # Vérifier le groupe de l'utilisateur et rediriger en conséquence
            if user.groups.filter(name='Administrateur').exists():
                return redirect('list_users')
            elif user.groups.filter(name='Recruteur Formateur').exists():
                return redirect('offres_list')
            elif user.groups.filter(name='Responsable Terrain').exists():
                return redirect('projet')
            elif user.groups.filter(name='Directeur Général').exists():
                return redirect('dashboard')
            else:
                # Gérer les cas où l'utilisateur n'appartient à aucun groupe spécifié
                messages.error(request, "Erreur de groupe! Veuillez contacter l'administrateur.")
                return redirect('dashboard')  # Rediriger vers une page par défaut ou un tableau de bord général
                
        else:
            # Si le compte n'est pas actif ou que l'utilisateur n'est pas authentifié, renvoyer un message d'erreur et afficher à nouveau la page de connexion 
            messages.error(request, "Erreur d'authentification! Veuillez réessayer ou contacter l'administrateur si le problème persiste.") 
            return render(request, 'comptes/login.html')

    # Si la méthode HTTP n'est pas POST, renvoyer simplement la page de connexion
    return render(request, 'comptes/login.html')

@login_required
def user_detail(request, user_id):
    # Récupération de l'utilisateur correspondant à l'ID fourni
    user = get_object_or_404(User, id=user_id)
    count = User.objects.filter(is_active=False).count()
    user_belongs_to_admin_group = request.user.groups.filter(name='Administrateur').exists()

    context = {'user': user, 'count':count, 'user_belongs_to_admin_group': user_belongs_to_admin_group}
    return render(request, 'comptes/user_detail.html', context)

@login_required
def activate_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        if request.user.is_superuser: # vérifier si l'utilisateur est un superuser
            user.is_active = True
            user.save()
            messages.success(request, 'Le compte de {} a été activé avec succès.'.format(user.username))
            return redirect('user_detail', user_id=user.id)
        else:
            messages.error(request, 'Vous n\'êtes pas autorisé à activer ce compte.') # rediriger l'utilisateur vers une page de confir
    else:
        message = ""

    # afficher le formulaire d'activation de l'utilisateur
    context = {
        'user': user,
        'message': message
    }
    return render(request, 'suivis/user_detail.html', context)

@login_required
def deactivate_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        if request.user.is_superuser: # vérifier si l'utilisateur est un superuser
            user.is_active = False
            user.save()
            messages.success(request, 'Le compte de {} a été désactivé avec succès.'.format(user.username))
            return redirect('user_detail', user_id=user.id)
        else:
            messages.error(request, 'Vous n\'êtes pas autorisé à activer ce compte.')
    else:
        message = ""

    # afficher le formulaire d'activation de l'utilisateur
    context = {
        'user': user,
        'message': message
    }
    return render(request, 'suivis/user_detail.html', context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    count = User.objects.filter(is_active=False).count()
    user_belongs_to_admin_group = request.user.groups.filter(name='Administrateur').exists()
    
    return render(request, 'comptes/profil.html', {'count':count, 'user_belongs_to_admin_group': user_belongs_to_admin_group})

@login_required
def voir_profile_view(request, id):
    count = User.objects.filter(is_active=False).count()
    user_belongs_to_admin_group = request.user.groups.filter(name='Administrateur').exists()
    user = get_object_or_404(User, id=id)

    context = {'user': user,'count':count, 'user_belongs_to_admin_group': user_belongs_to_admin_group}
    return render(request, 'comptes/profil.html', context)

@login_required
def profile_user_view(request):
    count = User.objects.filter(is_active=False).count()
    user_belongs_to_admin_group = request.user.groups.filter(name='Administrateur').exists()
    
    return render(request, 'comptes/profile-user.html', {'count':count, 'user_belongs_to_admin_group': user_belongs_to_admin_group})

@login_required
def update_profile_view(request, id):
    user = Utilisateurs.objects.get(id=id)
    
    if request.method == "POST":
        #Traiter le formulaire
        first_name = request.POST.get("sai_first_name")
        last_name = request.POST.get("sai_last_name")
        username = request.POST.get("sai_username")
        email = request.POST.get("sai_email")
        
        # Vérifier les données du formulaire
        if username == "":
            messages.error(request, "Un pseudo est requis.")  
            return render(request, 'comptes/profile-user.html')

        if Utilisateurs.objects.filter(email=email).exclude(id=id).exists():
            messages.error(request, "Cet utilisateur existe déjà! Veuillez en essayer un autre.")  
            return render(request, 'comptes/profile-user.html')

        if email == "":
            messages.error(request, "Veuillez vérifier votre adresse e-mail. Il ne peut pas être vide.") 
            return render(request, 'comptes/profile-user.html', {'message':message, 'date':date})
        # elif password == "":
        #     message = "Vous devez définir un mot de passe"
        #     return render(request, 'comptes/profile-user.html', {'message':message, 'date':date})

        # if password != confirm:
        #     message = "Les mots de passe ne correspondent pas ! Veuillez réessayer."
        #     return render(request, 'comptes/profile-user.html', {'message':message, 'date':date})

        # Mettre à jour l'utilisateur
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        # user.set_password(password)
        
        if 'sai_photo' in request.FILES:
            user.photo = request.FILES['sai_photo']
        
        user.save()

        return redirect('profile')
    
    return redirect("profile")

def add_group(request):
    if request.method == 'POST':
        form_data = request.POST
        name = form_data.get("sai_nom_group")
        permissions = form_data.getlist("permissions")

        group = Group.objects.create(name=name)

        for codename in permissions:
            permission = Permission.objects.get(codename=codename)
            group.permissions.add(permission)

        messages.success(request, "Le groupe a été ajouté avec succès !")
        # Remplacez 'nom_de_la_vue' par le nom de la vue qui affiche la liste des groupes.
        return redirect('list_groups')
    else:
        permissions = Permission.objects.all()
        return render(request, 'suivis/list_groups.html', {'permissions': permissions})


def update_group(request, id_group):
    group = Group.objects.get(id=id_group)
    
    if request.method == "POST":
        form_data = request.POST
        name = form_data.get("sai_nom_group")
        
        # Vérifier si le formulaire est valide avant de mettre à jour le groupe
        if name:
            group.name = name
            group.save()
            return redirect("list_groups")

    context = {"group": group}
    return render(request, "suivis/update_group.html", context)

def groups_list(request):
    groups = Group.objects.all()
    count = User.objects.filter(is_active=False).count()
    user_belongs_to_admin_group = request.user.groups.filter(name='Administrateur').exists()
    
    return render(request, 'suivis/list_groups.html', {'groups': groups, 'count':count, 'user_belongs_to_admin_group': user_belongs_to_admin_group})

def group_users(request, group_name):
    group = Group.objects.get(name=group_name)
    users = group.user_set.all()
    count = User.objects.filter(is_active=False).count()
    user_belongs_to_admin_group = request.user.groups.filter(name='Administrateur').exists()
    
    return render(request, 'suivis/list_groups_user.html', {'users': users, 'group': group, 'count': count, 'user_belongs_to_admin_group': user_belongs_to_admin_group})

def delete_group(request, group_id):
    # Récupère l'utilisateur par ID
    group = Group.objects.get(id=group_id)

    # Supprime l'utilisateur
    group.delete()

    # Redirige vers la page d'accueil ou toute autre page souhaitée
    return redirect('list_groups')

def add_user_to_group_view(request):
    if request.method == 'POST':
        # Récupérer les données POST
        username = request.POST['username']
        group_name = request.POST['group_name']
        
        try:
            # Récupérer l'utilisateur et le groupe
            user = User.objects.get(username=username)
            group = Group.objects.get(name=group_name)

            # Ajouter l'utilisateur au groupe
            group.user_set.add(user)

            # Afficher un message de succès
            messages.success(request, f"{user.username} a été ajouté à {group.name} groupe!")
            
            return redirect('add-user-to-group')

        except User.DoesNotExist:
            # Si l'utilisateur n'existe pas, afficher un message d'erreur
            messages.error(request, "L'utilisateur n'existe pas.")
        
        except Group.DoesNotExist:
            # Si le groupe n'existe pas, afficher un message d'erreur
            messages.error(request, "Le groupe n'existe pas.")

    # Récupérer tous les groupes et tous les utilisateurs sans groupe
    groups = Group.objects.all()
    users_without_group = User.objects.filter(groups=None)
    count = User.objects.filter(is_active=False).count()
    user_belongs_to_admin_group = request.user.groups.filter(name='Administrateur').exists()

    
    context = {'groups': groups, 'users_without_group': users_without_group, 'count':count, 'user_belongs_to_admin_group':user_belongs_to_admin_group}

    return render(request, 'suivis/add_user_to_group.html', context)

class SupprimerUtilisateurGroupeView(View):
    def post(self, request, *args, **kwargs):
        # Récupérez l'utilisateur et le groupe en question
        user = User.objects.get(pk=self.kwargs['pk'])
        group = Group.objects.get(name=self.kwargs['nom_groupe'])

        # Supprimez l'utilisateur du groupe
        group.user_set.remove(user)

        # Redirigez l'utilisateur vers la page de confirmation
        return redirect(reverse_lazy('confirmation_suppression_utilisateur'))

    def get(self, request, *args, **kwargs):
        # Affichez une formulaire de confirmation de suppression
        user = User.objects.get(pk=self.kwargs['pk'])
        nom_groupe = self.kwargs['nom_groupe']
        return render(request, 'suivis/list_groups.html', {'user': user, 'nom_groupe': nom_groupe})
    
class ConfirmationSuppressionUtilisateurView(TemplateView):
    template_name = 'suivis/confirmation_suppression_utilisateur.html'
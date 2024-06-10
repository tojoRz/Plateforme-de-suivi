"""
URL configuration for plateforme project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include


from plateforme import settings

from django.conf.urls.static import static
from comptes.views import login_view,signup_view,logout_view,users_view,profile_view,profile_user_view,update_profile_view, activate_user, user_detail,voir_profile_view, deactivate_user,delete_user,groups_list, group_users, add_group,delete_group, update_group,add_user_to_group_view,SupprimerUtilisateurGroupeView, ConfirmationSuppressionUtilisateurView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),
    path('', include('suivis.urls')),
    path("S'inscrire/", signup_view, name='signup'),
    path('Se connecter/', login_view, name='login'),
    path('Déconnecter/', logout_view, name='logout'),
    path('Utilisateur/', users_view, name='list_users'),
    path('Activate-user/<int:user_id>/', activate_user, name='activate_user'),
    path('Deactivate-user/<int:user_id>/', deactivate_user, name='deactivate_user'),
    path('Utilisateur/<int:user_id>/', user_detail, name='user_detail'),
    path('Utilisateur/Supprimer/<int:id>', delete_user, name='delete_user'),
    path('Groupe/Ajouter', add_group, name='add_group'),
    path('Groupe/',groups_list,name='list_groups'),
    path('Groupe/<str:group_name>/users/', group_users, name='group_users'),
    path('Groupe/<int:id_group>/update/', update_group, name='update_group'),
    path('Groupe/delete/<int:group_id>/', delete_group, name='delete_group'),
    path('Groupe/add-user-to-group/', add_user_to_group_view, name='add-user-to-group'),
    path('Groupe/<str:nom_groupe>/utilisateurs/<int:pk>/supprimer', SupprimerUtilisateurGroupeView.as_view(), name='supprimer_utilisateur_groupe'),
    path('confirmation_suppression_utilisateur/', ConfirmationSuppressionUtilisateurView.as_view(), name='confirmation_suppression_utilisateur'),
    path('Profile/', profile_view, name='profile'),
    path('Profile/Modifier/', profile_user_view, name='profile-user'),
    path('Profile/Modifier/<int:id>', update_profile_view, name='update-profile'),
    path('Resultat/Voir/<int:id>', voir_profile_view, name='voir-user'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

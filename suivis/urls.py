from django.urls import path, include
from suivis.views import dashboard, projet_list, add_projet, voir_projet, delete_projet, offres_list, add_offre, offres_detail, search_offre_view, add_postulant, postulant_remerciement, list_postulant, voir_offre, offres_views, delete_offre, projects_data, delete_postulant, update_offre_view, update_projet_view,run_update_proj_statuts,ajouter_collaborateur,liste_collaborateurs_par_projet, retirer_collaborateur

urlpatterns = [
    path('Dashboard/', dashboard, name='dashboard'),
    path('Projets/', projet_list, name='projet'),
    path('Projets/Ajouter/', add_projet, name='add_projet'),
    path('Projets/Voir/<int:id>/', voir_projet, name='voir_projet'),
    path('Projets/Modifier/<int:id>', update_projet_view, name='update_projet'),
    path('Projets/Supprimer/<int:id>/', delete_projet, name='delete_projet'),
    path('update_proj_statuts/', run_update_proj_statuts, name='update_proj_statuts'),
    path('api/projects/', projects_data, name='projects_data'),
    path('Offres/', offres_list, name='offre'),
    path('Offres/Listes/', offres_views, name='offres_list'),
    path('Offres/Ajouter/', add_offre, name='add_offre'),
    path('Offres/Voir/<int:offre_id>/', offres_detail, name='offres_detail'),
    path('Offres/Voirs/<int:id>',voir_offre, name='voir_offre'), 
    path('Offres/Modifier/<int:id>', update_offre_view, name='update_offre'),
    path('Offres/Supprimer/<int:id>/', delete_offre, name='delete_offre'),
    path('Postulant/<int:offre_id>/', add_postulant, name='add_postulant'),
    path('Postulant/remerciement/', postulant_remerciement, name='postulant_remerciement'),
    path('Postulant/listes/', list_postulant, name='list_postulant'),
    path('Projet/<int:id_offre>/collaborateurs/', liste_collaborateurs_par_projet, name='liste_collaborateurs_par_projet'),
    path('Ajouter_collaborateur/<str:id_postulant>/', ajouter_collaborateur, name='ajouter_collaborateur'),
    path('Retirer_collaborateur/<str:id_postulant>/', retirer_collaborateur, name='retirer_collaborateur'),
    path('Postulant/Supprimer/<str:id>/', delete_postulant, name='delete_postulant'),
    path('Resultat/', search_offre_view, name='search'),

    
]

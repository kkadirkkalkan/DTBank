from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.userloginpage, name='login'),
    path('managerlogin/', views.managerlogin, name='managerlogin'),
    path('userdirect/', views.login, name="userdirect"),
    path('managerloginpage/', views.managerloginpage, name='managerloginpage'),
    path('managerdirect/', views.managerlogin, name="managerdirect"),
    path('managerhome/', views.managerhome, name="managerhome"),
    path('userhome/', views.userhome, name="userhome"),
    path('saveuser/', views.saveuser, name='saveuser'),
    path('encrypt/', views.encrypt_passwords, name='encrypt'),
    path('update_affinity/', views.update_affinity),
    path('delete_drug/', views.delete_drug),
    path('delete_protein/', views.delete_protein),
    path('viewtable/<str:tablename>', views.viewtable),
    path('viewusers/', views.viewusers),
    path('viewpapers/', views.viewpapers),
    path('updatecontributors/', views.updateContributors),
    path('removeauthor/<str:username>/<str:reaction_id>', views.removeauthor),
    path('addauthors/<str:reaction_id>', views.addauthors),
    path('adduserasauthor/<str:reaction_id>', views.addUserAsAuthor),
    path('viewdruginteractions/', views.viewdruginteractions),
    path('viewsideeffects/', views.viewSideEffects),
    path('viewproteininteractings/', views.viewproteininteractings),
    path('viewdruginteractingtargets/', views.viewdruginteractingtargets),
    path('viewdrugswithsider/', views.viewdrugswithsider),
    path('viewdrugsleastside/', views.viewdrugsleastside),
    path('filterdruginteractingtargets/', views.filterdruginteractingtargets),
    path('searchandviewdrugs/', views.searchandviewdrugs),
    path('sameproteindrugs/', views.sameproteindrugs),
    path('rankinstitutes/', views.rankinstitutes),
    path('samedrugproteins/', views.samedrugproteins),
    path('viewdruginfo/', views.viewDrugInfo)


]

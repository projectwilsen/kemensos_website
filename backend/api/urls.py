from django.urls import path
from .views import Berita, KataMasyarakatDetail, index, kata_masyarakat

urlpatterns = [
    path('', index, name='index'),
    path('kata-masyarakat/pkh/', kata_masyarakat, {'program_id': 1, 'template_name': 'program.html'}, name='pkh'),
    path('kata-masyarakat/bpnt/', kata_masyarakat, {'program_id': 2, 'template_name': 'program.html'}, name='bpnt'),
    path('kata-masyarakat/bansos/', kata_masyarakat, {'program_id': 3, 'template_name': 'program.html'}, name='bansos'),
    path('kata-masyarakat/blt/', kata_masyarakat, {'program_id': 4, 'template_name': 'program.html'}, name='blt'),
    path('kata-masyarakat/kip/', kata_masyarakat, {'program_id': 5, 'template_name': 'program.html'}, name='kip'),
    path('kata-masyarakat/kis/', kata_masyarakat, {'program_id': 6, 'template_name': 'program.html'}, name='kis'),
    path('kata-masyarakat/rastra/', kata_masyarakat, {'program_id': 7, 'template_name': 'program.html'}, name='rastra'),
    path('kata-masyarakat/raskin/', kata_masyarakat, {'program_id': 8, 'template_name': 'program.html'}, name='raskin'),
    path('kata-masyarakat/kube/', kata_masyarakat, {'program_id': 9, 'template_name': 'program.html'}, name='kube'),
    path('kata-masyarakat/sembako/', kata_masyarakat, {'program_id': 10, 'template_name': 'program.html'}, name='sembako'),
    path('kata-masyarakat/rehabilitasi/', kata_masyarakat, {'program_id': 11, 'template_name': 'program.html'}, name='rehabilitasi'),
    path('kata-masyarakat/kat/', kata_masyarakat, {'program_id': 12, 'template_name': 'program.html'}, name='kat'),
    path('berita/', Berita.as_view(), name='berita'),
    path('kata-masyarakat/<int:id>/', KataMasyarakatDetail.as_view(), name='kata-masyarakat-detail')
]
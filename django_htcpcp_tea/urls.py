#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

from django.urls import path

from .views import brew_pot

urlpatterns = [
    path('', brew_pot, name='htcpcp-index'),
    path('pot-<int:pot_designator>/', brew_pot, name='pot-detail'),
    path('pot-<int:pot_designator>/<str:tea_type>/', brew_pot, name='pot-detail-tea')

]

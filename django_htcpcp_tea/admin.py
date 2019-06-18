#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

from django.contrib import admin
from django.db.models import Count

from .models import Addition, Pot, TeaType


class BrewTeaListFilter(admin.SimpleListFilter):
    """Admin list filter for whether a pots serves any teas."""

    title = 'able to brew tea'

    parameter_name = 'brew_tea'

    def lookups(self, request, model_admin):
        return (
            ('y', 'Yes'),
            ('n', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()

        if value == 'y':
            return queryset.filter(supported_teas__isnull=False)

        if value == 'n':
            return queryset.filter(supported_teas__isnull=True)


@admin.register(Pot)
class PotAdmin(admin.ModelAdmin):
    search_fields = ('supported_teas__name', 'supported_additions__name')

    fields = (('name', 'brew_coffee'), 'supported_teas', 'supported_additions')

    list_display = ('id', 'name', 'brew_coffee', 'tea_capable_view', 'tea_count_view', 'addition_count_view')

    list_display_links = ('id', 'name')

    filter_horizontal = ('supported_teas', 'supported_additions')

    list_filter = ('brew_coffee', BrewTeaListFilter, ('supported_teas', admin.RelatedOnlyFieldListFilter))

    save_as = True

    def tea_capable_view(self, obj):
        """Display whether the given pot can brew tea."""
        return obj.tea_capable

    tea_capable_view.boolean = True
    tea_capable_view.short_description = "able to brew tea"
    tea_capable_view.admin_order_field = 'supported_teas'

    def tea_count_view(self, obj):
        "Display the number of tea types that the given pot supports."
        return obj.tea_count

    tea_count_view.admin_order_field = 'tea_count'
    tea_count_view.short_description = 'supported teas'

    def addition_count_view(self, obj):
        "Display the number of addition types that the given pot supports."
        return obj.addition_count

    addition_count_view.admin_order_field = 'addition_count'
    addition_count_view.short_description = 'supported additions'

    def get_queryset(self, request):
        return super().get_queryset(request).with_tea_count().with_addition_count()


class PotsServingMixin:
    """Mixin to add a 'pots serving' item of a model admin's list_display."""

    def get_list_display(self, request):
        fields = super().get_list_display(request)
        serving_callable = self.pots_serving_count_view.__name__
        if serving_callable not in fields:
            return fields + (serving_callable,)
        return fields

    def pots_serving_count_view(self, obj):
        """Display the number of pots that serve the given object."""
        return obj.pot_count

    pots_serving_count_view.admin_order_field = 'pot_count'
    pots_serving_count_view.short_description = 'pots serving'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(pot_count=Count('pot'))


@admin.register(TeaType)
class TeaTypeAdmin(PotsServingMixin, admin.ModelAdmin):
    search_fields = ('name',)

    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('slug',),
        }),
    )


@admin.register(Addition)
class AdditionAdmin(PotsServingMixin, admin.ModelAdmin):
    search_fields = ('name',)

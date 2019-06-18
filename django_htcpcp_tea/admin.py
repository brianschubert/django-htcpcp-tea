#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

from django.contrib import admin

from .models import Addition, Pot, TeaType


class BrewTeaListFilter(admin.SimpleListFilter):
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

    list_display = ('id', 'name', 'brew_coffee', 'is_teapot_view')

    list_display_links = ('id', 'name')

    filter_horizontal = ('supported_teas', 'supported_additions')

    list_filter = ('brew_coffee', BrewTeaListFilter, ('supported_teas', admin.RelatedOnlyFieldListFilter))

    save_as = True

    def is_teapot_view(self, obj):
        return obj.is_teapot

    is_teapot_view.boolean = True
    is_teapot_view.short_description = "Is a teapot?"


@admin.register(TeaType)
class PotAdmin(admin.ModelAdmin):
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
class PotAdmin(admin.ModelAdmin):
    pass

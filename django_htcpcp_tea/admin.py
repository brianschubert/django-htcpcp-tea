#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.db import models

from .models import Addition, ForbiddenCombination, Pot, TeaType


class RelatedItemsExistsListFilter(admin.SimpleListFilter):
    """Admin list filter for whether an object has a ManyToMany related item."""
    related_item_field = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.related_item_field:
            error_msg = 'The list filter {} does not specify a related_item_field'
            raise ImproperlyConfigured(error_msg.format(self.__class__.__name__))

    def lookups(self, request, model_admin):
        return (
            ('y', 'Yes'),
            ('n', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        lookup_param = '{}__isnull'.format(self.related_item_field)

        if value == 'y':
            return queryset.filter(**{lookup_param: False})

        if value == 'n':
            return queryset.filter(**{lookup_param: True})


class BrewTeaListFilter(RelatedItemsExistsListFilter):
    """Admin list filter for whether a pots serves any teas."""
    title = 'able to brew tea'

    parameter_name = 'brew_tea'

    related_item_field = 'supported_teas'


class ServedByAPotListFilter(RelatedItemsExistsListFilter):
    """Admin list filter for whether an object is served by a pot."""
    title = 'served by a pot'

    parameter_name = 'is_served'

    related_item_field = 'pot_list'


class SomeCombinationsForbiddenListFilter(RelatedItemsExistsListFilter):
    title = 'has forbidden combinations'

    parameter_name = 'has_restrictions'

    related_item_field = 'forbidden_combinations'


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
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('supported_teas')
        queryset = queryset.prefetch_related('supported_additions')
        return queryset.with_tea_count().with_addition_count()


class PotsServingMixin:
    """
    Mixin to add a 'pots serving' item to a model admin's list_display
    and list_filter
    """

    def get_list_display(self, request):
        fields = super().get_list_display(request)
        serving_callable = self.pots_serving_count_view.__name__
        if serving_callable not in fields:
            return fields + (serving_callable,)
        return fields

    def get_list_filter(self, request):
        return (ServedByAPotListFilter,) + super().get_list_filter(request)

    def pots_serving_count_view(self, obj):
        """Display the number of pots that serve the given object."""
        return obj.pot_count

    pots_serving_count_view.admin_order_field = 'pot_count'
    pots_serving_count_view.short_description = 'pots serving'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            pot_count=models.Count('pot_list', distinct=True)
        )


class HasForbiddenCombinationsMixin:
    """
    Mixin to add a 'forbidden combinations' item to a model admin's
    list_display and list_filter.
    """

    def get_list_display(self, request):
        fields = super().get_list_display(request)
        forbidden_callable = self.forbidden_combination_count_view.__name__
        if forbidden_callable not in fields:
            return fields + (forbidden_callable,)
        return fields

    def get_list_filter(self, request):
        return super().get_list_filter(request) + (SomeCombinationsForbiddenListFilter,)

    def forbidden_combination_count_view(self, obj):
        """
        Display the number of forbidden combinations that include the
        given object.
        """
        return obj.forbidden_count

    forbidden_combination_count_view.admin_order_field = 'forbidden_count'
    forbidden_combination_count_view.short_description = 'forbidden combinations'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            forbidden_count=models.Count('forbidden_combinations', distinct=True)
        )


class ForbiddenCombinationInline(admin.TabularInline):
    model = ForbiddenCombination

    fields = ('reason', 'additions')

    extra = 0

    filter_horizontal = ('additions',)

    classes = ('collapse',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('tea').prefetch_related('additions')


@admin.register(TeaType)
class TeaTypeAdmin(PotsServingMixin, HasForbiddenCombinationsMixin, admin.ModelAdmin):
    inlines = (ForbiddenCombinationInline,)

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
class AdditionAdmin(PotsServingMixin, HasForbiddenCombinationsMixin, admin.ModelAdmin):
    search_fields = ('name',)

    list_display = ('name', 'type')

    list_filter = ('type',)

    radio_fields = {'type': admin.HORIZONTAL}


@admin.register(ForbiddenCombination)
class ForbiddenCombinationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'reason')

    search_fields = ('additions__name', 'tea__name')

    list_filter = (('tea', admin.RelatedOnlyFieldListFilter), ('additions', admin.RelatedOnlyFieldListFilter))

    filter_horizontal = ('additions',)

    save_as = True

    formfield_overrides = {
        models.ForeignKey: {'empty_label': '------ All ------'},
    }

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('tea').prefetch_related('additions')

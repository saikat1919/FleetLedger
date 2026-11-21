from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Company, User

# Register your models here.

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "contact_person_email",
        "status",
        "created_at",
    )
    search_fields = ("company_name", "contact_person_email")
    list_filter = ("status",)


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "email",
        "role",
        "company",
        "is_active",
    )
    list_filter = ("role", "company", "is_active")
    search_fields = ("username", "email")

    fieldsets = UserAdmin.fieldsets + (
        ("FleetLedger Information", {
            "fields": ("role", "company"),
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username",
                "email",
                "first_name",
                "last_name",
                "role",
                "company",
                "password1",
                "password2",
            ),
        }),
    )

    def has_module_permission(self, request):
        return request.user.role in [
            "platform_admin",
            "company_admin",
        ]

    def has_add_permission(self, request):
        return request.user.role in [
            "platform_admin",
            "company_admin",
        ]

    def has_view_permission(self, request, obj=None):
        if request.user.role == "platform_admin":
            return True

        if request.user.role == "company_admin":
            if obj is None:
                return True

            return (
                obj.company_id == request.user.company_id
                and obj.role == "company_manager"
            )

        return False

    def has_change_permission(self, request, obj=None):
        if request.user.role == "platform_admin":
            return True

        if request.user.role == "company_admin":
            if obj is None:
                return True

            return (
                obj.company_id == request.user.company_id
                and obj.role == "company_manager"
            )

        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        if request.user.role == "company_admin":
            return queryset.filter(
                company=request.user.company,
                role="company_manager",
            )

        return queryset

    def formfield_for_choice_field(self, db_field, request, **kwargs):

        is_add = (
            request.resolver_match
            and request.resolver_match.url_name.endswith("_add")
        )

        if db_field.name == "role" and is_add:

            if request.user.role == "platform_admin":
                kwargs["choices"] = [
                    ("company_admin", "Company Admin"),
                ]

            elif request.user.role == "company_admin":
                kwargs["choices"] = [
                    ("company_manager", "Company Manager"),
                ]

        return super().formfield_for_choice_field(
            db_field,
            request,
            **kwargs,
        )

    def save_model(self, request, obj, form, change):

        if not change:

            if request.user.role == "platform_admin":
                obj.role = "company_admin"
                obj.is_staff = True
                obj.is_superuser = False

            elif request.user.role == "company_admin":
                obj.role = "company_manager"
                obj.company = request.user.company
                obj.is_staff = False
                obj.is_superuser = False

        super().save_model(request, obj, form, change)

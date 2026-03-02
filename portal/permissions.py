from rest_framework import permissions

class IsAdminUserOrVolunteer(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in ['ADMIN', 'VOLUNTEER'])

class IsAdminOrFaculty(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in ['ADMIN', 'FACULTY', 'VOLUNTEER'])

class IsAuthorOrAdminOrVolunteer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the author or an admin/volunteer.
        is_admin_volunteer = bool(request.user and request.user.role in ['ADMIN', 'VOLUNTEER'])
        has_author_attr = hasattr(obj, 'author') and obj.author == request.user
        has_posted_by_attr = hasattr(obj, 'posted_by') and obj.posted_by == request.user
        return is_admin_volunteer or has_author_attr or has_posted_by_attr

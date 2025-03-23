from rest_framework.permissions import BasePermission, SAFE_METHODS


class FundamentalPermission(BasePermission):
    __permissions_dict: dict[str, str] = {
        'list': 'view',
        'retrieve': 'view',
        'fetch': 'view',
        'create': 'add',
        'partial_update': 'change',
        'update': 'change',
        'partial': 'change',
        'destroy': 'delete'
    }

    __allowed_permission_types: list[str] = ['view', 'crud']

    def _get_permission_code(self, action, model_class):
        app_label = model_class.model._meta.app_label
        model_name = model_class.model._meta.model_name
        permission_action = self.__permissions_dict.get(action)

        if not permission_action:
            return None

        return f'{app_label}.{permission_action}_{model_name}'

    def has_permission(self, request, view):
        permission_type = getattr(view, 'permission_type', 'view')
        action = getattr(view, 'action', None).split('_')[0]
        model_class = getattr(view, 'queryset', None)

        if action in ["login", "register", 'refresh', 'logout', 'is'] or request.user.is_superuser:
            return True

        if not request.user.is_authenticated or not action or not model_class or permission_type not in self.__allowed_permission_types:
            return False

        if permission_type == 'view' and request.method not in SAFE_METHODS:
            return False

        user_id = request.parser_context['kwargs'].get('pk')
        if user_id and (str(request.user.id) != str(user_id)):
            return False

        permission_code = self._get_permission_code(action, model_class)
        return request.user.has_perm(permission_code)

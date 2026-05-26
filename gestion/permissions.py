SYSTEM_ROLES = ('Administrador', 'Mesero', 'Cajero')


def user_roles(user):
    if not user.is_authenticated:
        return set()
    if user.is_superuser:
        return set(SYSTEM_ROLES)
    return set(
        user.groups.filter(name__in=SYSTEM_ROLES).values_list('name', flat=True)
    )


def user_has_any_role(user, *roles):
    return bool(user_roles(user).intersection(roles))


def user_is_admin(user):
    return user.is_superuser or 'Administrador' in user_roles(user)


def user_is_solo_mesero(user):
    roles = user_roles(user)
    return 'Mesero' in roles and not roles.intersection({'Administrador', 'Cajero'})


def user_is_solo_cajero(user):
    roles = user_roles(user)
    return 'Cajero' in roles and not roles.intersection({'Administrador', 'Mesero'})

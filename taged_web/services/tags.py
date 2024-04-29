from taged_web.models import Tags, User


def get_available_tags(user: User) -> list[str]:
    return list(
        Tags.objects.all().values_list("tag_name", flat=True)
        if user.is_superuser
        else Tags.objects.filter(user=user).values_list("tag_name", flat=True)
    )


def get_unavailable_tags(user: User) -> list[str]:
    all_tags = set(Tags.objects.all().values_list("tag_name", flat=True))
    return list(set(all_tags) - set(get_available_tags(user)))


def add_tags_to_user_if_not_exist(tags_names: list[str], by_user: User) -> None:
    """
    Принимает строку названий тегов и создает отсутствующие из них.
    Затем добавляет их к пользователю.
    """
    for tag_name in tags_names:
        tag, created = Tags.objects.get_or_create(tag_name=tag_name)  # type: Tags, bool
        if created:
            tag.user.add(by_user.id)

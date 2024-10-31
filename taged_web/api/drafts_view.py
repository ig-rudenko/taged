from uuid import uuid4

from django.core.cache import cache
from django.http import Http404
from rest_framework import viewsets
from rest_framework.response import Response

from ..es_index import PostIndex


class DraftsViewSet(viewsets.ViewSet):
    def list(self, request):
        drafts = self.get_drafts() or []
        return Response(drafts)

    def create(self, request):
        request.data.setdefault("id", str(uuid4()))
        self.set_preview(request.data)

        self.save_draft(request.data, request.data["id"])
        return Response(request.data)

    def retrieve(self, request, pk=None):
        draft = cache.get(self.get_cache_key(pk))
        if draft is None:
            raise Http404("Черновик не найден")
        return Response(draft)

    def update(self, request, pk: str):
        request.data["id"] = pk
        self.set_preview(request.data)

        self.save_draft(request.data, pk)
        return Response(request.data)

    def destroy(self, request, pk=None):
        self.delete_draft(pk)
        return Response(status=204)

    def get_cache_key(self, pk=None) -> str:
        if pk is None:
            return f"drafts:{self.request.user}"
        return f"drafts:{self.request.user}:{pk}"

    def get_drafts(self, pk=None) -> dict | None:
        return cache.get(self.get_cache_key(pk))

    def delete_draft(self, pk: str) -> None:
        cache.delete(self.get_cache_key(pk))

        all_drafts = self.get_drafts() or []
        # Обновляем список существующих drafts, удаляя черновик с указанным id.
        new_drafts = []
        for stored_draft in all_drafts:
            if stored_draft.get("id") != pk:
                # Пропускаем текущий черновик
                new_drafts.append(stored_draft)

        # Обновляем список черновиков.
        cache.set(self.get_cache_key(), new_drafts, timeout=None)

    def save_draft(self, data: dict, pk: str) -> None:
        data = data.copy()
        draft = self.get_drafts(pk)

        # Сохраняем новое значение в кэш.
        cache.set(self.get_cache_key(pk), data, timeout=None)

        # Удаляем содержимое черновика, так как в списке черновиков оно не должно быть.
        data.pop("content", None)

        # Если черновик существовал ранее, то проверяем, нужно ли обновлять его.
        if (
            draft is None
            or draft.get("title") != data.get("title")
            or draft.get("tags") != data.get("tags")
            or draft.get("previewImage") != data.get("previewImage")
        ):
            # Если имеется разница в полях заголовка и списка тегов, то обновляем список черновиков.
            all_drafts = self.get_drafts() or []
            # Обновляем список существующих drafts, добавляя новое значение в начало.
            new_drafts = [data]
            for stored_draft in all_drafts:
                if stored_draft.get("id") != pk:
                    # Пропускаем текущий черновик, т.к. он добавлен в начало.
                    new_drafts.append(stored_draft)

            # Обновляем список черновиков.
            cache.set(self.get_cache_key(), new_drafts, timeout=None)

    @staticmethod
    def set_preview(data: dict) -> None:
        data["previewImage"] = PostIndex.get_first_image_url(data.get("content", ""))

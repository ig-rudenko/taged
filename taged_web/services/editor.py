from django.core.cache import cache


class Editor:
    timeout = 4  # seconds

    def __init__(self, uuid: str):
        self._uuid = uuid

    def set_edit_note(self, note_uuid: str):
        self._register()
        self._set_target_note(note_uuid)

        editors = []
        if (data := cache.get(f"noteEditors:{note_uuid}")) is not None:
            editors = data
        if self._uuid not in editors:
            editors.append(self._uuid)

        cache.set(f"noteEditors:{note_uuid}", editors, timeout=self.timeout)

    def _register(self):
        cache_key = "editors"
        editors = []
        if (data := cache.get(cache_key)) is not None:
            editors = data

        if self._uuid not in editors:
            editors.append(self._uuid)

        cache.set(cache_key, editors, timeout=self.timeout)

    def _set_target_note(self, note_uuid: str):
        cache.set(f"editors:{self._uuid}", note_uuid, timeout=self.timeout)

    @classmethod
    def get_target(cls, editor_uuid: str) -> str | None:
        return cache.get(f"editors:{editor_uuid}")


class NoteEditors:
    timeout = 10  # seconds

    def __init__(self, uuid: str):
        self._uuid = uuid

    def get_active_editors(self) -> list[str]:
        editors: list[str] = cache.get(f"noteEditors:{self._uuid}") or []

        valid_editors = []
        for editor in editors:
            if Editor.get_target(editor) == self._uuid:
                valid_editors.append(editor)

        cache.set(f"noteEditors:{self._uuid}", valid_editors, timeout=self.timeout)

        return valid_editors

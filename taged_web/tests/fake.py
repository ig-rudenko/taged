from typing import Any

from elasticsearch import Elasticsearch


class FakeElasticsearch(Elasticsearch):

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.index_docs = []
        self.delete_ids = []

    def clear_fake_data(self):
        self.index_docs = []
        self.delete_ids = []

    def get(
        self,
        *,
        index,
        id,
        doc_type=...,
        _source=...,
        _source_excludes=...,
        _source_includes=...,
        preference=...,
        realtime=...,
        refresh=...,
        routing=...,
        stored_fields=...,
        version=...,
        version_type=...,
        pretty=...,
        human=...,
        error_trace=...,
        format=...,
        filter_path=...,
        request_timeout=...,
        ignore=...,
        opaque_id=...,
        http_auth=...,
        api_key=...,
        params=...,
        headers=...,
    ):
        return {
            "_source": {
                "title": "title",
                "content": "content",
                "tags": ["tag1", "tag2"],
                "published_at": "2024-04-28T00:00:00.866799",
            }
        }

    def index(
        self,
        *,
        index,
        document,
        doc_type=...,
        id=...,
        if_primary_term=...,
        if_seq_no=...,
        op_type=...,
        pipeline=...,
        refresh=...,
        require_alias=...,
        routing=...,
        timeout=...,
        version=...,
        version_type=...,
        wait_for_active_shards=...,
        pretty=...,
        human=...,
        error_trace=...,
        format=...,
        filter_path=...,
        request_timeout=...,
        ignore=...,
        opaque_id=...,
        http_auth=...,
        api_key=...,
        params=...,
        headers=...,
    ):
        self.index_docs.append(document)
        return {"_id": id}

    def delete(
        self,
        *,
        index,
        id,
        doc_type=...,
        if_primary_term=...,
        if_seq_no=...,
        refresh=...,
        routing=...,
        timeout=...,
        version=...,
        version_type=...,
        wait_for_active_shards=...,
        pretty=...,
        human=...,
        error_trace=...,
        format=...,
        filter_path=...,
        request_timeout=...,
        ignore=...,
        opaque_id=...,
        http_auth=...,
        api_key=...,
        params=...,
        headers=...,
    ):
        self.delete_ids.append(id)
        return {"_shards": {"failed": 0, "successful": 1, "total": 1}}

    def count(
        self,
        *,
        body=...,
        index=...,
        doc_type=...,
        allow_no_indices=...,
        analyze_wildcard=...,
        analyzer=...,
        default_operator=...,
        df=...,
        expand_wildcards=...,
        ignore_throttled=...,
        ignore_unavailable=...,
        lenient=...,
        min_score=...,
        preference=...,
        q=...,
        routing=...,
        terminate_after=...,
        pretty=...,
        human=...,
        error_trace=...,
        format=...,
        filter_path=...,
        request_timeout=...,
        ignore=...,
        opaque_id=...,
        http_auth=...,
        api_key=...,
        params=...,
        headers=...,
    ):
        return {"count": 123}

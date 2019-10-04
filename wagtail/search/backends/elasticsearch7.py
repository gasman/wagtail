from .elasticsearch2 import ElasticsearchAutocompleteQueryCompilerImpl
from .elasticsearch6 import (
    Elasticsearch6Index,
    Elasticsearch6Mapping,
    Elasticsearch6SearchBackend,
    Elasticsearch6SearchQueryCompiler,
    Elasticsearch6SearchResults,
)


class Elasticsearch7Mapping(Elasticsearch6Mapping):
    pass


class Elasticsearch7Index(Elasticsearch6Index):
    def add_model(self, model):
        # Get mapping
        mapping = self.mapping_class(model)

        # Put mapping
        self.es.indices.put_mapping(
            index=self.name,
            doc_type=mapping.get_document_type(),
            body=mapping.get_mapping(),
            include_type_name=True,
        )


class Elasticsearch7SearchQueryCompiler(Elasticsearch6SearchQueryCompiler):
    mapping_class = Elasticsearch6Mapping


class Elasticsearch7SearchResults(Elasticsearch6SearchResults):
    pass


class Elasticsearch7AutocompleteQueryCompiler(
    Elasticsearch6SearchQueryCompiler, ElasticsearchAutocompleteQueryCompilerImpl
):
    pass


class Elasticsearch7SearchBackend(Elasticsearch6SearchBackend):
    mapping_class = Elasticsearch7Mapping
    index_class = Elasticsearch7Index
    query_compiler_class = Elasticsearch7SearchQueryCompiler
    autocomplete_query_compiler_class = Elasticsearch7AutocompleteQueryCompiler
    results_class = Elasticsearch7SearchResults

    def __init__(self, params):
        self.settings["settings"]["index"] = {"max_ngram_diff": 12}
        super().__init__(params)


SearchBackend = Elasticsearch7SearchBackend

from pydantic import BaseModel, Field


# ── Retrieval request generation ─────────────────────────────────────────────

class QdrantCondition(BaseModel):
    key: str = Field(description=(
        "Klucz pola w payloadzie, np. 'metadata.bible_part'. "
        "Zawsze poprzedź nazwę pola prefiksem 'metadata.'."
    ))
    value: str = Field(description=(
        "Wartość pola – MUSI być dosłownie jedną z wartości z listy unikalnych wartości metadanych. "
        "Skopiuj wartość znak w znak."
    ))


class QdrantFilter(BaseModel):
    must: list[QdrantCondition] = Field(
        default_factory=list,
        description="Warunki AND – WSZYSTKIE muszą być spełnione jednocześnie.",
    )
    should: list[QdrantCondition] = Field(
        default_factory=list,
        description="Warunki OR – przynajmniej jeden musi być spełniony.",
    )
    must_not: list[QdrantCondition] = Field(
        default_factory=list,
        description="Warunki NOT – żaden nie może być spełniony.",
    )


def build_retrieval_request_model(
    top_k_popular: int,
    top_k_standard: int,
    top_k_specific: int,
    metadata_json: str,
):
    class RetrievalRequest(BaseModel):
        query_text: str = Field(description=(
            "Zapytanie zoptymalizowane pod kątem semantycznego wyszukiwania wersetów Biblii. "
            "Przeformułuj pytanie użytkownika tak, aby retriever odnalazł jak najlepiej pasujące wersety. "
            "Nie zawieraj w nim informacji o konkretnej księdze lub części Biblii – te trafią do filtrów. "
            "Nie używaj słowa 'Biblia' – skup się wyłącznie na samym temacie."
        ))
        query_filters: QdrantFilter = Field(
            default_factory=QdrantFilter,
            description=(
                "Filtry Qdrant – używaj WYŁĄCZNIE gdy użytkownik wprost wskazuje konkretną część lub "
                f"księgę Biblii. Dostępne pola i ich wartości: {metadata_json}. "
                "Jeśli filtrowanie nie jest potrzebne, pozostaw wszystkie listy puste."
            ),
        )
        top_k: int = Field(
            ge=top_k_specific,
            le=top_k_popular,
            description=(
                "Liczba wersetów do pobrania. Dobierz na podstawie popularności tematu: "
                f"temat popularny (wiele pasujących fragmentów): {top_k_popular}, "
                f"temat standardowy: {top_k_standard}, "
                f"temat bardzo specyficzny (jedno konkretne miejsce w Biblii): {top_k_specific}."
            ),
        )
        reasoning: str = Field(description="Krótkie uzasadnienie wyborów query_text, query_filters i top_k.")

    class RetrievalRequests(BaseModel):
        requests: list[RetrievalRequest] = Field(description=(
            "Lista 2-3 zapytań do retrievera pokrywających różne aspekty pytania użytkownika. "
            "Każde zapytanie musi dotyczyć innego aspektu – nie duplikuj tematu między requestami. "
            "Jeśli pytanie jest proste i specyficzne, jedno zapytanie wystarczy."
        ))

    return RetrievalRequests


# ── Verse relevance filtering ─────────────────────────────────────────────────

class VerseRelevance(BaseModel):
    is_relevant: bool = Field(description=(
        "True jeśli fragment Biblii bezpośrednio lub pośrednio dotyczy pytania użytkownika "
        "i może stanowić wartościowy element odpowiedzi na to pytanie."
    ))
    reasoning: str = Field(description="Krótkie uzasadnienie decyzji o trafności lub braku trafności fragmentu.")


# ── Verse grouping ────────────────────────────────────────────────────────────

class CategoryEntry(BaseModel):
    category_name: str = Field(description="Nazwa obszaru tematycznego – pasuje jako nagłówek sekcji odpowiedzi.")
    verse_ids: list[int] = Field(description="Lista id wersetów należących do tego obszaru tematycznego.")


class GroupedVerses(BaseModel):
    categories: list[CategoryEntry] = Field(description=(
        "Lista obszarów tematycznych. Obszary muszą być odrębne i niezależne tematycznie. "
        "Każde id wersetu musi wystąpić w co najmniej jednej kategorii. "
        "Jeśli werset pasuje do kilku tematów, możesz umieścić go w wielu kategoriach."
    ))


# ── Answer generation ─────────────────────────────────────────────────────────

class BibleCitation(BaseModel):
    book_name: str = Field(description="Pełna nazwa księgi Biblii – użyj dokładnie takiej nazwy jak w kontekście.")
    chapter_number: int = Field(description="Numer rozdziału cytowanego fragmentu.")
    verse_number: int = Field(description="Numer wersetu cytowanego fragmentu.")


class ResponseParagraph(BaseModel):
    response_paragraph_text: str = Field(
        description="Tekst akapitu odpowiedzi dotyczący jednego konkretnego zagadnienia."
    )
    response_paragraph_citations: list[BibleCitation] = Field(description=(
        "Lista cytowań biblijnych użytych w tym akapicie. "
        "Cytuj wyłącznie wersety wprost wymienione w kontekście."
    ))


class AspectResponse(BaseModel):
    aspect_name: str = Field(description="Nazwa aspektu, którego dotyczy odpowiedź.")
    paragraphs: list[ResponseParagraph] = Field(description=(
        "Lista akapitów poruszających różne zagadnienia z kontekstu. "
        "Razem powinny tworzyć spójną, ciągłą narrację w ramach danego aspektu."
    ))

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine


_nlp_provider = NlpEngineProvider(nlp_configuration={
    "nlp_engine_name": "spacy",
    "models": [
        {"lang_code": "en", "model_name": "en_core_web_lg"},
        {"lang_code": "pt", "model_name": "pt_core_news_lg"},
    ],
})

_analyzer = AnalyzerEngine(
    nlp_engine=_nlp_provider.create_engine(),
    supported_languages=["en", "pt"]
)

_anonymizer = AnonymizerEngine()

def censor(text: str, language: str) -> str:
    results = _analyzer.analyze(
        text=text,
        language=language,
        entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD", "IBAN_CODE", "US_SSN", "US_BANK_NUMBER"],
    )
    return _anonymizer.anonymize(text=text, analyzer_results=results).text
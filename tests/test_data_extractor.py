from f1p.services.data_extractor import DataExtractorService, SessionIdentifiers


def test_data_extractor():
    extractor_service = DataExtractorService(2025, 16, SessionIdentifiers.RACE)
    extractor_service.extract()

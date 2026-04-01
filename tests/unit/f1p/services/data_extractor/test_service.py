from pathlib import Path
from unittest.mock import MagicMock

from pytest_mock import MockerFixture

from f1p.services.data_extractor.service import DataExtractorService


def test_init(
    mock_parent: MagicMock,
    mock_task_manager: MagicMock,
    mock_text_font: MagicMock,
    mocker: MockerFixture,
) -> None:
    mock_accept = mocker.MagicMock()
    mock_enable_cache = mocker.MagicMock()
    mocker.patch.object(DataExtractorService, "accept", mock_accept)
    mocker.patch("f1p.services.data_extractor.service.fastf1.Cache.enable_cache", mock_enable_cache)
    mocker.patch.object(Path, "exists", return_value=True)

    service = DataExtractorService(
        parent=mock_parent,
        task_manager=mock_task_manager,
        window_width=1920,
        window_height=1080,
        text_font=mock_text_font,
    )

    assert service.parent == mock_parent
    assert service.task_manager == mock_task_manager
    assert service.window_width == 1920
    assert service.window_height == 1080
    assert service.text_font == mock_text_font

    assert service._session_results is None
    assert service._car_data is None

    mock_accept.assert_called_once_with("loadData", service.load_data)
    mock_enable_cache.assert_called_once()


def test_init_and_create_cache_dir(
    mock_parent: MagicMock,
    mock_task_manager: MagicMock,
    mock_text_font: MagicMock,
    mocker: MockerFixture,
) -> None:
    mock_accept = mocker.MagicMock()
    mock_enable_cache = mocker.MagicMock()
    mocker.patch.object(DataExtractorService, "accept", mock_accept)
    mocker.patch("f1p.services.data_extractor.service.fastf1.Cache.enable_cache", mock_enable_cache)
    mocker.patch.object(Path, "exists", return_value=True)

    mock_path = mocker.MagicMock(spec=Path)
    mock_path.exists.return_value = False
    DataExtractorService.cache_path = mock_path

    service = DataExtractorService(
        parent=mock_parent,
        task_manager=mock_task_manager,
        window_width=1920,
        window_height=1080,
        text_font=mock_text_font,
    )

    assert service.parent == mock_parent
    assert service.task_manager == mock_task_manager
    assert service.window_width == 1920
    assert service.window_height == 1080
    assert service.text_font == mock_text_font

    assert service._session_results is None
    assert service._car_data is None

    mock_accept.assert_called_once_with("loadData", service.load_data)
    mock_enable_cache.assert_called_once()

    mock_path.exists.assert_called_once()
    mock_path.mkdir.assert_called_once_with(parents=True)

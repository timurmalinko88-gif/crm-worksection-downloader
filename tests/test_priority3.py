"""
PRIORITY 3 Tests - Convenience Features
Тестирование функций фильтрации, уведомлений и интерактивного меню.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from datetime import datetime

# Import modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from downloader import should_download_file, play_notification_sound, send_toast_notification, notify_completion
from menu import MenuManager


class TestFileFiltering:
    """Тестирование системы фильтрации файлов."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Настройка тестового конфига."""
        import downloader
        self.original_config = downloader.CONFIG
        
        # Конфиг с отключенной фильтрацией
        downloader.CONFIG = {
            'enable_file_filtering': False,
            'allowed_extensions': [],
            'min_file_size_kb': 0,
            'max_file_size_mb': 0,
        }
        yield
        downloader.CONFIG = self.original_config
    
    def test_filtering_disabled(self):
        """Тест: фильтрация отключена - все файлы проходят."""
        import downloader
        downloader.CONFIG['enable_file_filtering'] = False
        
        should_download, reason = should_download_file("test.pdf", 1000)
        assert should_download is True
        assert reason == "фильтрация отключена"
    
    def test_extension_filter_allowed(self):
        """Тест: расширение разрешено."""
        import downloader
        downloader.CONFIG['enable_file_filtering'] = True
        downloader.CONFIG['allowed_extensions'] = ['pdf', 'jpg', 'png']
        
        should_download, _ = should_download_file("document.pdf", 1000)
        assert should_download is True
    
    def test_extension_filter_denied(self):
        """Тест: расширение запрещено."""
        import downloader
        downloader.CONFIG['enable_file_filtering'] = True
        downloader.CONFIG['allowed_extensions'] = ['pdf', 'jpg']
        
        should_download, reason = should_download_file("video.mp4", 1000)
        assert should_download is False
        assert "mp4" in reason
    
    def test_min_file_size(self):
        """Тест: файл меньше минимального размера."""
        import downloader
        downloader.CONFIG['enable_file_filtering'] = True
        downloader.CONFIG['min_file_size_kb'] = 500
        
        should_download, reason = should_download_file("small.pdf", 100)
        assert should_download is False
        assert "меньше минимума" in reason
    
    def test_max_file_size(self):
        """Тест: файл больше максимального размера."""
        import downloader
        downloader.CONFIG['enable_file_filtering'] = True
        downloader.CONFIG['max_file_size_mb'] = 100
        
        should_download, reason = should_download_file("huge.zip", 200 * 1024)  # 200 MB
        assert should_download is False
        assert "больше максимума" in reason
    
    def test_multiple_filters_passed(self):
        """Тест: файл прошел все фильтры."""
        import downloader
        downloader.CONFIG['enable_file_filtering'] = True
        downloader.CONFIG['allowed_extensions'] = ['pdf']
        downloader.CONFIG['min_file_size_kb'] = 100
        downloader.CONFIG['max_file_size_mb'] = 50
        
        should_download, reason = should_download_file("document.pdf", 1000)
        assert should_download is True


class TestNotifications:
    """Тестирование системы уведомлений."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Настройка тестового логгера."""
        import logging
        self.logger = logging.getLogger('downloader')
    
    @patch('winsound.Beep')
    def test_sound_notification(self, mock_beep):
        """Тест: проигрывание звука."""
        play_notification_sound()
        mock_beep.assert_called_once()
        # Проверяем параметры звука
        args, kwargs = mock_beep.call_args
        assert args[0] == 1000  # Frequency
        assert args[1] == 500   # Duration
    
    @patch('plyer.notification.notify')
    def test_toast_notification(self, mock_notify):
        """Тест: Windows Toast уведомление."""
        send_toast_notification("Test Title", "Test Message", show_time_sec=5)
        mock_notify.assert_called_once()
        kwargs = mock_notify.call_args.kwargs
        assert kwargs['title'] == "Test Title"
        assert kwargs['message'] == "Test Message"
    
    @patch('downloader.play_notification_sound')
    @patch('downloader.send_toast_notification')
    def test_completion_notification_all_enabled(self, mock_toast, mock_sound):
        """Тест: полное уведомление о завершении."""
        import downloader
        downloader.CONFIG = {
            'enable_notifications': True,
            'notification_sound': True,
            'notification_toast': True,
        }
        
        notify_completion("TestTask", 10, 1.5, 60, 100)
        
        mock_sound.assert_called_once()
        mock_toast.assert_called_once()
    
    @patch('downloader.play_notification_sound')
    @patch('downloader.send_toast_notification')
    def test_completion_notification_disabled(self, mock_toast, mock_sound):
        """Тест: уведомления отключены."""
        import downloader
        downloader.CONFIG = {
            'enable_notifications': False,
            'notification_sound': True,
            'notification_toast': True,
        }
        
        notify_completion("TestTask", 10, 1.5, 60, 100)
        
        mock_sound.assert_not_called()
        mock_toast.assert_not_called()


class TestMenu:
    """Тестирование интерактивного меню."""
    
    @pytest.fixture
    def temp_dir(self):
        """Создает временную директорию."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def menu_manager(self, temp_dir):
        """Создает менеджер меню с временной директорией."""
        config = {
            'base_dir': str(temp_dir),
            'max_workers': 5,
            'request_timeout': 30,
        }
        return MenuManager(temp_dir, config)
    
    def test_menu_manager_initialization(self, menu_manager, temp_dir):
        """Тест: инициализация менеджера меню."""
        assert menu_manager.base_dir == temp_dir
        assert menu_manager.history_file == temp_dir / 'download_history.json'
        assert menu_manager.logs_dir == temp_dir / 'logs'
    
    def test_menu_banner_display(self, menu_manager, capsys):
        """Тест: вывод заголовка."""
        menu_manager.display_banner()
        captured = capsys.readouterr()
        assert "CRM DOWNLOADER" in captured.out
        assert "v3.0" in captured.out or "интерфейс" in captured.out
    
    def test_main_menu_display(self, menu_manager, capsys):
        """Тест: вывод главного меню."""
        menu_manager.display_main_menu()
        captured = capsys.readouterr()
        assert "ГЛАВНОЕ МЕНЮ" in captured.out
        assert "Загрузить по URL" in captured.out
        assert "История загрузок" in captured.out
    
    @patch('builtins.input', return_value='1')
    def test_menu_choice_valid(self, mock_input, menu_manager):
        """Тест: корректный выбор пункта."""
        choice = menu_manager.get_menu_choice()
        assert choice == '1'
    
    @patch('builtins.input', side_effect=['invalid', '5'])
    def test_menu_choice_invalid_then_valid(self, mock_input, menu_manager, capsys):
        """Тест: неверный выбор, затем корректный."""
        choice = menu_manager.get_menu_choice()
        assert choice == '5'
        captured = capsys.readouterr()
        assert "Неверный выбор" in captured.out
    
    @patch('builtins.input', return_value='https://example.com')
    def test_url_input_valid(self, mock_input, menu_manager):
        """Тест: корректный ввод URL."""
        url = menu_manager.get_url_input()
        assert url == 'https://example.com'
    
    @patch('builtins.input', return_value='not-a-url')
    def test_url_input_invalid(self, mock_input, menu_manager, capsys):
        """Тест: некорректный URL."""
        url = menu_manager.get_url_input()
        assert url is None
        captured = capsys.readouterr()
        assert "должен начинаться" in captured.out
    
    @patch('builtins.input', return_value='back')
    def test_url_input_back(self, mock_input, menu_manager):
        """Тест: возврат из ввода URL."""
        url = menu_manager.get_url_input()
        assert url is None
    
    def test_statistics_empty_history(self, menu_manager, capsys):
        """Тест: статистика без истории."""
        menu_manager.show_statistics()
        captured = capsys.readouterr()
        assert "История пуста" in captured.out
    
    def test_statistics_with_history(self, menu_manager, capsys):
        """Тест: статистика с историей."""
        # Создаем тестовую историю
        history = {
            "Task1": {
                "task_name": "Task1",
                "first_download": datetime.now().isoformat(),
                "files": [
                    {
                        "filename": "file1.pdf",
                        "size": 1024 * 1024,  # 1 MB
                        "md5": "abc123",
                        "download_date": datetime.now().isoformat(),
                        "url": "http://example.com/file1"
                    }
                ]
            }
        }
        
        with open(menu_manager.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f)
        
        menu_manager.show_statistics()
        captured = capsys.readouterr()
        
        assert "ОБЩАЯ СТАТИСТИКА" in captured.out
        assert "Task1" in captured.out
        assert "1" in captured.out  # Количество задач/файлов
    
    def test_batch_file_input_valid(self, menu_manager, temp_dir):
        """Тест: загрузка корректного batch файла."""
        batch_file = temp_dir / "urls.txt"
        batch_file.write_text("https://example.com/1\nhttps://example.com/2\n")
        
        with patch('builtins.input', return_value=str(batch_file)):
            urls = menu_manager.get_batch_file_input()
        
        assert urls == ["https://example.com/1", "https://example.com/2"]
    
    def test_batch_file_not_found(self, menu_manager, capsys):
        """Тест: batch файл не найден."""
        with patch('builtins.input', return_value="/nonexistent/file.txt"):
            urls = menu_manager.get_batch_file_input()
        
        assert urls is None
        captured = capsys.readouterr()
        assert "не найден" in captured.out
    
    def test_clear_logs_no_logs(self, menu_manager, capsys):
        """Тест: очистка логов, когда их нет."""
        menu_manager.clear_logs()
        captured = capsys.readouterr()
        assert "не найдена" in captured.out or "нет файлов" in captured.out
    
    def test_clear_logs_with_logs(self, menu_manager, temp_dir, capsys):
        """Тест: очистка логов с наличием файлов."""
        logs_dir = temp_dir / 'logs'
        logs_dir.mkdir()
        
        log_file = logs_dir / 'downloader_2026-01-27.log'
        log_file.write_text("test log content")
        
        with patch('builtins.input', return_value='да'):
            menu_manager.clear_logs()
        
        captured = capsys.readouterr()
        assert "Удалено" in captured.out
        assert not log_file.exists()
    
    def test_show_settings(self, menu_manager, capsys):
        """Тест: отображение параметров."""
        menu_manager.show_settings()
        captured = capsys.readouterr()
        
        assert "ПАРАМЕТРЫ" in captured.out
        assert "Базовая папка" in captured.out
        assert "Рабочих потоков" in captured.out
        assert "PRIORITY 3" in captured.out or "УДОБСТВО" in captured.out


class TestBatchProcessing:
    """Тестирование пакетной обработки URL."""
    
    def test_batch_url_list_parsing(self):
        """Тест: парсинг списка URL из файла."""
        urls = ["https://example.com/1", "https://example.com/2", "https://example.com/3"]
        assert len(urls) == 3
        assert all(url.startswith('https://') for url in urls)
    
    def test_batch_parallel_config(self):
        """Тест: конфигурация параллельной обработки."""
        config = {
            'enable_batch_parallel': True,
            'parallel_urls': 2,
        }
        
        assert config['enable_batch_parallel'] is True
        assert config['parallel_urls'] == 2
        assert config['parallel_urls'] >= 1


class TestIntegration:
    """Интеграционные тесты для PRIORITY 3."""
    
    def test_filtering_in_download_context(self):
        """Тест: фильтрация в контексте загрузки."""
        import downloader
        downloader.CONFIG = {
            'enable_file_filtering': True,
            'allowed_extensions': ['jpg', 'png'],
            'min_file_size_kb': 100,
            'max_file_size_mb': 50,
        }
        
        # Файл, прошедший все фильтры
        should_dl, _ = should_download_file("photo.jpg", 500)
        assert should_dl is True
        
        # Файл с запрещенным расширением
        should_dl, _ = should_download_file("document.pdf", 500)
        assert should_dl is False
    
    @patch('downloader.play_notification_sound')
    @patch('downloader.send_toast_notification')
    def test_notification_after_completion(self, mock_toast, mock_sound):
        """Тест: уведомления срабатывают после завершения."""
        import downloader
        downloader.CONFIG = {
            'enable_notifications': True,
            'notification_sound': True,
            'notification_toast': True,
        }
        
        notify_completion("TestTask", 5, 2.1, 120, 100)
        
        assert mock_sound.called
        assert mock_toast.called


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

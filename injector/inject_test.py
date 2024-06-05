import unittest
from unittest.mock import patch, mock_open, MagicMock
import logging
import json

# Assuming process_json_file is imported from inject module
from inject import process_json_file

class TestProcessJsonFile(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data='{"actor": {"login": "user1"}, "repo": {"name": "repo1"}}\n{"actor": {"login": "user2"}, "repo": {"name": "repo2"}}')
    @patch('inject.insert_event_if_not_exist')
    @patch('inject.filter_event')
    def test_process_json_file(self, mock_filter_event, mock_insert_event, mock_open):
        # Mock database connection
        mock_conn = MagicMock()
        
        # Set the behavior of filter_event
        mock_filter_event.side_effect = [True, False]
        
        # Call the function
        result = process_json_file('dummy_path.json', mock_conn)
        
        # Verify the function returns True
        self.assertTrue(result)
        
        # Ensure the file was read
        mock_open.assert_called_once_with('dummy_path.json', 'r')
        
        # Check if insert_event_if_not_exist was called once
        self.assertEqual(mock_insert_event.call_count, 1)
        
        # Verify filter_event was called twice, once for each event
        self.assertEqual(mock_filter_event.call_count, 2)
        
        # Ensure insert_event_if_not_exist was called with the correct parameters
        expected_event = {"actor": {"login": "user1"}, "repo": {"name": "repo1"}}
        mock_insert_event.assert_called_once_with(mock_conn, expected_event)
        
    @patch('builtins.open', new_callable=mock_open, read_data='')
    def test_process_empty_file(self, mock_open):
        # Mock database connection
        mock_conn = MagicMock()
        
        # Call the function
        result = process_json_file('dummy_path.json', mock_conn)
        
        # Verify the function returns False
        self.assertFalse(result)
        
        # Ensure the file was read
        mock_open.assert_called_once_with('dummy_path.json', 'r')
        
    @patch('builtins.open', new_callable=mock_open)
    @patch('logging.warning')
    def test_process_json_file_with_empty_lines(self, mock_warning, mock_open):
        # Mock database connection
        mock_conn = MagicMock()
        
        # Mock file with empty lines
        mock_open.return_value.readlines.return_value = []
        
        # Call the function
        result = process_json_file('dummy_path.json', mock_conn)
        
        # Verify the function returns False
        self.assertFalse(result)
        
        # Ensure the file was read
        mock_open.assert_called_once_with('dummy_path.json', 'r')
        
        # Ensure a warning was logged
        mock_warning.assert_called_once_with("Empty file..skipping..: dummy_path.json")
    
    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    @patch('logging.error')
    def test_process_json_file_with_invalid_json(self, mock_error, mock_open):
        # Mock database connection
        mock_conn = MagicMock()
        
        # Call the function
        result = process_json_file('dummy_path.json', mock_conn)
        
        # Verify the function returns False
        self.assertFalse(result)
        
        # Ensure the file was read
        mock_open.assert_called_once_with('dummy_path.json', 'r')
        
        # Ensure an error was logged
        mock_error.assert_called_once()

    @patch('builtins.open', new_callable=mock_open, read_data='{"actor": {"login": "user1"}, "repo": {"name": "repo1"}}\n')
    @patch('inject.insert_event_if_not_exist')
    @patch('inject.filter_event')
    @patch('logging.error')
    def test_process_json_file_with_unexpected_error(self, mock_error, mock_filter_event, mock_insert_event, mock_open):
        # Mock database connection
        mock_conn = MagicMock()
        
        # Simulate an unexpected error in insert_event_if_not_exist
        mock_insert_event.side_effect = Exception('Unexpected error')
        
        # Set the behavior of filter_event
        mock_filter_event.return_value = True
        
        # Call the function
        result = process_json_file('dummy_path.json', mock_conn)
        
        # Verify the function returns False
        self.assertFalse(result)
        
        # Ensure the file was read
        mock_open.assert_called_once_with('dummy_path.json', 'r')
        
        # Ensure an error was logged
        mock_error.assert_called_once_with('Unexpected error processing file dummy_path.json: Unexpected error')
        
if __name__ == '__main__':
    unittest.main()
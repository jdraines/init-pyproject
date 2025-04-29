from unittest.mock import patch

from ${project_name}.main import main

@patch("{project_name}.main.say_hello")
def test_main(mock_say_hello):
    main()
    mock_say_hello.assert_called_once()


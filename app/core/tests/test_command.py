from django.test import SimpleTestCase
from unittest.mock import patch, Mock
from psycopg2 import OperationalError as psycopg2OperationalError
from django.db.utils import OperationalError
from django.core.management import call_command


@patch('core.management.commands.waitfordb.Command.check')
class TestWaitForDB(SimpleTestCase):

    def test_wait_for_db_ready(self, command_check):
        command_check.return_value = True

        call_command('waitfordb')

        command_check.assert_called_once_with(database=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, time_sleep, command_check):
        command_check.return_value = \
        [psycopg2OperationalError] * 13 + [OperationalError] * 6 + [True]


        call_command('waitfordb')

        self.assertEqual(command_check.called_count, 20)

        command_check.assert_called_with(database=['default'])

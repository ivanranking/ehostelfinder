import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehostelfinder.settings')
import django
django.setup()
from django.test.utils import get_runner
from django.conf import settings
TestRunner = get_runner(settings)
test_runner = TestRunner(verbosity=2)
failures = test_runner.run_tests(['hostels.tests'])
print('FAILURES', failures)
sys.exit(bool(failures))

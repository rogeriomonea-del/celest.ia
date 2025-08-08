import os, pytest

selenium_available = os.path.exists('/usr/bin/chromium') or os.getenv('CI')

pytestmark = pytest.mark.skipif(not selenium_available, reason="Selenium/Chromium not available in this env")

"""Tests of comprehensive theming."""

from functools import wraps

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings

import edxmako
from lms.startup import comprehensive_theme_changes


def with_comp_theme(theme_dir):
    """
    A decorator to run a test with a particular comprehensive theme.

    Arguments:
        theme_dir (str): the full path to the theme directory to use.
            This will likely use `settings.REPO_ROOT` to get the full path.

    """
    changes = comprehensive_theme_changes(theme_dir)

    def _decorator(func):       # pylint: disable=missing-docstring
        @wraps(func)
        def _decorated(*args, **kwargs):
            with override_settings(COMP_THEME_DIR=theme_dir, **changes['settings']):
                with edxmako.save_lookups():
                    for template_dir in changes['mako_paths']:
                        edxmako.paths.add_lookup('main', template_dir, prepend=True)

                    return func(*args, **kwargs)
        return _decorated
    return _decorator


class TestComprehensiveTheming(TestCase):
    """Test comprehensive theming."""

    @with_comp_theme(settings.REPO_ROOT / 'themes/red-theme')
    def test_red_footer(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

        import os, os.path
        for namespace, lookup in edxmako.LOOKUP.items():
            print "--- %s: %s" % (namespace, lookup.template_args['module_directory'])
            for directory in lookup.directories:
                print "  %s" % (directory,)

        print "="*80
        theme_dir = settings.REPO_ROOT / "themes/red-theme/lms/templates"
        for file in os.listdir(theme_dir):
            theme_file = os.path.join(theme_dir, file)
            with open(theme_file) as f:
                bytes = len(f.read())
            print "    %s: %d" % (theme_file, bytes)

        print "="*80
        for dir, dirs, files in os.walk(settings.MAKO_MODULE_DIR):
            print "%s ----------------" % (dir,)
            for file in sorted(files):
                with open(os.path.join(dir, file)) as f:
                    bytes = len(f.read())
                print "    %s: %d" % (file, bytes)
        self.assertContains(resp, "super-ugly")

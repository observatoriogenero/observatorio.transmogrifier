# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from observatorio.transmogrifier.testing import IntegrationTestCase
from plone import api


class TestInstall(IntegrationTestCase):
    """Test installation of observatorio.transmogrifier into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if observatorio.transmogrifier is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('observatorio.transmogrifier'))

    def test_uninstall(self):
        """Test if observatorio.transmogrifier is cleanly uninstalled."""
        self.installer.uninstallProducts(['observatorio.transmogrifier'])
        self.assertFalse(self.installer.isProductInstalled('observatorio.transmogrifier'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that IObservatorioTransmogrifierLayer is registered."""
        from observatorio.transmogrifier.interfaces import IObservatorioTransmogrifierLayer
        from plone.browserlayer import utils
        self.failUnless(IObservatorioTransmogrifierLayer in utils.registered_layers())

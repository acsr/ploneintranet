from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite
from zope.i18nmessageid import MessageFactory

from logging import getLogger

logger = getLogger(__name__)
DocconvMessageFactory = MessageFactory('ploneintranet')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""


def is_autoconv_enabled():
    site = getSite()
    portal_properties = getToolByName(site, 'portal_properties')
    site_properties = portal_properties.site_properties
    return site_properties.getProperty('docconv_autoconv', False)

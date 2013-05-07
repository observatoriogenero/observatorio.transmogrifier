# -*- coding: utf-8 -*-
# Rode o script com o comando: ./bin/instance run NOMEDOSCRIPT.py
#

from StringIO import StringIO
from Products.Archetypes.Storage import AttributeStorage
import transaction
from Testing.makerequest import makerequest
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy
from Products.CMFCore.tests.base.security import PermissiveSecurityPolicy
from Products.CMFCore.tests.base.security import OmnipotentUser
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import setSite
from Acquisition import aq_base
from datetime import datetime
from AccessControl.SecurityManagement import noSecurityManager


attr_storage = AttributeStorage()
ploneid = 'intrateste'

app = makerequest(app)

_policy = PermissiveSecurityPolicy()
_oldpolicy = setSecurityPolicy(_policy)
newSecurityManager(None, OmnipotentUser().__of__(app.acl_users))

portal = app[ploneid]
setSite(portal)

print 'Iniciado as ',
print datetime.now().isoformat()

ct = getToolByName(portal, 'portal_catalog')
contents = ct.searchResults({'path':'/intrateste/migracao'})

for content in contents:
    print 'Alterando Creator: %s em %s ... ' %(content.id, content.getPath()),
    obj = portal.restrictedTraverse(content.getPath())
    try:
        owner = obj.getOwner(info=1)[1:]
    except AttributeError:
        owner = obj.Creator()
    obj.setCreators(owner) 
    
    print 'OK'
    print ''

    print 'Commit da transacao e sinconismo do Data.fs'
    print ''

    transaction.commit()
    app._p_jar.sync()


noSecurityManager()

# Liberando memória.
transaction.savepoint(1)
transaction.commit()
app._p_jar.sync()

print 'Finalizado as ',
print datetime.now().isoformat()
print ''

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
ploneid = 'essintra'
pt = ('File',)

app = makerequest(app)

_policy = PermissiveSecurityPolicy()
_oldpolicy = setSecurityPolicy(_policy)
newSecurityManager(None, OmnipotentUser().__of__(app.acl_users))

portal = app[ploneid]
setSite(portal)

print 'Iniciado as ',
print datetime.now().isoformat()

ct = getToolByName(portal, 'portal_catalog')
arquivos = ct.searchResults({'portal_type':pt})

for arq in arquivos:
    print 'Populando: %s em %s ... ' %(arq.id, arq.getPath()),
    obj = portal.restrictedTraverse(arq.getPath())

    f_tp = 'file'
    field = obj.Schema()[f_tp]

    try:
        mimetype = field.getContentType(obj)
    except:
        mimetype = obj.getContentType()

    fieldValue = field.getStorage(obj).get(field.getName(), obj)
    content = StringIO(str(fieldValue))

    # Remove acquisition wrappers
    fieldValue = str(aq_base( fieldValue ))

    if field.getFilename(obj) == 'file' or field.getFilename(obj) == '' or field.getFilename(obj) == None:
       newname = str(obj.id)
    else:
       newname = field.getFilename(obj)

    attr_storage.unset('file',obj)
    field.set(obj, content)
    field.setContentType(obj, mimetype)
    obj.getBlobWrapper().setFilename(newname)

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

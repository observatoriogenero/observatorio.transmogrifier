
import os
import shutil
import simplejson
from datetime import datetime
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName

COUNTER = 1

HOMEDIR = '/home/observatorio/exported_data'

CLASSNAME_TO_SKIP_LAUD = ['ControllerPythonScript',
    'ControllerPageTemplate', 'ControllerValidator', 'PythonScript', 'SQL', 'Connection',
    'ZetadbScript', 'ExternalMethod', 'ZetadbSqlInsert', 'ZetadbMysqlda', 'SiteRoot',
    'ZetadbApplication', 'ZetadbZptInsert', 'I18NLayer', 'ZetadbZptView', 'BrowserIdManager',
    'ZetadbScriptSelectMaster', 'ZetadbSqlSelect', ]

CLASSNAME_TO_SKIP = ['SetupTool', 'SecureMailHost', 'ContentTypeRegistry', 'SiteErrorLog',
    'PloneTool', 'ActionIconsTool', 'ActionsTool', 'ATCTTool', 'CalendarTool',
    'CatalogTool', 'PloneControlPanel', 'CSSRegistryTool', 'CMFDiffTool',
    'DiscussionTool', 'FactoryTool', 'GroupDataTool', 'GroupsTool', 'InterfaceTool',
    'JSRegistryTool', 'KSSRegistryTool', 'MemberDataTool', 'MembershipTool',
    'MetadataTool', 'MigrationTool', 'PasswordResetTool', 'PropertiesTool',
    'QuickInstallerTool', 'RegistrationTool', 'SkinsTool', 'SyndicationTool',
    'TypesTool', 'UniqueIdAnnotationTool', 'UniqueIdGeneratorTool', 'UndoTool',
    'URLTool', 'ViewTemplateContainer', 'WorkflowTool', 'TranslationServiceTool',
    'FormController', 'MimeTypesRegistry', 'TransformTool', 'ArchetypeTool',
    'ReferenceCatalog', 'UIDCatalog', 'PluggableAuthService', 'PloneKupuLibraryTool',
    'ArchivistTool', 'ZVCStorageTool', 'UniqueIdHandlerTool', 'ModifierRegistryTool',
    'KeepLastNVersionsTool', 'ReferenceFactoriesTool', 'CopyModifyMergeRepositoryTool',
    'UniqueIdHandlerTool', 'LanguageTool', 'RAMCacheManager', 'RAMCacheManager',
    'ContentPanelsTool', 'RAMCacheManager', 'PlacefulWorkflowTool', 'ChecklistTool',
    'ContractTool', 'CronTool','CatalogServiceDesk','TinyMCE','RedirectionTool',
    'SquidTool', 'JobPerformanceTool', 'CacheTool', 'WorkflowPolicyConfig',
    'MessageTool', 'PloneboardTool', 'Analytics', 'PageCacheManager','CSCachingPolicyManager',
    'PolicyHTTPCacheManager', 'PolicyHTTPCacheManager', 'RAMCacheManager','PersonalData',
    'SchemaEditorTool', 'ATSETemplateTool', 'AreaTematica', 'Banners', 'EixoAtuacao',
    'FolderSignupSheets', 'FolderTipoListas', 'HeaderSetFolder', 'MacroFolder', 'Newsletter',
    'NewsletterBTree', 'NewsletterReference', 'NewsletterRichReference', 'NewsletterTheme',
    'SERPROSCEquidadeGenerosTool', 'PublicatorTool', 'FolderBanners', 'SyndicationInformation']
    
ID_TO_SKIP = ['Members', ]


def export_plone_observatorio(self):

    global COUNTER
    global TMPDIR
    global ID_TO_SKIP

    COUNTER = 1
    TODAY = datetime.today()
    TMPDIR = HOMEDIR+'/content_'+self.getId()+'_'+TODAY.strftime('%Y-%m-%d-%H-%M-%S')

    id_to_skip = self.REQUEST.get('id_to_skip', None)
    if id_to_skip is not None:
        ID_TO_SKIP += id_to_skip.split(',')

    if os.path.isdir(TMPDIR):
        shutil.rmtree(TMPDIR)
    else:
        os.mkdir(TMPDIR)

    write(walk(self))

    # TODO: we should return something more useful
    return 'SUCCESS :: '+self.absolute_url()+'\n'


def walk(folder):
    for item_id in folder.objectIds():
        item = folder[item_id]
        if item.__class__.__name__ in CLASSNAME_TO_SKIP or \
           item.getId() in ID_TO_SKIP:
            continue
        if item.__class__.__name__ in CLASSNAME_TO_SKIP_LAUD:
            print '>> SKIPPING :: ['+item.__class__.__name__+'] '+item.absolute_url()
            continue
        yield item
        if getattr(item, 'objectIds', None) and \
           item.objectIds():
            for subitem in walk(item):
                yield subitem


def write(items):
    global COUNTER

    for item in items:
        if item.__class__.__name__ not in CLASSNAME_TO_WAPPER_MAP.keys() and item.__class__.__name__ != 'ATBlob':
            #import pdb;pdb.set_trace()
            raise Exception, 'No wrapper defined for "'+item.__class__.__name__+ \
                                                  '" ('+item.absolute_url()+').'
        try:
            if item.__class__.__name__ == 'ATBlob':
                if item.portal_type == 'Image':
                    dictionary = CLASSNAME_TO_WAPPER_MAP['ATImage'](item)
                if item.portal_type == 'Arquivo':
                    dictionary = CLASSNAME_TO_WAPPER_MAP['Arquivo'](item)
            else:
                dictionary = CLASSNAME_TO_WAPPER_MAP[item.__class__.__name__](item)
            write_to_jsonfile(dictionary)
            COUNTER += 1
        except:
            import pdb; pdb.set_trace()


def write_to_jsonfile(item):
    global COUNTER

    SUB_TMPDIR = os.path.join(TMPDIR, str(COUNTER/1000)) # 1000 files per folder, so we dont reach some fs limit
    if not os.path.isdir(SUB_TMPDIR):
        os.mkdir(SUB_TMPDIR)

    # we store data fields in separate files
    datafield_counter = 1
    if '__datafields__' in item.keys():
        for datafield in item['__datafields__']:
            datafield_filepath = os.path.join(SUB_TMPDIR, str(COUNTER)+'.json-file-'+str(datafield_counter))
            f = open(datafield_filepath, 'wb')
            f.write(item[datafield])
            item[datafield] = os.path.join(str(COUNTER/1000), str(COUNTER)+'.json-file-'+str(datafield_counter))
            f.close()
            datafield_counter += 1
        item.pop(u'__datafields__')

    f = open(os.path.join(SUB_TMPDIR, str(COUNTER)+'.json'), 'wb')
    simplejson.dump(item, f, indent=4)
    f.close()


def getPermissionMapping(acperm):
    result = {}
    for entry in acperm:
        result[entry[0]] = entry[1]
    return result


class BaseWrapper(dict):
    """Wraps the dublin core metadata and pass it as tranmogrifier friendly style
    """

    def __init__(self, obj):
        self.obj = obj

        self.portal = getToolByName(obj, 'portal_url').getPortalObject()
        self.portal_utils = getToolByName(obj, 'plone_utils')
        self.charset = self.portal.portal_properties.site_properties.default_charset

        if not self.charset: # newer seen it missing ... but users can change it
            self.charset = 'utf-8'

        self['__datafields__'] = []
        self['_path'] = '/'.join(self.obj.getPhysicalPath())

        self['_type'] = self.obj.__class__.__name__

        self['id'] = obj.getId()
        self['_uid'] = obj.UID()
        self['title'] = obj.title.decode(self.charset, 'ignore')
        self['description'] = obj.description.decode(self.charset, 'ignore')
        self['language'] = obj.language
        self['rights'] = obj.rights.decode(self.charset, 'ignore')
        # for DC attrs that are tuples
        for attr in ('subject', 'contributors'):
            self[attr] = []
            val_tuple = getattr(obj, attr, False)
            if val_tuple:
                for val in val_tuple:
                    self[attr].append(val.decode(self.charset, 'ignore'))
                self[attr] = tuple(self[attr])
        # for DC attrs that are DateTimes
        datetimes_dict = {'creation_date': 'creation_date',
                          'modification_date': 'modification_date',
                          'expiration_date': 'expirationDate',
                          'effective_date': 'effectiveDate'}
        for old_name, new_name in datetimes_dict.items():
            val = getattr(obj, old_name, False)
            if val:
                self[new_name] = str(val)

        # workflow history
        if hasattr(obj, 'workflow_history'):
            workflow_history = obj.workflow_history.data
            try:
                for w in workflow_history:
                    for i, w2 in enumerate(workflow_history[w]):
                        workflow_history[w][i]['time'] = str(workflow_history[w][i]['time'])
                        workflow_history[w][i]['comments'] = workflow_history[w][i]['comments'].decode(self.charset, 'ignore')
            except:
                import pdb; pdb.set_trace()
            self['_workflow_history'] = workflow_history

        # default view
        
        try:
            _browser = '/'.join(self.portal_utils.browserDefault(aq_base(obj))[1])
        except AttributeError:
            _browser = None
        
        if _browser not in ['folder_listing']:
            self['_layout'] = ''
            self['_defaultpage'] = _browser
        #elif obj.getId() != 'index_html':
        #    self['_layout'] = _browser
        #    self['_defaultpage'] = ''

        if obj.portal_type == 'Folder':
            try:
                self['_layout'] = obj.layout
            except AttributeError:
                self['_layout'] = ''
        # format
        self['_content_type'] = obj.Format()
        
        # properties
        self['_properties'] = []
        if getattr(aq_base(obj), 'propertyIds', False):
            obj_base = aq_base(obj)
            for pid in obj_base.propertyIds():
                val = obj_base.getProperty(pid)
                typ = obj_base.getPropertyType(pid)
                if typ == 'string':
                    if getattr(val, 'decode', False):
                        try:
                            val = val.decode(self.charset, 'ignore')
                        except UnicodeEncodeError:
                            val = unicode(val)
                    else:
                        val = unicode(val)
                self['_properties'].append((pid, val,
                                       obj_base.getPropertyType(pid)))

        # local roles
        self['_ac_local_roles'] = {}
        if getattr(obj, '__ac_local_roles__', False):
            for key, val in obj.__ac_local_roles__.items():
                if key is not None:
                    self['_ac_local_roles'][key] = val

        self['_userdefined_roles'] = ()
        if getattr(aq_base(obj), 'userdefined_roles', False):
            self['_userdefined_roles'] = obj.userdefined_roles()

        self['_permission_mapping'] = {}
        if getattr(aq_base(obj), 'permission_settings', False):
            roles = obj.validRoles()
            ps = obj.permission_settings()
            for perm in ps:
                unchecked = 0
                if not perm['acquire']:
                    unchecked = 1
                new_roles = []
                for role in perm['roles']:
                    if role['checked']:
                        role_idx = role['name'].index('r')+1
                        role_name = roles[int(role['name'][role_idx:])]
                        new_roles.append(role_name)
                if unchecked or new_roles:
                    self['_permission_mapping'][perm['name']] = \
                         {'acquire': not unchecked,
                          'roles': new_roles}

#        self['_ac_inherited_permissions'] = {}
#        if getattr(aq_base(obj), 'ac_inherited_permissions', False):
#            oldmap = getPermissionMapping(obj.ac_inherited_permissions(1))
#            for key, values in oldmap.items():
#                old_p = Permission(key, values, obj)
#                self['_ac_inherited_permissions'][key] = old_p.getRoles()

        if getattr(aq_base(obj), 'getWrappedOwner', False):
            self['_owner'] = (1, obj.getWrappedOwner().getId())
        else:
            # fallback
            # not very nice but at least it works
            # trying to get/set the owner via getOwner(), changeOwnership(...)
            # did not work, at least not with plone 1.x, at 1.0.1, zope 2.6.2
            self['_owner'] = (0, obj.getOwner(info = 1).getId())

    def decode(self, s, encodings=('utf8', 'latin1', 'ascii')):
        if self.charset:
            test_encodings = (self.charset, ) + encodings
        for encoding in test_encodings:
            try:
                return s.decode(encoding)
            except UnicodeDecodeError:
                pass
        return s.decode(test_encodings[0], 'ignore')


class PaginaWrapper(BaseWrapper):

    def __init__(self, obj):
        super(PaginaWrapper, self).__init__(obj)
        self['text'] = obj.getText().decode(self.charset, 'ignore')
        self['eixo'] = obj.eixo
        self['area'] = obj.area


class I18NFolderWrapper(BaseWrapper):

    def __init__(self, obj):
        super(I18NFolderWrapper, self).__init__(obj)
        # We are ignoring another languages
        lang = obj.getDefaultLanguage()
        data = obj.folder_languages.get(lang, None)
        if data is not None:
            self['title'] = data['title'].decode(self.charset, 'ignore')
            self['description'] = data['description'].decode(self.charset, 'ignore')
        else:
            print 'ERROR: Cannot get default data for I18NFolder "%s"' % self['_path']

        # delete empty title in properties
        for prop in self['_properties']:
            propname, propvalue, proptitle = prop
            if propname == "title":
                self['_properties'].remove(prop)


        # Not lose information: generate properites es_title, en_title, etc.
        for lang in obj.folder_languages:
            data = obj.folder_languages[lang]
            for field in data:
                self['_properties'].append(['%s_%s' % (lang, field),
                                            data[field].decode(self.charset, 'ignore'),
                                            'text'])


class LinksWrapper(BaseWrapper):

    def __init__(self, obj):
        super(LinksWrapper, self).__init__(obj)
        self['remoteUrl'] = obj.remote_url()
        self['eixo'] = obj.eixo
        self['area'] = obj.area


class NoticiaWrapper(BaseWrapper):

    def __init__(self, obj):
        super(NoticiaWrapper, self).__init__(obj)
        self['text'] = obj.getText().decode(self.charset, 'ignore')
        self['text_format'] = obj.text_format
        try:
            data = str(obj.getImage().data)
            self['__datafields__'].append('_datafield_image')
            self['_datafield_image'] = data
        except AttributeError:
            pass


class ListCriteriaWrapper(BaseWrapper):

    def __init__(self, obj):
        super(ListCriteriaWrapper, self).__init__(obj)
        self['field'] = obj.field
        self['value'] = obj.value
        self['operator'] = obj.operator


class StringCriteriaWrapper(BaseWrapper):

    def __init__(self, obj):
        super(StringCriteriaWrapper, self).__init__(obj)
        self['field'] = obj.field
        self['value'] = obj.value


class SortCriteriaWrapper(BaseWrapper):

    def __init__(self, obj):
        super(SortCriteriaWrapper, self).__init__(obj)
        self['field'] = obj.field
        self['reversed'] = obj.reversed


class ATRelativePathCriterionWrapper(BaseWrapper):

    def __init__(self, obj):
        super(ATRelativePathCriterionWrapper, self).__init__(obj)
        self['field'] = obj.field
        self['relativePath'] = obj.relativePath
        self['recurse'] = obj.recurse


class ATPortalTypeCriterionWrapper(BaseWrapper):

    def __init__(self, obj):
        super(ATPortalTypeCriterionWrapper, self).__init__(obj)
        self['field'] = obj.field
        self['value'] = obj.value
        self['operator'] = obj.operator
        

class ATPathCriterionWrapper(BaseWrapper):

    def __init__(self, obj):
        super(ATPathCriterionWrapper, self).__init__(obj)
        self['field'] = obj.field
        self['recurse'] = obj.recurse


class DateCriteriaWrapper(BaseWrapper):

    def __init__(self, obj):
        super(DateCriteriaWrapper, self).__init__(obj)
        self['field'] = obj.field
        self['value'] = obj.value
        self['operation'] = obj.operation
        self['daterange'] = obj.daterange


class ArquivoWrapper(BaseWrapper):

    def __init__(self, obj):
        super(ArquivoWrapper, self).__init__(obj)
        self['__datafields__'].append('_datafield_file')
        data = str(obj.data)
        self['_datafield_file'] = data
        self['eixo'] = obj.eixo
        self['area'] = obj.area


class ImageWrapper(BaseWrapper):

    def __init__(self, obj):
        super(ImageWrapper, self).__init__(obj)
        self['__datafields__'].append('_datafield_image')
        data = str(obj.data)
        self['_datafield_image'] = data


class EventoWrapper(BaseWrapper):

    def __init__(self, obj):
        super(EventoWrapper, self).__init__(obj)
        self['startDate'] = str(obj.start_date)
        self['endDate'] = str(obj.end_date)
        self['location'] = obj.location
        self['contactName'] = obj.contact_name()
        self['contactEmail'] = obj.contact_email()
        self['contactPhone'] = obj.contact_phone()
        self['eventUrl'] = obj.event_url()


class ZopeObjectWrapper(BaseWrapper):

    def __init__(self, obj):
        super(ZopeObjectWrapper, self).__init__(obj)
        self['document_src'] = self.decode(obj.document_src())
        # self['__datafields__'].append('document_src')


# TODO: should be also possible to set it with through parameters
CLASSNAME_TO_WAPPER_MAP = {
    'LargePloneFolder':         BaseWrapper,
    'ATFolder':                 BaseWrapper,
    'PloneSite':                BaseWrapper,
    'PloneFolder':              BaseWrapper,
    'ATTopic':                  BaseWrapper,
    'ListCriterion':            ListCriteriaWrapper,
    'SimpleStringCriterion':    StringCriteriaWrapper,
    'ATSortCriterion':          SortCriteriaWrapper,
    'FriendlyDateCriterion':    DateCriteriaWrapper,
    'ATRelativePathCriterion':  ATRelativePathCriterionWrapper,
    'ATPortalTypeCriterion':    ATPortalTypeCriterionWrapper,
    'ATSelectionCriterion':     ATPortalTypeCriterionWrapper,
    'ATPathCriterion':          ATPathCriterionWrapper,
    'ATImage':                  ImageWrapper,

    # conteudos SERPRO
    'Pagina':                   PaginaWrapper,
    'Arquivo':                  ArquivoWrapper,
    'Links':                    LinksWrapper,
    'Evento':                   EventoWrapper,
    'Noticia':                  NoticiaWrapper,
    'FolderEventos':            BaseWrapper,

    # other contents
    'DTMLMethod':               ZopeObjectWrapper,
    'ZopePageTemplate':         ZopeObjectWrapper,
}

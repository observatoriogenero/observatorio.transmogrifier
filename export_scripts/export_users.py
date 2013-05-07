
import os
import shutil
import simplejson
from datetime import datetime
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName

COUNTER = 1

HOMEDIR = '/home/essencis/intranet_essencis/exported_data'

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
                     'ContentPanelsTool', 'RAMCacheManager', 'SinTool', 'ContentPanels',
                     'BookingTool', 'PlonePopollTool','PlacefulWorkflowTool', 'ChecklistTool',
                     'PublicatorTool', 'ContractTool', 'CronTool','CatalogServiceDesk',
                     'CatalogCurriculum', 'CatalogIndicadores', 'TinyMCE','RedirectionTool',
                     'SquidTool', 'JobPerformanceTool', 'CacheTool', 'FormGenTool',
                     'WorkflowPolicyConfig', 'MessageTool', 'PloneboardTool', 'Analytics', 'PageCacheManager',
                     'CSCachingPolicyManager', 'PolicyHTTPCacheManager', 'PolicyHTTPCacheManager',
                     'RAMCacheManager','SyndicationInformation','FaqFolder','PersonalData',
                     'Checklist','PloneboardComment','FaqEntry','PloneboardConversation',
                     'Ploneboard','AbroadExperience','PloneboardForum','ServiceDesk','Ideia',
                     'IdeiasFolder','PlonePopoll','ATBlob','Curriculum',
                     'PloneSite', 'ATDocument','ATFile', 'ATImage', 'ATLink',
                     'ATEvent', 'ATNewsItem', 'ATTopic', 'ListCriterion', 'SimpleStringCriterion',
                     'ATSortCriterion','FriendlyDateCriterion', 'ATRelativePathCriterion',
                     'ATPortalTypeCriterion', 'ATSelectionCriterion', 'ATPathCriterion',
                     'FormFolder', 'FormMailerAdapter', 'FGStringField', 'FGTextField',
                     'FormThanksPage', 'FGBooleanField', 'FormCustomScriptAdapter', 'FGDateField',
                     'FGFixedPointField', 'FGLabelField', 'FGLinesField', 'FGMultiSelectField',
                     'FGPasswordField', 'FGLikertField', 'FGRichLabelField', 'FGRichTextField',
                     'FormSaveDataAdapter', 'FGSelectionField', 'FieldsetFolder','FGIntegerField', 'FGFileField',]

ID_TO_SKIP = ['Members', ]


def export_plone_essencis(self):

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
        if item.__class__.__name__ in CLASSNAME_TO_SKIP or\
           item.getId() in ID_TO_SKIP:
            continue
        if item.__class__.__name__ in CLASSNAME_TO_SKIP_LAUD:
            print '>> SKIPPING :: ['+item.__class__.__name__+'] '+item.absolute_url()
            continue
        yield item
        if getattr(item, 'objectIds', None) and\
           item.objectIds():
            for subitem in walk(item):
                yield subitem


def write(items):
    global COUNTER

    for item in items:
        if item.__class__.__name__ not in CLASSNAME_TO_WAPPER_MAP.keys():
            raise Exception, 'No wrapper defined for "'+item.__class__.__name__+\
                             '" ('+item.absolute_url()+').'
        try:
            dictionary = CLASSNAME_TO_WAPPER_MAP[item.__class__.__name__](item)
            write_to_jsonfile(dictionary)
            COUNTER += 1
        except:
            print '>> PROBLEM EXPORTING ::['+item.__class__.__name__+'] '+item.absolute_url()
            import pdb; pdb.set_trace()


def write_to_jsonfile(item):
    global COUNTER

    SUB_TMPDIR = os.path.join(TMPDIR, str(COUNTER/1000)) # 1000 files per folder, so we dont reach some fs limit
    if not os.path.isdir(SUB_TMPDIR):
        os.mkdir(SUB_TMPDIR)

    # we store data fields in separate files
    datafield_counter = 1
    if 'picture' in item.keys():
        datafield_filepath = os.path.join(SUB_TMPDIR, str(COUNTER)+'.json-file-'+str(datafield_counter))
        f = open(datafield_filepath, 'wb')
        f.write(item['picture'])
        item['picture'] = os.path.join(str(COUNTER/1000), str(COUNTER)+'.json-file-'+str(datafield_counter))
        f.close()

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
                try:
                    val = obj_base.getProperty(pid)
                except AttributeError:
                    pass
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
                    self['_permission_mapping'][perm['name']] =\
                    {'acquire': not unchecked,
                     'roles': new_roles}

                #        self['_ac_inherited_permissions'] = {}
                #        if getattr(aq_base(obj), 'ac_inherited_permissions', False):
                #            oldmap = getPermissionMapping(obj.ac_inherited_permissions(1))
                #            for key, values in oldmap.items():
                #                old_p = Permission(key, values, obj)
                #                self['_ac_inherited_permissions'][key] = old_p.getRoles()

        if getattr(aq_base(obj), 'getWrappedOwner', False):
            try:
                self['_owner'] = (1, obj.getWrappedOwner().getId())
            except AttributeError:
                self['_owner'] = 'admin_simples'             
        else:
            # fallback
            # not very nice but at least it works
            # trying to get/set the owner via getOwner(), changeOwnership(...)
            # did not work, at least not with plone 1.x, at 1.0.1, zope 2.6.2
            try:
                self['_owner'] = (0, obj.getOwner().getId())
            except AttributeError:
                self['_owner'] = 'admin_simples'

    def decode(self, s, encodings=('utf8', 'latin1', 'ascii')):
        if self.charset:
            test_encodings = (self.charset, ) + encodings
        for encoding in test_encodings:
            try:
                return s.decode(encoding)
            except UnicodeDecodeError:
                pass
        return s.decode(test_encodings[0], 'ignore')


class EmployeeWrapper(BaseWrapper):

    def __init__(self, obj):
        super(EmployeeWrapper, self).__init__(obj)

        self['employee_id'] = int(obj.registration)
        self['given_name'] = obj.firstName
        self['surname'] = obj.lastName
        if obj.getOrganizationUnit():
            self['ou'] = obj.getOrganizationUnit()

        if obj['personal']:
            p = obj['personal']
            self['position'] = p.cargo
            self['gender'] = p.gender
            self['telephones'] = p.telephone
            self['emails'] = p.email
            if p.birthDate:
                self['birthday'] = p.birthDate.strftime('%Y-%m-%d')
            else:
                self['birthday'] = p.birthDate
            try:
                image=p.image
            except AttributeError:
                image=None
            if image:
                try:
                    data = image.data.data
                except:
                    data = image.data
                self['picture'] = data
                self['_filename'] = image.filename


# TODO: should be also possible to set it with through parameters
CLASSNAME_TO_WAPPER_MAP = {
    'LargePloneFolder':         BaseWrapper,
    'ATFolder':                 BaseWrapper,
    'PloneSite':                BaseWrapper,
    'PloneFolder':              BaseWrapper,
    'Department':               BaseWrapper,
    'Employee':                 EmployeeWrapper,
    'OrganizationUnit':         BaseWrapper,
    'WorkLocation':             BaseWrapper, 
    }

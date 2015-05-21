from ploneintranet.workspace.tests.base import BaseTestCase
from plone import api
from plone.app.testing import login
from plone.app.testing import logout

VIEW = 'View'
ACCESS = 'Access contents information'
MODIFY = 'Modify portal content'
MANAGE = 'ploneintranet.workspace: Manage workspace'


class TestWorkSpaceWorkflow(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.login_as_portal_owner()
        api.user.create(username='nonmember', email="user@test.com")
        api.user.create(username='wsmember', email="member@test.com")
        api.user.create(username='wsadmin', email="admin@test.com")
        self.workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='Welcome to my workspace')
        self.add_user_to_workspace('wsmember', self.workspace_folder)
        self.add_user_to_workspace('wsadmin', self.workspace_folder,
                                   set(['Admins']))

    def test_private_workspace(self):
        """
        Private workspaces should be visible to all,
        but only accessible to members
        """
        api.content.transition(self.workspace_folder,
                               'make_private')

        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.workspace_folder,
        )
        self.assertTrue(admin_permissions[VIEW],
                        'Admin cannot view private workspace')
        self.assertTrue(admin_permissions[ACCESS],
                        'Admin cannot access contents of private workspace')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.workspace_folder,
        )
        self.assertTrue(member_permissions[VIEW],
                        'Member cannot view private workspace')
        self.assertTrue(member_permissions[ACCESS],
                        'Member cannot access contents of private workspace')

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.workspace_folder,
        )
        self.assertTrue(nonmember_permissions[VIEW],
                        'Non-member cannot view private workspace')
        self.assertFalse(nonmember_permissions[ACCESS],
                         'Non-member can access private workspace')

        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.workspace_folder,
        )
        self.assertFalse(anon_permissions[VIEW],
                         'Anonymous can view private workspace')
        self.assertFalse(anon_permissions[ACCESS],
                         'Anonymous can access contents of private workspace')

    def test_secret_workspace(self):
        """
        Secret workspaces should be invisible to all but members
        """
        # default state is secret
        self.assertEqual(api.content.get_state(self.workspace_folder),
                         'secret')

        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.workspace_folder,
        )
        self.assertTrue(admin_permissions[VIEW],
                        'admin cannot view secret workspace')
        self.assertTrue(admin_permissions[ACCESS],
                        'admin cannot access contents of secret workspace')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.workspace_folder,
        )
        self.assertTrue(member_permissions[VIEW],
                        'Member cannot view secret workspace')
        self.assertTrue(member_permissions[ACCESS],
                        'Member cannot access contents of secret workspace')

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.workspace_folder,
        )
        self.assertFalse(nonmember_permissions[VIEW],
                         'Non-member can view secret workspace')
        self.assertFalse(nonmember_permissions[ACCESS],
                         'Non-member can access contents of secret workspace')

        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.workspace_folder,
        )
        self.assertFalse(anon_permissions[VIEW],
                         'Anonymous can view secret workspace')
        self.assertFalse(anon_permissions[ACCESS],
                         'Anonymous can access contents of secret workspace')

    def test_open_workspace(self):
        """
        Open workspaces should be visible
        and accessible to all users

        Content within open workspace is also visible
        to all users
        """
        api.content.transition(self.workspace_folder,
                               'make_open')

        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.workspace_folder,
        )
        self.assertTrue(admin_permissions[VIEW],
                        'admin cannot view open workspace')
        self.assertTrue(admin_permissions[ACCESS],
                        'admin cannot access contents of open workspace')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.workspace_folder,
        )
        self.assertTrue(member_permissions[VIEW],
                        'Member cannot view open workspace')
        self.assertTrue(member_permissions[ACCESS],
                        'Member cannot access contents of open workspace')

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.workspace_folder,
        )
        self.assertTrue(nonmember_permissions[VIEW],
                        'Non-Member cannot view open workspace')
        self.assertTrue(nonmember_permissions[ACCESS],
                        'Non-Member cannot access contents of open workspace')

        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.workspace_folder,
        )
        self.assertFalse(anon_permissions[VIEW],
                         'Anonymous can view open workspace')
        self.assertFalse(anon_permissions[ACCESS],
                         'Anonymous can access contents of open workspace')

    def test_modify_workspace(self):
        """
        Only a Workspace Admin should be able to edit the workspace.
        A user with the Editor role should not be able
        to edit the workspace itself (only the content within a workspace)
        """

        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.workspace_folder,
        )
        self.assertTrue(admin_permissions[MODIFY],
                        'Admin cannot modify workspace')

        # A workspace editor
        api.user.create(username='wseditor', email='wseditor@test.com')
        self.add_user_to_workspace('wseditor', self.workspace_folder)
        # Grant them the Editor role on the workspace
        api.user.grant_roles(
            username='wseditor',
            obj=self.workspace_folder,
            roles=['Editor'],
        )
        editor_permissions = api.user.get_permissions(
            username='wseditor',
            obj=self.workspace_folder,
        )

        # Editor cannot edit workspace itself, only content within
        self.assertFalse(editor_permissions[MODIFY],
                         'Editor can modify workspace content')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.workspace_folder,
        )
        self.assertFalse(member_permissions[MODIFY],
                         'Member can modify workspace')

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.workspace_folder,
        )
        self.assertFalse(nonmember_permissions[MODIFY],
                         'Non-member can modify workspace')

        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.workspace_folder,
        )
        self.assertFalse(anon_permissions[MODIFY],
                         'Anon can modify workspace')

    def test_manage_workspace(self):
        """
        A Workspace Admin should have the manage workspace permission
        """
        # A workspace admin can manage the workspace
        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.workspace_folder,
        )
        self.assertTrue(
            admin_permissions[MANAGE],
            'Admin cannot manage workspace'
        )

        # A workspace member cannot manage the workspace
        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.workspace_folder,
        )
        self.assertFalse(
            member_permissions[MANAGE],
            'Member can manage workspace'
        )

        # A normal user cannot manage the workspace
        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.workspace_folder,
        )
        self.assertFalse(
            nonmember_permissions[MANAGE],
            'Non-Member can manage workspace'
        )

        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.workspace_folder,
        )
        self.assertFalse(
            anon_permissions[MANAGE],
            'Anon can manage workspace'
        )

    def test_workspace_transitions(self):
        """
        A Workspace Admin should be able to change the state of a workspace
        """
        # The Admin should have the manage workspace permission
        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.workspace_folder,
        )
        self.assertTrue(
            admin_permissions[MANAGE],
            'Admin cannot manage workspace'
        )

        # The Admin should be able to transition the workspace
        # through each state
        login(self.portal, 'wsadmin')

        api.content.transition(self.workspace_folder,
                               'make_private')
        self.assertEqual(api.content.get_state(self.workspace_folder),
                         'private')

        api.content.transition(self.workspace_folder,
                               'make_open')
        self.assertEqual(api.content.get_state(self.workspace_folder),
                         'open')

        api.content.transition(self.workspace_folder,
                               'make_secret')
        self.assertEqual(api.content.get_state(self.workspace_folder),
                         'secret')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.workspace_folder,
        )
        self.assertFalse(
            member_permissions[MANAGE],
            'Member can manage workspace'
        )

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.workspace_folder,
        )
        self.assertFalse(
            nonmember_permissions[MANAGE],
            'Non-member can manage workspace'
        )

        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.workspace_folder,
        )
        self.assertFalse(
            anon_permissions[MANAGE],
            'Anon can manage workspace'
        )

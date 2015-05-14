# -*- coding: utf-8 -*-
from Acquisition import Explicit
# from BTrees import LOBTree
from BTrees import OOBTree
from persistent import Persistent
from ploneintranet.network.interfaces import ILikesContainer
from zope.interface import implementer


@implementer(ILikesContainer)
class LikesContainer(Persistent, Explicit):

    def __init__(self, context=None):
        # maps user id to liked content uids
        self._user_uuids_mapping = OOBTree.OOBTree()
        # maps content uid to user ids
        self._uuid_users_mapping = OOBTree.OOBTree()

        # maps user id to liked status ids
        # self._user_statusids_mapping = LOBTree.LOBTree()
        # maps status id to user ids
        # self._statusid_users_mapping = OOBTree.OOBTree()

    def like(self, user_id, item_id):
        assert(user_id == str(user_id))
        assert(item_id == str(item_id))

        self._user_uuids_mapping.insert(user_id, OOBTree.OOTreeSet())
        self._uuid_users_mapping.insert(item_id, OOBTree.OOTreeSet())

        self._user_uuids_mapping[user_id].insert(item_id)
        self._uuid_users_mapping[item_id].insert(user_id)

    def unlike(self, user_id, item_id):
        assert(user_id == str(user_id))
        assert(item_id == str(item_id))

        try:
            self._user_uuids_mapping[user_id].remove(item_id)
        except KeyError:
            pass
        try:
            self._uuid_users_mapping[item_id].remove(user_id)
        except KeyError:
            pass

    def get(self, user_id):
        assert(user_id == str(user_id))
        try:
            return self._user_uuids_mapping[user_id]
        except KeyError:
            return []

    def get_items_for_user(self, user_id):
        return self.get(user_id)

    def lookup(self, item_id):
        assert(item_id == str(item_id))
        try:
            return self._uuid_users_mapping[item_id]
        except KeyError:
            return []

    def get_users_for_item(self, item_id):
        return self.lookup(item_id)

    def is_item_liked_by_user(self, user_id, item_id):
        try:
            return user_id in self.lookup(item_id)
        except KeyError:
            return False

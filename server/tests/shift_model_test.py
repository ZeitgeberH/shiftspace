import unittest
import datetime
import server.models.core as core

from server.models.shift import Shift
from server.models.ssuser import SSUser
from server.models.group import Group
from server.models.permission import Permission
from server.tests.dummy_data import *


class BasicOperations(unittest.TestCase):

    def setUp(self):
        db = core.connect()
        self.fakemary = SSUser.create(fakemary)
        self.fakejohn = SSUser.create(fakejohn)
        self.fakebob = SSUser.create(fakebob)
        self.root = SSUser.read("shiftspace")

    """
    def testCreate(self):
        json = shiftJson()
        json["createdBy"] = self.fakemary.id
        theShift = Shift.create(json)
        self.assertEqual(theShift.type, "shift")
        self.assertEqual(theShift.createdBy, self.fakemary.id)
        self.assertNotEqual(theShift.created, None)
        self.assertEqual(type(theShift.created), datetime.datetime)
        self.assertNotEqual(theShift.modified, None)
        self.assertEqual(type(theShift.modified), datetime.datetime)
        self.assertEqual(theShift.domain, "http://google.com")
        db = core.connect(SSUser.privateDb(self.fakemary.id))
        del db[theShift.id]

    def testRead(self):
        json = shiftJson()
        json["createdBy"] = self.fakemary.id
        newShift = Shift.create(json)
        theShift = Shift.read(newShift.id, self.fakemary.id)
        self.assertEqual(theShift.source.server, newShift.source.server)
        self.assertEqual(theShift.source.database, newShift.source.database)
        self.assertEqual(theShift.createdBy, self.fakemary.id)
        db = core.connect(SSUser.privateDb(self.fakemary.id))
        del db[theShift.id]

    def testUpdate(self):
        json = shiftJson()
        json["createdBy"] = self.fakemary.id
        newShift = Shift.create(json)
        newShift.update({"summary":"changed!"})
        theShift = Shift.read(newShift.id, self.fakemary.id)
        self.assertEqual(theShift.summary, "changed!")
        db = core.connect(SSUser.privateDb(self.fakemary.id))
        del db[theShift.id]

    def testDelete(self):
        json = shiftJson()
        json["createdBy"] = self.fakemary.id
        newShift = Shift.create(json)
        self.assertNotEqual(newShift, None)
        newShift.delete()
        theShift = Shift.read(newShift.id, self.fakemary.id)
        self.assertEqual(theShift, None)

    def testJoinData(self):
        json = shiftJson()
        json["createdBy"] = self.fakemary.id
        newShift = Shift.create(json)
        # gravatar not a real property, added via Shift.joinData
        self.assertNotEqual(newShift["gravatar"], None)

    def testCanModify(self):
        json = shiftJson()
        json["createdBy"] = self.fakemary.id
        newShift = Shift.create(json)
        self.assertTrue(self.fakemary.canModify(newShift))
        self.assertTrue(not self.fakejohn.canModify(newShift))
        self.assertTrue(self.root.canModify(newShift))
    """

    def testBasicPublish(self):
        json = shiftJson()
        json["createdBy"] = self.fakemary.id
        newShift = Shift.create(json)
        newShift.publish({"private":False})
        # should exist in user/public db
        theShift = Shift.load(core.connect(SSUser.publicDb(self.fakemary.id)), newShift.id)
        self.assertEqual(theShift.summary, newShift.summary)
        self.assertTrue(not theShift.publishData.draft)
        self.assertTrue(not theShift.publishData.private)
        # should exist in shiftspace/public db 
        theShift = Shift.load(core.connect("shiftspace/public"), newShift.id)
        self.assertEqual(theShift.summary, newShift.summary)
        self.assertTrue(not theShift.publishData.draft)
        self.assertTrue(not theShift.publishData.private)
        # should exist in shiftspace/shared db
        theShift = Shift.load(core.connect("shiftspace/shared"), newShift.id)
        self.assertEqual(theShift.summary, newShift.summary)
        self.assertTrue(not theShift.publishData.draft)
        self.assertTrue(not theShift.publishData.private)
        # should _not_ exist in user/private db
        theShift = Shift.load(core.connect(SSUser.privateDb(self.fakemary.id)), newShift.id)
        self.assertEqual(theShift, None)

    """
    def testPublishToFollowers(self):
        json = shiftJson()
        json["createdBy"] = self.fakemary.id
        newShift = Shift.create(json)
        self.fakejohn.follow(self.fakemary)
        fakejohn = SSUser.read(self.fakejohn.id)
        # should be in the list of people fakejohn is following
        self.assertTrue(self.fakemary.id in fakejohn.following())
        # should be in the list of fakemary's followers
        followers = self.fakemary.followers()
        self.assertTrue(self.fakejohn.id in followers)
        newShift.publish({"private":False})
        # should exist in shiftspace/shared db
        theShift = Shift.load(core.connect("shiftspace/shared"), newShift.id)
        self.assertEqual(theShift.summary, newShift.summary)


    def testPublishToUser(self):
        json = shiftJson()
        json["createdBy"] = self.fakemary.id
        newShift = Shift.create(json)
        publishData = {
            "dbs": [SSUser.db(self.fakejohn.id)]
            }
        newShift.publish(publishData)
        # should exist in user feed
        # TODO: in inbox if peer - David 11/18/09
        theShift = Shift.load(core.connect("shiftspace/shared"), newShift.id)
        self.assertEqual(theShift.summary, newShift.summary)

    def testPublishToGroup(self):
        json = shiftJson()
        json["createdBy"] = self.fakemary.id
        newShift = Shift.create(json)
        json = groupJson()
        json["createdBy"] = self.fakemary.id
        newGroup = Group.create(json)
        # make sure fakemary owns the group
        newPerm = Permission.readByUserAndGroup(self.fakemary.id, newGroup.id)
        self.assertTrue(newPerm.level == 4)
        # create read permission for fakejohn
        newPerm = Permission.create("shiftspace", newGroup.id, self.fakejohn.id, level=1)
        fakejohn = SSUser.read(self.fakejohn.id)
        self.assertTrue(Group.db(newGroup.id) in fakejohn.readable())
        publishData = {
            "dbs": [Group.db(newGroup.id)]
            }
        newShift.publish(publishData)
        # should exists in shiftspace/shared
        db = core.connect("shiftspace/shared")
        theShift = Shift.load(db, newShift.id)
        self.assertEqual(theShift.summary, newShift.summary)
        newGroup.delete()

    def testPublishToGroupAndUser(self):
        json = shiftJson()
        json["createdBy"] = self.fakemary.id
        newShift = Shift.create(json)
        json = groupJson()
        json["createdBy"] = self.fakemary.id
        newGroup = Group.create(json)
        newPerm = Permission.create("shiftspace", newGroup.id, self.fakejohn.id, level=1)
        publishData = {
            "dbs": [Group.db(newGroup.id), SSUser.db(self.fakebob.id)]
            }
        newShift.publish(publishData)
        # should exist in subscriber's feed
        db = core.connect("shiftspace/shared")
        theShift = Shift.load(db, newShift.id)
        self.assertEqual(theShift.summary, newShift.summary)
        newGroup.delete()
        # should exist in shiftspace/shared
        # TODO: inbox if user is peer - David 11/18/09
        theShift = Shift.load(core.connect("shiftspace/shared"), newShift.id)
        self.assertEqual(theShift.summary, newShift.summary)
    """

    def tearDown(self):
        db = core.connect()
        self.fakemary.delete()
        self.fakejohn.delete()
        self.fakebob.delete()


if __name__ == "__main__":
    unittest.main()

from PyQt6.QtWidgets import QTreeWidgetItem
from PyQt6.QtCore import Qt

class BuddyGroupHuman(QTreeWidgetItem):
    """
      BuddyGroupHuman implements the view of a Buddy group from the Roster
    """

    def __init__(self, name):
        QTreeWidgetItem.__init__(self, [name], QTreeWidgetItem.ItemType.UserType + 1)

        self.name = name
        # QTreeWidgetItem configuration
        self.setFlags(Qt.ItemFlag.ItemIsDropEnabled |  Qt.ItemFlag.ItemIsEnabled)  # We can move a contact into

    def isAway(self):
        for child in self.takeChildren():
            if not child.isAway():
                return False
        return True

    def isOffline(self):
        for child in self.takeChildren():
            if not child.isOffline():
                return False
        return True

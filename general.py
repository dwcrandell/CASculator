#!/usr/bin/python
'''
Generally useful methods
'''
import wx

def get_Selection(list_control):
    selection = []
    current = -1 # start at -1 to get the first selected item
    while True:
        next = GetNextSelected(list_control, current)
        if next == -1:
            return selection
        selection.append(next)
        current = next

def GetNextSelected(list_control, current):
    """Returns next selected item, or -1 when no more"""
    return list_control.GetNextItem(current,wx.LIST_NEXT_ALL,wx.LIST_STATE_SELECTED)

def getColumn(list_ctrl):
    count = list_ctrl.GetItemCount()
    orb_list = []
    for row in range(count):
        item = list_ctrl.GetItem(itemId=row, col=0)
        orb_list.append(item.GetText())
    return orb_list

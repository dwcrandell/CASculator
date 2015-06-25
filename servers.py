#!/usr/bin/python
'''
Server Database for Casculator Version 1.1
Douglas Crandell-Indiana University-Bloomington, IN 47401
7/21/2014
'''
import wx
import sqlite3 as lite
import os,sys
import general as gen
import base64

def getServerNames():
    name_list = []
    con = lite.connect('cas.sqlite')
    cursor = con.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS Servers(
	               id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,name TEXT,address TEXT,calcpath TEXT,user TEXT,password TEXT)""")
    con.commit()
    with con:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM Servers")
        rows = cursor.fetchall()
        for row in rows:
            current = 0
            for item in row[1:-1]:
                if current == 0:
                    name_list.append(str(item))
                    current += 1
    return name_list

class ServerDialog(wx.Dialog):
    def __init__(self,parent, id, title):
        wx.Dialog.__init__(self,parent,id,title,size = (600,350), style=wx.DEFAULT_DIALOG_STYLE)
        self.comp_list = parent.computers
        pnl = wx.Panel(self,-1,style=wx.SIMPLE_BORDER)
        vbox1 = wx.BoxSizer(wx.VERTICAL)
        vbox2 = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.name_tc = wx.TextCtrl(pnl,size = (75,20))
        self.address_tc = wx.TextCtrl(pnl,size = (150,20))
        self.cp_tc = wx.TextCtrl(pnl,size = (150,20))
        self.uid_tc = wx.TextCtrl(pnl,size = (75,20))
        self.pwd_tc = wx.TextCtrl(pnl,style=wx.TE_PASSWORD,size = (100,20))
        self.server_lc = wx.ListCtrl(pnl,11,style=wx.LC_REPORT)
        self.server_lc.InsertColumn(0, 'Name')
        self.server_lc.InsertColumn(1, 'Address')
        self.server_lc.InsertColumn(2, 'CalcPath')
        self.server_lc.InsertColumn(3, 'User ID')
        self.server_lc.SetColumnWidth(1,150)
        self.server_lc.SetColumnWidth(2,255)
        self.populateServers(self.server_lc)
        vbox1.Add(pnl, 1, wx.EXPAND | wx.ALL, 3)
        hbox1.AddMany([(wx.StaticText(pnl, -1, 'Name'), 0, wx.ALIGN_LEFT|wx.LEFT, 5),
                       (wx.StaticText(pnl, -1, 'Address'), 0, wx.ALIGN_LEFT|wx.LEFT, 50),
                       (wx.StaticText(pnl, -1, 'CalcPath'), 0, wx.ALIGN_LEFT|wx.LEFT, 115),
                       (wx.StaticText(pnl, -1, 'UserID'), 0, wx.ALIGN_LEFT|wx.LEFT, 105),
                       (wx.StaticText(pnl, -1, 'Password'), 0,wx.ALIGN_LEFT|wx.LEFT, 45)])
        hbox2.AddMany([(self.name_tc, 0, wx.ALIGN_LEFT|wx.LEFT, 5),
                       (self.address_tc, 0, wx.ALIGN_LEFT|wx.LEFT, 5),
                       (self.cp_tc, 0, wx.ALIGN_LEFT|wx.LEFT, 5),
                       (self.uid_tc, 0, wx.ALIGN_LEFT|wx.LEFT, 5),
                       (self.pwd_tc, 0, wx.ALIGN_LEFT|wx.LEFT, 5)])
        vbox2.Add(wx.Button(pnl, 10, 'Add Server'))
        vbox2.Add(hbox1,0,wx.ALIGN_LEFT|wx.TOP, 10)
        vbox2.Add(hbox2,0,wx.ALIGN_LEFT|wx.TOP, 10)
        vbox2.Add(self.server_lc,0,wx.ALIGN_LEFT|wx.LEFT|wx.TOP,5)
        vbox2.Add(wx.Button(pnl,12,'Delete Server'),0, wx.ALIGN_LEFT|wx.TOP,10)
        
        pnl.SetSizer(vbox2)
        self.Bind(wx.EVT_BUTTON, lambda event: self.onAddServer(event, self.comp_list), id=10)
        self.Bind(wx.EVT_BUTTON, lambda event: self.onDeleteServer(event, self.comp_list), id=12)

    def populateServers(self, listctrl):
        con = lite.connect('cas.sqlite')
        with con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM Servers")
            rows = cursor.fetchall()
            num_items = listctrl.GetItemCount()
            for row in rows:
                current = 0
                for item in row[1:-1]:
                    if current == 0:
                        listctrl.InsertStringItem(num_items,item)
                        current += 1
                    else:
                        listctrl.SetStringItem(num_items,current,item)
                        current +=1
                num_items += 1
        return rows        

    def onAddServer(self,event,comp_list):
        u_name = self.name_tc.GetValue()
        u_address = self.address_tc.GetValue()
        u_calcpath = self.cp_tc.GetValue()
        u_userid = self.uid_tc.GetValue()
        pwd = '"' + self.pwd_tc.GetValue() +'"'
        u_password = base64.b64encode(self.pwd_tc.GetValue())
        try:
            con = lite.connect('cas.sqlite')
            cursor = con.cursor()  
            cursor.execute("""CREATE TABLE IF NOT EXISTS Servers(
	               id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,name TEXT,address TEXT,calcpath TEXT,user TEXT,password TEXT)""")
            q ="""INSERT INTO Servers(name,address,calcpath,user,password)VALUES(?,?,?,?,?)"""
            cursor.execute(q,(u_name,u_address,u_calcpath,u_userid,u_password))
            con.commit()
        except lite.Error, e:
            if con:
                con.rollback()
            print "Error %s:" % e.args[0]
            sys.exit(1)
        finally:
            if con:
                con.close()
        num_items = self.server_lc.GetItemCount()
        self.server_lc.InsertStringItem(num_items,u_name)
        self.server_lc.SetStringItem(num_items,1,u_address)
        self.server_lc.SetStringItem(num_items,2,u_calcpath)
        self.server_lc.SetStringItem(num_items,3,u_userid)
        comp_list.Append(u_name)

    def onDeleteServer(self,event,comp_list):
        selected = gen.get_Selection(self.server_lc)
        server = self.server_lc.GetItemText(selected[0])
        try:
            con = lite.connect('cas.sqlite')
            cursor = con.cursor()
            q ="""DELETE FROM Servers WHERE name = '%s';""" %server
            print q
            con.execute(q)
            con.commit()
        except lite.Error, e:
            if con:
                con.rollback()
            print "Error %s:" % e.args[0]
            sys.exit(1)
        finally:
            if con:
                con.close()
        self.server_lc.DeleteItem(selected[0])
        comp_list.Delete(selected[0])


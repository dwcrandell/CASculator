#!/usr/bin/python
'''
Server Database for Casculator Version 1.1
Douglas Crandell-Indiana University-Bloomington, IN 47401
7/21/2014
'''
import wx
import os
import sys
import shutil
import casculator as cas
from decimal import *
import general as gen
import servers
import sshsftp

class RotateDialog(wx.Dialog):
    def __init__(self,parent, id, title):
        wx.Dialog.__init__(self,parent,id,title,size = (600,650), style=wx.DEFAULT_DIALOG_STYLE)
        pnl = wx.Panel(self,-1,style=wx.SIMPLE_BORDER)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        vbox1 = wx.BoxSizer(wx.VERTICAL)
        vbox2 = wx.BoxSizer(wx.VERTICAL)
        vbox3 = wx.BoxSizer(wx.VERTICAL)
        gridsizer = wx.GridSizer(rows = 3,cols=2, hgap = 1, vgap = 5)
        self.oldcalcid_tc = wx.TextCtrl(pnl,size = (150,20))
        self.oldcalcid_tc.SetValue(parent.getCalcID())
        self.newcalcid_tc = wx.TextCtrl(pnl,2,size = (150,20))
        self.newcalcid_tc.SetFocus()
        self.oldorb_tc = wx.TextCtrl(pnl,size=(75,20))
        self.neworb_tc = wx.TextCtrl(pnl,size=(75,20))
        self.oldpath_tc = wx.TextCtrl(pnl, size = (300,20))
        self.newpath_tc = wx.TextCtrl(pnl, size = (300,20))
        self.input_tc = wx.TextCtrl(pnl, size = (300,300), style=wx.TE_MULTILINE)
        self.oldpath_tc.SetValue(parent.tc0.GetValue())
        self.basepath = '\\'.join(parent.tc0.GetValue().split('\\')[:-1])+'\\'
        self.newpath_tc.SetValue('\\'.join(parent.tc0.GetValue().split('\\')[:-1])+'\\')
        self.active_lc = wx.ListCtrl(pnl,4,style=wx.LC_REPORT)
        self.active_lc.InsertColumn(0, 'Orbital')
        self.active_lc.InsertColumn(1, 'Occupation Number')
        self.active_lc.InsertColumn(2, 'Orbital Type')
        self.active_lc.InsertColumn(3, 'Percentage')
        self.active_lc.SetColumnWidth(0,75)
        self.active_lc.SetColumnWidth(1,150)
        self.new_lc = wx.ListCtrl(pnl,5,style=wx.LC_REPORT)
        self.new_lc.InsertColumn(0, 'Orbital')
        self.new_lc.InsertColumn(1, 'Orbital Type')
        self.new_lc.InsertColumn(2, 'Percentage')
        self.new_lc.SetColumnWidth(0,75)
        self.new_lc.SetColumnWidth(1,150)

        server_names = servers.getServerNames()
        self.computers = wx.ComboBox(pnl,choices=server_names,style=wx.CB_READONLY)
        if len(server_names) > 0:
            self.computers.SetValue(server_names[0])

        self.processors_tc = wx.TextCtrl(pnl,size=(40,20))
        self.hours_tc = wx.TextCtrl(pnl,size=(40,20))
        self.memory_tc = wx.TextCtrl(pnl,size =(40,20))
        self.processors_tc.SetValue('32')
        self.hours_tc.SetValue('6')
        self.memory_tc.SetValue('64')

        gridsizer.Add(wx.StaticText(pnl,-1,"#of Processors :"), 0, wx.ALIGN_RIGHT, 5)
        gridsizer.Add(self.processors_tc,0,wx.ALIGN_LEFT)
        gridsizer.Add(wx.StaticText(pnl,-1,"#of Hours :"), 0, wx.ALIGN_RIGHT, 5)
        gridsizer.Add(self.hours_tc,0,wx.ALIGN_LEFT)
        gridsizer.Add(wx.StaticText(pnl,-1,"Memory in GB :"), 0, wx.ALIGN_RIGHT, 5)
        gridsizer.Add(self.memory_tc,0,wx.ALIGN_LEFT)
        
        vbox1.Add(pnl, 1, wx.EXPAND | wx.ALL, 3)
        hbox1.AddMany([(wx.StaticText(pnl, -1, 'Current CalcID :'), 0, wx.ALIGN_LEFT|wx.LEFT, 5),
                       (self.oldcalcid_tc, 0, wx.ALIGN_LEFT|wx.LEFT, 5),
                       (wx.StaticText(pnl, -1, 'New CalcID :'), 0, wx.ALIGN_LEFT|wx.LEFT, 50),
                       (self.newcalcid_tc, 2, wx.ALIGN_LEFT|wx.LEFT, 5)])
        hbox2.AddMany([(self.oldpath_tc,0,wx.ALIGN_LEFT|wx.LEFT|wx.TOP, 5),
                      (self.newpath_tc,0,wx.ALIGN_LEFT|wx.LEFT|wx.TOP, 5)])
        hbox3.AddMany([(wx.StaticText(pnl, -1, 'Active Orbital to Rotate Out :'), 0, wx.ALIGN_LEFT|wx.LEFT, 5),
                       (self.oldorb_tc, 0, wx.ALIGN_LEFT|wx.LEFT, 5),
                       (wx.StaticText(pnl, -1, 'New Orbital to Rotate In :'), 0, wx.ALIGN_LEFT|wx.LEFT, 50),
                       (self.neworb_tc, 2, wx.ALIGN_LEFT|wx.LEFT, 5)])
        hbox4.AddMany([(wx.Button(pnl, 3, 'Rotate'), 0, wx.ALIGN_LEFT|wx.LEFT|wx.TOP, 5),
                       (wx.Button(pnl,6, 'Create Calc'),0, wx.ALIGN_LEFT|wx.LEFT|wx.TOP,5),
                       (wx.Button(pnl,7, 'Launch'),0, wx.ALIGN_LEFT|wx.LEFT|wx.TOP,5),
                       (self.computers, 8, wx.EXPAND|wx.LEFT|wx.TOP,5)])
        vbox3.AddMany([(gridsizer,0,wx.ALIGN_LEFT|wx.LEFT,370),
                      (hbox4,0,wx.ALIGN_LEFT|wx.TOP,-30),
                      (self.active_lc,0,wx.EXPAND|wx.ALL,3),
                      (self.new_lc,0,wx.EXPAND|wx.ALL,3),
                      (self.input_tc,0,wx.EXPAND|wx.ALL,3)])
        vbox2.Add(hbox1,0,wx.ALIGN_LEFT|wx.TOP, 10)
        vbox2.Add(hbox2,0,wx.ALIGN_LEFT|wx.TOP, 10)
        vbox2.Add(hbox3,0,wx.ALIGN_LEFT|wx.TOP, 10)
        vbox2.Add(vbox3,0,wx.ALIGN_LEFT|wx.TOP, 10)
        pnl.SetSizer(vbox2)

        data = cas.open_file(parent.tc0.GetValue())
        start,end,nel,norb = cas.get_active(data)
        old_num_items = self.active_lc.GetItemCount()
        new_num_items = self.new_lc.GetItemCount()
        LCO = cas.get_LCO(data)
        orb_dict = cas.create_OrbDict(LCO)
        comp = cas.get_d_orbitals(LCO,Decimal(parent.tc1.GetValue()))
        for orbital in range(int(start),int(end)+1):
            self.active_lc.InsertStringItem(old_num_items, str(orbital))
            self.active_lc.SetStringItem(old_num_items,1,orb_dict[str(orbital)][1])
            old_num_items += 1
        ordered = {}
        for k in comp.iterkeys():
            ordered[int(k)] = comp[k]
        ordered = sorted(ordered,key=lambda key: key)
        for number in ordered:
            orbitals = comp[str(number)]
            for orb in orbitals:
                self.new_lc.InsertStringItem(new_num_items,str(number))
                self.new_lc.SetStringItem(new_num_items,1,orb[0])
                self.new_lc.SetStringItem(new_num_items,2,orb[1])
                new_num_items += 1

        self.newcalcid_tc.Bind(wx.EVT_TEXT, self.onNewCalcID, id=2)
        self.Bind(wx.EVT_BUTTON, self.onRotateEvent, id=3)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onOldOrb, id=4)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onNewOrb, id=5)
        self.Bind(wx.EVT_BUTTON, self.onCreateCalcEvent, id = 6)
        self.Bind(wx.EVT_BUTTON, self.onLaunch, id = 7)

    def onNewCalcID(self,event):
        self.newcalcid = self.newcalcid_tc.GetValue()
        string = '\\'.join(self.basepath.split('\\')[:-2]) +'\\'
        self.newpath_tc.SetValue(string+self.newcalcid +'\\'+self.newcalcid+'.in')

    def onRotateEvent(self,event):
            self.onRotate()

    def onRotate(self):
        active_orb = self.oldorb_tc.GetValue()
        new_orb = self.neworb_tc.GetValue()
        with open(self.basepath+ self.oldcalcid_tc.GetValue()+'.in', 'r') as f:
            data = f.readlines()
        string =''
        line_nr = 1
        scf = False
        for line in data:
            if scf == True and not line.startswith('end'):
                line = ''
            elif scf == True and line.startswith('end'):
                line = ''
                scf = False
            elif scf == True and line.endswith('end end\n'):
                line = ''
                scf = False
            if line_nr == 1:
                line = '#%s\n' %(self.newcalcid_tc.GetValue())
            if line.startswith("%moinp"):
                line = '%%moinp "%s.gbw"\n' %self.oldcalcid_tc.GetValue()
                line += '%%scf\nrotate {%s,%s,90} end\nend\n' %(active_orb,new_orb)
            elif line.startswith("%scf"):
                scf = True
                line = ''
            string += line
            line_nr += 1
        self.input_tc.SetValue(string)

    def onOldOrb(self,event):
        selected = gen.get_Selection(self.active_lc)
        self.oldorb_tc.SetValue(self.active_lc.GetItemText(selected[0]))

    def onNewOrb(self,event):
        selected = gen.get_Selection(self.new_lc)
        self.neworb_tc.SetValue(self.new_lc.GetItemText(selected[0]))

    def onCreateCalcEvent(self,event):
            self.createCalc()

    def createCalc(self):
        new_path = ('\\').join(self.newpath_tc.GetValue().split('.')[0].split('\\')[:-1])
        input_file = new_path + '\\'+ self.newpath_tc.GetValue().split('\\')[-1]
        if self.newcalcid_tc.GetValue()== "":
             wx.MessageBox('Enter a Calc ID', 'Info', wx.OK | wx.ICON_INFORMATION)
        else:  
            if not os.path.isdir(new_path):
                os.mkdir(new_path)
                self.onRotate()
                shutil.copyfile(self.oldpath_tc.GetValue().split('.')[0]+'.gbw',new_path+'\\'+self.oldcalcid_tc.GetValue()+'.gbw')
                shutil.copyfile(self.oldpath_tc.GetValue().split('.')[0]+'.xyz',new_path+'\\'+self.oldcalcid_tc.GetValue()+'.xyz')
                with open(input_file,'w') as in_f:
                    in_f.write(self.input_tc.GetValue())
            else:
                wx.MessageBox('Directory already exists', 'Info', wx.OK | wx.ICON_INFORMATION)

    def onUpload(self):
        host, path, user, passwd = sshsftp.getLogin(self.computers.GetValue())
        sftp = sshsftp.sftp_connect(host, path, user, passwd)
        ssh = sshsftp.ssh_connect(host, user, passwd)
        calcid = self.newcalcid_tc.GetValue()
        calcdir = path+calcid
        gbw_count = 0
        localdir = '\\'.join(self.oldpath_tc.GetValue().split('\\')[:-1])+ '\\'
        sftp.chdir(path)
        if calcdir not in sftp.listdir():
            try:
                sftp.mkdir(calcid)
            except IOError:
                print 'Error'
        else:
            sftp.chdir(calcdir)
        sftp.chdir(path + calcid)
        for name in os.listdir(localdir):
            localfile = localdir+name
            remotefile = path+calcid+'/'+name
            if name.endswith(".in"):
                sftp.put(localdir+name,path+'/'+calcid+'/'+name)
            elif name.endswith(".gbw"):
                gbw_count += 1
                with open('transfer.txt','a') as f:
                    if gbw_count == 1:
                        f.write('option batch on\noption confirm off\n')
                        connect_string = 'open sftp://%s:%s@%s\n' %(user,passwd,host)
                        f.write(connect_string)
                    upld_string = 'put -transfer=ascii %s %s\n' %(localfile, remotefile)
                    f.write(upld_string)
        if os.path.isfile('transfer.txt'):
            os.system('winscp.exe /script=transfer.txt')
            os.remove('transfer.txt')

    def onLaunch(self,event):
        self.createCalc()
        cpu = self.computers.GetValue()
        calcid = self.newcalcid_tc.GetValue()
        processors = self.processors_tc.GetValue()
        hours = self.hours_tc.GetValue()
        memory = self.memory_tc.GetValue() + 'gb'
        self.onUpload()
        sshsftp.submit(cpu,calcid,processors,hours,memory)

        


        
        


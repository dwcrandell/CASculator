#!/usr/bin/python
# -*- coding: cp1252 -*-
'''
CASculator GUI Version 1.0
Graphical User Interface for Aiding Interpretation/Processing of
CASSCF Results Obtained With ORCA
Douglas Crandell-Indiana University-Bloomington, IN 47401
7/14/2014
'''

import wx
import casculator as cas
import general as gen
import servers
import rotate_orbs
import sqlite3 as lite
import os
import platform
import sshsftp
import base64
from decimal import *
from subprocess import Popen, PIPE, STDOUT

class MyApp(wx.App):
    def OnInit(self):
        dialog = MyDialog(None, -1, 'CASculator')
        dialog.ShowModal()
        dialog.Destroy()
        return True

class MyDialog(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title, size=(600,700), style=wx.DEFAULT_DIALOG_STYLE)
        self.status = 0
        self.p = ''
        self.threshold = 10
        
        hbox  = wx.BoxSizer(wx.HORIZONTAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        hbox7 = wx.BoxSizer(wx.HORIZONTAL)
        hbox8 = wx.BoxSizer(wx.HORIZONTAL)
        hbox9 = wx.BoxSizer(wx.HORIZONTAL)
        vbox1 = wx.BoxSizer(wx.VERTICAL)
        vbox2 = wx.BoxSizer(wx.VERTICAL)
        vbox3 = wx.BoxSizer(wx.VERTICAL)
        vbox4 = wx.BoxSizer(wx.VERTICAL)
        grid1 = wx.GridSizer(rows=5,cols=2,hgap = -70, vgap = -200)
        pnl1 = wx.Panel(self, -1, style=wx.SIMPLE_BORDER)
        pnl2 = wx.Panel(self, -1, style=wx.SIMPLE_BORDER)
        vbox1.Add(pnl1, 1, wx.EXPAND | wx.ALL, 3)
        vbox1.Add(pnl2, 1, wx.EXPAND | wx.ALL, 3)
        pnl1.SetSizer(vbox3)
        pnl2.SetSizer(vbox4)
        hbox.Add(vbox1, 1, wx.EXPAND)
        hbox.Add(vbox2, 1, wx.EXPAND)
        self.SetSizer(hbox)
        
        self.lc = wx.ListCtrl(self, 11, style=wx.LC_REPORT)
        self.lc.InsertColumn(0, 'Orbital')
        self.lc.InsertColumn(1, 'Occupation Number')
        self.lc.SetColumnWidth(0, 115)
        self.lc.SetColumnWidth(1, 140)
        vbox2.Add(self.lc, 1, wx.EXPAND | wx.ALL, 3)

        self.tc0 = wx.TextCtrl(pnl1,size=(310,20))
        self.tc1 = wx.TextCtrl(pnl1,size=(50,20))
        self.tc2 = wx.TextCtrl(pnl1,size=(50,20))
        self.tc3 = wx.TextCtrl(pnl1,size=(50,20))
        self.tc4 = wx.TextCtrl(pnl1,size=(50,20))
        self.tc5 = wx.TextCtrl(pnl1,size=(125,20))
        self.nel_tc = wx.TextCtrl(pnl1,size=(50,20))
        self.norb_tc = wx.TextCtrl(pnl1,size=(50,20))
        self.rangestart_tc = wx.TextCtrl(pnl1, size=(50,20))
        self.rangeend_tc = wx.TextCtrl(pnl1, size=(50,20))
        
        upload_image = wx.Image('images/upload_icon.jpg', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        download_image = wx.Image('images/download_icon.jpg', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        delete_image = wx.Image('images/delete_icon.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        open_image = wx.Image('images/open_folder_icon.jpg',wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.uploadButton = wx.BitmapButton(pnl1, 21, bitmap = upload_image, size=(upload_image.GetWidth()+5, upload_image.GetHeight()+5))
        self.downloadButton = wx.BitmapButton(pnl1, 22, bitmap = download_image, size=(download_image.GetWidth()+5, download_image.GetHeight()+5))
        self.deleteButton = wx.BitmapButton(pnl1, 23, bitmap = delete_image, size=(delete_image.GetWidth()+5, delete_image.GetHeight()+5))
        self.openButton = wx.BitmapButton(pnl1, 30, bitmap = open_image, size=(open_image.GetWidth()+5, open_image.GetHeight()+5))
        self.uploadButton.SetToolTipString('Upload to server')
        self.downloadButton.SetToolTipString('Download from server')
        self.deleteButton.SetToolTipString('Delete folder from server')
        self.openButton.SetToolTipString('Open folder')

        server_names = servers.getServerNames()
        self.computers = wx.ComboBox(pnl1,choices=server_names,style=wx.CB_READONLY)
        if len(server_names) > 0:
            self.computers.SetValue(server_names[0])
        self.tc1.SetValue('10.0')
        self.tc4.SetValue('0.05')

        self.units = wx.ComboBox(pnl1,24, value = 'kcal/mol',choices=['kcal/mol','eV','hartrees','kJ/mol'],style=wx.CB_READONLY)
        self.units.SetValue('kcal/mol')

        self.mulliken = wx.RadioButton(pnl2, 27, 'Mulliken', style=wx.RB_GROUP)
        self.loewdin = wx.RadioButton(pnl2, 28, 'Loewdin')

        hbox1.AddMany([(wx.StaticText(pnl1, -1, 'CAS Output File'), 0, wx.ALIGN_LEFT),
                                 (wx.Button(pnl1, 10, 'Browse...'),0, wx.ALIGN_LEFT|wx.LEFT,5),
                                 (self.uploadButton, 0, wx.ALIGN_LEFT|wx.LEFT,5),
                                 (self.downloadButton, 0, wx.ALIGN_LEFT|wx.LEFT, 5),
                                 (self.deleteButton, 0, wx.ALIGN_LEFT|wx.LEFT, 5),
                                 (self.openButton, 0, wx.ALIGN_LEFT|wx.LEFT, 5)])
        hbox2.AddMany([(self.nel_tc,0,wx.ALIGN_LEFT|wx.LEFT,5),
                       (wx.StaticText(pnl1, -1, 'active electrons in '), 0, wx.ALIGN_LEFT|wx.LEFT,5),
                       (self.norb_tc,0,wx.ALIGN_LEFT|wx.LEFT,5),
                       (wx.StaticText(pnl1, -1, 'in active orbitals'), 0, wx.ALIGN_LEFT|wx.LEFT, 5)])
        hbox3.AddMany([(wx.StaticText(pnl1, -1, 'Orbital % Threshold :'), 0, wx.ALIGN_LEFT),
                      (self.tc1,0,wx.ALIGN_LEFT|wx.LEFT,5)])
        hbox4.AddMany([(wx.StaticText(pnl1, -1, 'Element/Number :'), 0, wx.ALIGN_LEFT),
                      (self.tc2,0,wx.ALIGN_LEFT|wx.LEFT,5)])
        hbox5.AddMany([(wx.StaticText(pnl1, -1, 'Orbital Type :'), 0, wx.ALIGN_LEFT),
                      (self.tc3,0,wx.ALIGN_LEFT|wx.LEFT,5)])
        hbox6.AddMany([(wx.StaticText(pnl1, -1, 'Orbital Range :'), 0, wx.ALIGN_LEFT),
                      (self.rangestart_tc,0,wx.ALIGN_LEFT|wx.LEFT,5),
                       (wx.StaticText(pnl1, -1, '–'), 0, wx.ALIGN_LEFT|wx.LEFT,5),
                      (self.rangeend_tc,0,wx.ALIGN_LEFT|wx.LEFT,5)])
        hbox7.AddMany([(wx.StaticText(pnl1, -1, 'Isovalue :'), 0, wx.ALIGN_LEFT),
                      (self.tc4,0,wx.ALIGN_LEFT|wx.LEFT,5)])
        hbox8.AddMany([(wx.StaticText(pnl1, -1, 'Computer :'), 0, wx.ALIGN_LEFT|wx.TOP, 5),(self.computers, 1, wx.EXPAND | wx.ALL, 3)])
        hbox9.AddMany([(wx.StaticText(pnl1, -1, 'Single Point Energy'), 0, wx.ALIGN_LEFT|wx.LEFT, 5),
                      (self.tc5,0,wx.ALIGN_LEFT|wx.LEFT,5),
                      (self.units, 0, wx.ALIGN_LEFT|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)])
        vbox3.AddMany([(hbox1, 0, wx.ALIGN_LEFT|wx.LEFT, 5),
                       (self.tc0, 0, wx.ALIGN_LEFT|wx.ALIGN_TOP|wx.TOP, 5),
                       (hbox2, 0, wx.ALIGN_LEFT|wx.TOP|wx.LEFT, 5),
                       (hbox3, 0, wx.ALIGN_LEFT|wx.TOP|wx.LEFT, 5),
                       (hbox4, 0, wx.ALIGN_LEFT|wx.TOP|wx.LEFT, 5),
                       (hbox5, 0, wx.ALIGN_LEFT|wx.TOP|wx.LEFT, 5),
                       (hbox6, 0, wx.ALIGN_LEFT|wx.TOP|wx.LEFT, 5),
                       (hbox7, 0, wx.ALIGN_LEFT|wx.TOP|wx.LEFT, 5),
                       (hbox8, 0, wx.ALIGN_LEFT|wx.TOP|wx.LEFT, 5),
                       (hbox9, 0, wx.ALIGN_LEFT|wx.TOP, 55)])

        grid1.Add(wx.Button(pnl2, 15, 'Active Space'), 0, wx.ALIGN_CENTER|wx.TOP, 15)
        grid1.Add(wx.Button(pnl2, 16, 'Get Orbitals'), 0, wx.ALIGN_CENTER|wx.TOP, 15)
        grid1.Add(wx.Button(pnl2, 20, 'Plot Listed Orbitals'), 0, wx.ALIGN_CENTER|wx.TOP, 15)
        grid1.Add(wx.Button(pnl2, 17, 'Rotate Orbitals'), 0, wx.ALIGN_CENTER| wx.TOP, 15)
        grid1.Add(wx.Button(pnl2, 25, 'Spin Densities'), 0, wx.ALIGN_CENTER|wx.TOP, 15)
        grid1.Add(wx.Button(pnl2, 26, 'Atomic Charges'), 0, wx.ALIGN_CENTER|wx.TOP, 15)
        grid1.Add(self.mulliken, 0, wx.ALIGN_CENTER|wx.TOP,15)
        grid1.Add(self.loewdin, 0, wx.ALIGN_CENTER|wx.TOP,15)
        grid1.Add(wx.Button(pnl2, 19, 'Import Energy'), 0, wx.ALIGN_CENTER| wx.TOP, 15)
        grid1.Add(wx.Button(pnl2, 29, 'EEC'), 0, wx.ALIGN_CENTER| wx.TOP, 15)
        #grid1.Add(wx.Button(pnl2, 13, 'Clear'), 0, wx.ALIGN_CENTER| wx.TOP, 15)
        vbox4.Add(grid1, 1, wx.EXPAND|wx.TOP, -70)
        vbox4.Add(wx.Button(pnl2, 18, 'Servers'), 0, wx.ALIGN_LEFT|wx.TOP, -10)

        self.Bind(wx.EVT_BUTTON, self.onBrowse, id=10)
        self.Bind(wx.EVT_BUTTON, self.onClear, id=13)
        self.Bind(wx.EVT_BUTTON, self.onActive, id=15)
        self.Bind(wx.EVT_BUTTON, self.onComp, id=16)
        self.Bind(wx.EVT_BUTTON, self.onRotateOrbs, id=17)
        self.Bind(wx.EVT_BUTTON, self.onServers, id=18)
        self.Bind(wx.EVT_BUTTON, self.onImportSPE, id=19)
        self.Bind(wx.EVT_BUTTON, self.onPlotOrb, id=20)
        self.Bind(wx.EVT_BUTTON, self.onUpload, id=21)
        self.Bind(wx.EVT_BUTTON, self.onDownload, id=22)
        self.Bind(wx.EVT_BUTTON, self.onDelete, id=23)
        self.Bind(wx.EVT_BUTTON, self.onOpenFolder, id=30)
        self.Bind(wx.EVT_BUTTON, self.onSpin, id =25)
        self.Bind(wx.EVT_BUTTON, self.onCharge, id=26)
        self.Bind(wx.EVT_BUTTON, self.onEEC, id=29)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onViewOrb, id=11)
        self.Bind(wx.EVT_COMBOBOX, self.onImportSPE, id=24)
        

    def onClear(self, event):
        self.lc.DeleteAllItems()

    def onActive(self, event):
        self.lc.DeleteAllItems()
        if self.lc.GetColumnCount() == 3:
            self.lc.DeleteColumn(2)
        self.lc.DeleteColumn(0)
        self.lc.InsertColumn(0,'Orbital')
        self.lc.DeleteColumn(1)
        self.lc.InsertColumn(1,'Occupation Number')
        self.lc.SetColumnWidth(0, 115)
        self.lc.SetColumnWidth(1, 140)
        data = cas.open_file(self.tc0.GetValue())
        start, end, nel, norb = cas.get_active(data)
        num_items = self.lc.GetItemCount()
        LCO = cas.get_LCO(data)
        orb_dict = cas.create_OrbDict(LCO)
        for orbital in range(int(start),int(end)+1):
            self.lc.InsertStringItem(num_items, str(orbital))
            self.lc.SetStringItem(num_items,1,orb_dict[str(orbital)][1])
            num_items += 1

    def onSpin(self, event):
        mulliken, loewdin = cas.get_ChargeSpin(self.tc0.GetValue())
        self.lc.DeleteAllItems()
        if self.lc.GetColumnCount() == 3:
            self.lc.DeleteColumn(2)
        self.lc.DeleteColumn(1)
        self.lc.DeleteColumn(0)
        self.lc.InsertColumn(0,'Atom')
        self.lc.InsertColumn(1,'Spin')
        num_items = self.lc.GetItemCount()
        if self.mulliken.GetValue():
            charge_list = mulliken
        else:
            charge_list = loewdin
        for item in charge_list:
                item = item.split(':')
                atom = item[0]
                atom = filter(None,atom.split(' '))
                chargespin = filter(None,item[1].split(' '))
                atomstring = "%s%s " %(atom[1],atom[0])
                if self.tc2.GetValue() == '':
                    self.lc.InsertStringItem(num_items, atomstring)
                    self.lc.SetStringItem(num_items,1,str(chargespin[1]))
                    num_items +=1
                else:
                    if atomstring.strip() == self.tc2.GetValue():
                        self.lc.InsertStringItem(num_items, atomstring)
                        self.lc.SetStringItem(num_items,1,str(chargespin[1]))
                        num_items +=1

    def onCharge(self, event):
        mulliken, loewdin = cas.get_ChargeSpin(self.tc0.GetValue())
        self.lc.DeleteAllItems()
        if self.lc.GetColumnCount() == 3:
            self.lc.DeleteColumn(2)
        self.lc.DeleteColumn(1)
        self.lc.DeleteColumn(0)
        self.lc.InsertColumn(0,'Atom')
        self.lc.InsertColumn(1,'Atomic Charge')
        num_items = self.lc.GetItemCount()
        if self.mulliken.GetValue():
            charge_list = mulliken
        else:
            charge_list = loewdin
        for item in charge_list:
                item = item.split(':')
                atom = item[0]
                atom = filter(None,atom.split(' '))
                chargespin = filter(None,item[1].split(' '))
                atomstring = "%s%s " %(atom[1],atom[0])
                if self.tc2.GetValue() == '':
                    self.lc.InsertStringItem(num_items, atomstring)
                    self.lc.SetStringItem(num_items,1,str(chargespin[0]))
                    num_items +=1
                else:
                    if atomstring.strip() == self.tc2.GetValue():
                        self.lc.InsertStringItem(num_items, atomstring)
                        self.lc.SetStringItem(num_items,1,str(chargespin[0]))
                        num_items +=1

    def onEEC(self, event):
        atom = self.tc2.GetValue()
        orbital = self.tc3.GetValue()
        data = cas.open_file(self.tc0.GetValue())
        start, end, nel, norb = cas.get_active(data)
        LCO = cas.get_LCO(data)
        comp = cas.get_spec_orb(LCO,self.tc2.GetValue(),self.tc3.GetValue().lower(),Decimal('0.1'))
        orb_dict = cas.create_OrbDict(LCO)
        eec = 0
        active_eec = 0
        ordered = {}
        for k in comp.iterkeys():
            ordered[int(k)] = comp[k]
        ordered = sorted(ordered,key=lambda key: key)
        for orbital in ordered:
            percentage = comp[str(orbital)][0][1]
            occupation = orb_dict[str(orbital)][1]
            eec += Decimal(percentage) * Decimal(occupation)
            if orbital in range(int(start),int(end)+1):
                active_eec += Decimal(percentage) * Decimal(occupation)
        eec = round(eec/100,2)
        active_eec = round(active_eec/100,2)
        int_eec = eec-active_eec
        message = 'The effective electron count (EEC) is: %s\nThe internal EEC is: %s\nThe active EEC is: %s' %(str(eec),str(int_eec),str(active_eec))
        wx.MessageBox(message, 'Info', wx.OK | wx.ICON_INFORMATION)

    def onBrowse(self, event):
        browser = wx.FileDialog(None, "Choose a file", os.getcwd(), "", "*.out", wx.OPEN)
        if browser.ShowModal() == wx.ID_OK:
            self.tc0.SetValue(browser.GetPath())
            data = cas.open_file(browser.GetPath())
            start, end, nel, norb = cas.get_active(data)
            self.nel_tc.SetValue(nel)
            self.norb_tc.SetValue(norb)

    def onOpenFolder(self, event):
        folder = '\\'.join(self.tc0.GetValue().split('\\')[:-1]) +'\\'
        Popen('explorer ' + folder)

    def onUpload(self,event):
        host, path, user, passwd = sshsftp.getLogin(self.computers.GetValue())
        sftp = sshsftp.sftp_connect(host, path, user, passwd)
        ssh = sshsftp.ssh_connect(host, user, passwd)
        calcid = self.getCalcID()
        calcdir = path+calcid
        gbw_count = 0
        localdir = '\\'.join(self.tc0.GetValue().split('\\')[:-1])+ '\\'
        sftp.chdir(path)
        if calcdir not in sftp.listdir():
            try:
                sftp.mkdir(calcid)
            except IOError:
                pass
        else:
            sftp.chdir(calcdir)
        sftp.chdir(path + calcid)
        for name in os.listdir(localdir):
            localfile = localdir+name
            remotefile = path+calcid+'/'+name
            if name.endswith(".out") or name.endswith(".in"):
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
        wx.MessageBox('Upload Complete', 'Info', wx.OK | wx.ICON_INFORMATION)

    def onDownload(self,event):
        host, path, user, passwd = sshsftp.getLogin(self.computers.GetValue())
        sftp = sshsftp.sftp_connect(host, path, user, passwd)
        ssh = sshsftp.ssh_connect(host, user, passwd)
        calcid = self.getCalcID()
        calcdir = path+calcid
        gbw_count = 0
        localdir = '\\'.join(self.tc0.GetValue().split('\\')[:-1])+ '\\'
        sftp.chdir(path)
        if calcdir not in sftp.listdir():
            sftp.chdir(calcdir)
        for name in sftp.listdir():
            remotefile = path + calcid + '/'+ name
            localpath = '\\'.join(self.tc0.GetValue().split('\\')[:-1])+ '\\'
            localfile = localpath + name
            if not name.endswith('.gbw'):
                sftp.get(remotefile,localfile)
            else:
                gbw_count += 1
                with open('transfer.txt','a') as f:
                    if gbw_count == 1:
                        cmd = 'cd %s' %calcdir
                        cmd2 = '~/bin/unix2dos.sh'
                        stdin, stdout, stderr = ssh.exec_command(cmd+';'+cmd2)
                        f.write('option batch on\noption confirm off\n')
                        connect_string = 'open sftp://%s:%s@%s\n' %(user,passwd,host)
                        f.write(connect_string)
                    upld_string = 'get -transfer=ascii %s %s\n' %(remotefile, localfile)
                    f.write(upld_string)
        if os.path.isfile('transfer.txt'):
            os.system('winscp.exe /script=transfer.txt')
            os.remove('transfer.txt')
        wx.MessageBox('Download Complete', 'Info', wx.OK | wx.ICON_INFORMATION)

    def onDelete(self,event):
        host, path, user, passwd = sshsftp.getLogin(self.computers.GetValue())
        sftp = sshsftp.sftp_connect(host, path, user, passwd)
        calcid = self.getCalcID()
        calcdir = path+calcid
        files = sftp.listdir(calcdir)
        for name in files:
            filepath = calcdir + '/' + name
            try:
                sftp.remove(filepath)
            except IOError:
                self.onDelete(filepath)
        sftp.rmdir(calcdir)
        wx.MessageBox('Folder Deleted', 'Info', wx.OK | wx.ICON_INFORMATION)

    def onPlotOrb(self, event):
        orbs = ''
        orb_list = gen.getColumn(self.lc)
        host, path, user, passwd = sshsftp.getLogin(self.computers.GetValue())
        sftp = sshsftp.sftp_connect(host, path, user, passwd)
        ssh = sshsftp.ssh_connect(host, user, passwd)
        calcid = self.getCalcID()
        calcdir = path+calcid
        gbw_count = 0
        localdir = '\\'.join(self.tc0.GetValue().split('\\')[:-1])+ '\\'
        cmd1 = 'cd %s' %path + calcid
        sftp.chdir(path)
        if calcdir not in sftp.listdir():
            try:
                sftp.mkdir(calcid)
            except IOError:
                pass
        else:
            sftp.chdir(calcdir)
        sftp.chdir(path + calcid)
        for name in os.listdir(localdir):
            localfile = localdir+name
            remotefile = path+calcid+'/'+name
            if name.endswith(".out") or name.endswith(".in"):
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
        for orbital in orb_list:
            orbs += str(orbital) +' '
        cmd2 = 'cask %s -plot ' %calcid + orbs
        stdin, stdout, stderr = ssh.exec_command(cmd1 + ';' + cmd2)
        print stdout.readlines()
        for file_name in sftp.listdir():
            if not file_name.endswith(".gbw"):
                f = path + calcid + '/'+ file_name
                local = '\\'.join(self.tc0.GetValue().split('\\')[:-1])+ '\\' + file_name
                sftp.get(f,local)
        ssh.close()
        wx.MessageBox('Orbital Plotting Finished', 'Info', wx.OK | wx.ICON_INFORMATION)
        
    def onViewOrb(self, event):
        sys_type = platform.system()
        selected = gen.get_Selection(self.lc)
        orbital = self.lc.GetItemText(selected[0])
        basename = self.tc0.GetValue().split('/')[-1].split('.')[0]
        iso = self.tc4.GetValue()
        tu = (basename, orbital, iso)
        load_string = 'load {0}.xyz\n'.format(*tu)
        pos_iso = 'isoSurface pos {2} {0}.mo{1}a.cube\n'.format(*tu)
        neg_iso = 'isoSurface neg -{2} {0}.mo{1}a.cube\n'.format(*tu)
        with open('moplot.txt','w') as f:
            f.write(load_string)
            f.write(pos_iso)
            f.write(neg_iso)
            f.write('color $pos red\ncolor $neg blue\n')
        if self.status != 0:
            try:
                running = self.p.poll()
                if running == None:
                    self.p.stdin.write('script moplot.txtt\n')
                    self.p.stdin.close()
            except:
                print 'Problem exists with Jmol subprocess'
        if sys_type == 'Windows':
            self.p = Popen('jmol.jar -I -L -s moplot.txt', shell=True)
            self.status = 1
        else:
            self.p = Popen('java -jar Jmol.jar -I -L -s moplot.txt', shell=True, stdout=PIPE, stdin=PIPE)
            self.status = 1

    def onComp(self,event):
        self.lc.DeleteAllItems()
        num_items = self.lc.GetItemCount()
        if self.lc.GetColumnCount() == 3:
            self.lc.DeleteColumn(2)
        self.lc.DeleteColumn(0)
        self.lc.InsertColumn(0,'Orbital')
        self.lc.DeleteColumn(1)
        self.lc.InsertColumn(1,'Orbital Type')
        self.lc.InsertColumn(2,'Percentage')
        self.lc.SetColumnWidth(0, 95)
        self.lc.SetColumnWidth(1, 95)
        self.lc.SetColumnWidth(2, 95)
        data = cas.open_file(self.tc0.GetValue())
        self.threshold = Decimal(self.tc1.GetValue())
        self.rangestart = self.rangestart_tc.GetValue()
        self.rangeend = self.rangeend_tc.GetValue()
        LCO = cas.get_LCO(data)
        if self.tc2.GetValue() == '' and self.tc3.GetValue() == '' and self.rangestart == '' and self.rangeend == '':
            comp = cas.get_d_orbitals(LCO,self.threshold)
        elif self.rangestart != '' and self.rangeend != '':
            if isinstance(int(self.rangestart),int) and isinstance(int(self.rangeend),int):
                self.lc.DeleteAllItems()
                if self.lc.GetColumnCount() == 3:
                    self.lc.DeleteColumn(2)
                    self.lc.DeleteColumn(1)
                    self.lc.DeleteColumn(0)
                    self.lc.InsertColumn(0,'Orbital')
                    self.lc.InsertColumn(1,'Occupation Number')
                    self.lc.SetColumnWidth(0, 115)
                    self.lc.SetColumnWidth(1, 140)
                    data = cas.open_file(self.tc0.GetValue())
                    num_items = self.lc.GetItemCount()
                    LCO = cas.get_LCO(data)
                    orb_dict = cas.create_OrbDict(LCO)
                    for orbital in range(int(self.rangestart),int(self.rangeend)+1):
                        self.lc.InsertStringItem(num_items, str(orbital))
                        self.lc.SetStringItem(num_items,1,orb_dict[str(orbital)][1])
                        num_items += 1
        else:
            comp = cas.get_spec_orb(LCO,self.tc2.GetValue(),self.tc3.GetValue().lower(),self.threshold)
        ordered = {}
        if self.rangestart == '' and self.rangeend == '':
            for k in comp.iterkeys():
                ordered[int(k)] = comp[k]
            ordered = sorted(ordered,key=lambda key: key)
            for number in ordered:
                orbitals = comp[str(number)]
                for orb in orbitals:
                    self.lc.InsertStringItem(num_items,str(number))
                    self.lc.SetStringItem(num_items,1,orb[0])
                    self.lc.SetStringItem(num_items,2,orb[1])
                    num_items += 1

    def onRotateOrbs(self,event):
        dialog = rotate_orbs.RotateDialog(self,-1,'Rotate Orbitals')
        dialog.ShowModal()
        dialog.Destroy()
        return True

    def onImportSPE(self,event):
        spe = cas.get_SPE(self.tc0.GetValue())
        if self.units.GetValue() == 'kcal/mol':
            kcal = round(float(spe)*627.509,2)
            self.tc5.SetValue(str(kcal))
        elif self.units.GetValue() == 'eV':
            eV = round(float(spe)*27.21139611,3)
            self.tc5.SetValue(str(eV))
        elif self.units.GetValue() == 'hartrees':
            self.tc5.SetValue(str(round(float(spe),5)))
        elif self.units.GetValue() == 'kJ/mol':
            kJ = round(float(spe)*2625.50,2)
            self.tc5.SetValue(str(kJ))
            
    def onServers(self,event):
        dialog = servers.ServerDialog(self,-1,'Servers')
        dialog.ShowModal()
        dialog.Destroy()
        return True

    def getCalcID(self):
        return self.tc0.GetValue().split('.')[0].split("\\")[-1]

    def getLogin(self, computer):
        con = lite.connect('cas.sqlite')
        cursor = con.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS Servers(
	               id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,name TEXT,address TEXT,calcpath TEXT,user TEXT,password TEXT)""")
        con.commit()
        with con:
            cursor.execute("SELECT * FROM Servers")
            rows = cursor.fetchall()
            for row in rows:
                index = 0
                for item in row:
                    if item == computer:
                        host = row[index+1]
                        path = row[index+2]
                        user = row[index+3]
                        pwd = base64.b64decode(row[index+4])
                    index += 1
        return host, path, user, pwd

def main():
    app = MyApp()

if __name__ == "__main__":
    main()

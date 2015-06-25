#!/usr/bin/python
'''
SFTP/SSH Module for Casculator
'''

import paramiko
import sqlite3 as lite
import base64

def sftp_connect(host, path, user, passwd):
    port = 22
    transport = paramiko.Transport((host,port))
    transport.connect(username = user, password = passwd)
    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp

def ssh_connect(host, user, passwd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username = user, password = passwd)
    return ssh

def getLogin(computer):
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

def submit(computer, calcid, processors, hours, memory):
    host, path, user, passwd = getLogin(computer)
    ssh = ssh_connect(host,user, passwd)
    cmd1 = 'cd %s' %(path +'/' +calcid+'/')
    if computer == "Mason":
        cmd2 = 'msub %s %s %s %s orca' %(calcid,processors,memory, hours)
    else:
        cmd2 = 'jsub %s %s %s orca' %(calcid,processors,hours)
    ssh.exec_command(cmd1 +';' + cmd2)

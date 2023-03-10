import pyodbc
import os
con=pyodbc.connect('Driver={SQL Server};'
                   'SERVER=TRIEUAN\MASTERSQL;'
                   'Database=KhoaLuan;'
                   'Trusted_connection=yes')
cursor=con.cursor()
con.autocommit = True
cursor.execute(f"Use master; ALTER DATABASE KhoaLuan SET SINGLE_USER WITH ROLLBACK IMMEDIATE "
                               f"Use master; RESTORE DATABASE KhoaLuan FROM DISK = 'K:\###KhoaLuan\Data.bak' WITH REPLACE "
                               f"Use master; ALTER DATABASE KhoaLuan SET MULTI_USER WITH ROLLBACK IMMEDIATE")
while cursor.nextset():
    pass
cursor.execute("Use KhoaLuan ")
cursor.execute(f"select* from SINHVIEN Where MASV='2001190116' AND MATKHAU='123'")
data = cursor.fetchall()
print(data)
print("thành công")
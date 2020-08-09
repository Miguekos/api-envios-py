from datetime import datetime
tipo1 = "2020-04-27 12:41:46"
tipo1str = datetime.strptime("{}:23".format(tipo1), '%Y-%m-%d %H:%M:%S:%f')
print(tipo1str)
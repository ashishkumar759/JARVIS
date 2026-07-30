from tools.application_catalog import ApplicationCatalog

print(ApplicationCatalog.get_executable("notepad"))
print(ApplicationCatalog.get_executable("calculator"))
print(ApplicationCatalog.get_executable("calc"))
print(ApplicationCatalog.get_executable("unknown"))
ImportError: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).
Traceback:
File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/compat/_optional.py", line 158, in import_optional_dependency
    module = importlib.import_module(name)
File "/usr/local/lib/python3.14/importlib/__init__.py", line 88, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "<frozen importlib._bootstrap>", line 1406, in _gcd_import
File "<frozen importlib._bootstrap>", line 1371, in _find_and_load
File "<frozen importlib._bootstrap>", line 1335, in _find_and_load_unlocked
ModuleNotFoundError
The above exception was the direct cause of the following exception:
File "/mount/src/tac.py/tac.py", line 58, in <module>
    df_principal = pd.read_excel(archivo_principal)
File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/io/excel/_base.py", line 481, in read_excel
    io = ExcelFile(
        io,
    ...<2 lines>...
        engine_kwargs=engine_kwargs,
    )
File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/io/excel/_base.py", line 1621, in __init__
    self._reader = self._engines[engine](
                   ~~~~~~~~~~~~~~~~~~~~~^
        self._io,
        ^^^^^^^^^
        storage_options=storage_options,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        engine_kwargs=engine_kwargs,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/io/excel/_openpyxl.py", line 559, in __init__
    import_optional_dependency("openpyxl")
    ~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/compat/_optional.py", line 161, in import_optional_dependency
    raise ImportError(msg) from err

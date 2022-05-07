from distutils.core import setup
import py2exe
data_files =  ["assets"],


setup(

    windows=['main.py'],
    #data_files =  data_files,
    options={
                    "py2exe":{
                            "unbuffered": True,
                            "optimize": 2,
                            "includes": ["assets"],
                            "bundle_files":1
                    }
            }
)



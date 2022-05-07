from distutils.core import setup
import py2exe
data_files =  ["assets"]

data_files = [('assets', ['assets/fx13.wav','assets/fx16.wav','assets/fx22.wav'])]



setup(

    windows=['main.py'],
    #zipfile="pypong.zip",
    data_files =  data_files,
    options={
                    "py2exe":{
                            "unbuffered": True,
                            "optimize": 2,
                            "includes": ["assets"],
                            "bundle_files":1
                    }
            }
)



'''from distutils.core import setup
import py2exe
import os

# Get a list of all files in the Resources folder
resource_files = [os.path.join('Resources', f) for f in os.listdir('Resources')]

setup(
    name='ExamTrack',
    version='1.0',
    description='an innovative application designed to streamline the process of managing exams',
    windows=['StartingFrame.py'],
    # List of your main script(s) and other Python files
    scripts=['LandingFrame.py', 'UserInterface.py', 'StudentData.py', 'ReportFrames.py', 'ReportData.py',
                                                    'NotesFeature.py', 'ManualConfirmFeature.py', 'FirebaseManager.py',
                                                    'FaceRecFrame.py', 'ExamConfig.py', 'EncodePhotos.py', 'BreaksFeature.py'],
    # List of additional data files or folders (e.g., images, configuration files)
    data_files=[('Resources', resource_files),
                ('', ['serviceAccountKey.json'])]

)
'''


from cx_Freeze import setup, Executable

options = {
    "build_exe": {
        "include_files": ["Resources"],
    }
}

setup(
    name="ExamTrack",
    version="1.0",
    description="ExamTrack is an innovative application designed to streamline the process of managing exams",
    executables=[Executable("StartingFrame.py")],
    options={
        "build_exe": {
            "includes": ['LandingFrame', 'UserInterface', 'StudentData', 'ReportFrames', 'ReportData',
                         'NotesFeature', 'ManualConfirmFeature', 'FirebaseManager',
                         'FaceRecFrame', 'ExamConfig', 'EncodePhotos', 'BreaksFeature'],
            # List additional modules to include
            "packages": [],  # List additional packages to include
        }
    }
)

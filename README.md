You need to download python 3.9 and CMake for this to work.

The file is too big to keep here, https://drive.google.com/file/d/1sEOgc6TFbNA6kWenKjESa6dLPhAeGS1g/view?usp=sharing 
Use this link to access the cam project.

BEWARE! This project is VERY version sensitive!!!

If you get getting errors try this, commands are used in VS code terminal:
To see the current verison of libaries use "pip show *library name*", if
versions don't match do "pip uninstall *library name*" and install the correct version.

1) Must use winget, it's automatically included it windows 11
Command: winget install Microsoft.VisualStudio.2022.BuildTools --force --override "--passive --wait --add Microsoft.VisualStudio.Workload.VCTools;includeRecommended"
2) make sure dlib is 19.22
Command: pip install dlib==19.22
3) make sure numpy is 1.26.3
Command: pip install numpy==1.26.3
4) make sure opencv-python is 4.9.0.80
Command: pip install opencv-python==4.9.0.80
5) install face recognition
Command: pip install face_recognition

To run program do "python main.py"

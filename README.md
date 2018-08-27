# BetterLifePythonConsole
This is a simple GUI python console.
  
You can select a .py script to run via GUI.  
Also, you can save code snippet as a quick command button and click it to run.

How to use
==========
Just run main.py in your termnal, or double click the main.py file.
  
  
Add autorun scripts
===================
When the console starts, it search .py files with file names start with capital "S" in the autorun directory, by "glob" order. Yes, just like the  linux init.d scripts.  
So, if you need to add some scripts to run at startup, just put them in the auto run directory and rename them to start with "S" and two digitals, like "S03".  
There is something you may need to pay attention. All code  runs in the same scope, which means  that you can get access to objects defined in previous scripts. I write it this way on purpose, it's not a bug.

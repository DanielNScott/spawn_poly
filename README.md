This is a python-based replacement for spawn_poly.sh, which is more flexible and extensible.

Usage:
1) Make a folder in which to run a set of simulations
2) Put a link to spawn_poly.py in it
3) Put a link or an actual folder called "template" in it with the following contents...
   - A "template" ED2IN
   - A folder "analy"
   - A folder "hist"
4) Create or grab a joborder.txt file with format as below:

[beginning of file]
------------------------------------------------
Name         option1     option2  ... optionN
------------------------------------------------
some_sim        2011        2012            5
...
last_sim        2004        2015           -1
[end of file]

Where opiton1, option2, etc are eg NL%IYEARA, NL%IYEARZ etc.

5) Type "python spawn_poly.py" at the command line.

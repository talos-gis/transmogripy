import os
import sys
my_scripts_dir = r'd:\Scripts'
sys.path.append(my_scripts_dir)

from transmogripy import trans_dir

my_input_dir = os.path.join(my_scripts_dir, 'test1')
my_output_dir = os.path.join(my_scripts_dir, 'test2')
trans_dir.trans_dir(my_input_dir, my_output_dir)

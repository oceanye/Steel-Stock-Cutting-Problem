import argparse

#import argparse
#import tkinter as tk
#from tkinter import filedialog





parser = argparse.ArgumentParser(description='套料设置')
parser.add_argument('-l','--roll_length', type=int,help='整料长度')
parser.add_argument('-t','--roll_type', type=str,help='套料方式:opt_method,rank_roll')
args = parser.parse_args()


print(args.roll_type)
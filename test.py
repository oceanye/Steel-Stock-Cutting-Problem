import argparse

parse = argparse.ArgumentParser()
parse.add_argument('-t')
args = parse.parse_args()

print(args.t)
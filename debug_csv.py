with open('clock_ips.csv', 'r') as f:
    for i, line in enumerate(f.readlines()):
        print(f"Line {i}: {repr(line)}")
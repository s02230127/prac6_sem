import calendar

cal = calendar.month(2026, calendar.MARCH).split('\n')

print(f".. table:: {cal[0].strip()}\n")
print("    == == == == == == ==")
print(f"    {cal[1]}")
print("    == == == == == == ==")
line = [' ' + i for i in cal[2].split() if i]
line = ['\\ '] * (7 - len(line)) + line

print(f"    {' '.join(line)}")
for i in cal[3:]:
	if i:
		print(f"    {i}")
print(f"    == == == == == == ==")




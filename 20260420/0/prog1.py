def sqroots(coeffs:str) -> str:
	a, b, c = list(map(int, coeffs.split()))
	d = (b ** 2 - 4 * a * c)
	if d < 0:
		return ""
	elif d == 0:
		return str((-b + d ** 0.5) / ( 2 * a))
	else:
		mi, ma = sorted([(-b + d ** 0.5) / ( 2 * a), (-b - d ** 0.5) / ( 2 * a)])
		return f"{mi} {ma}"
	

	

#!/usr/bin/env python3

import gettext
import locale

locale = locale.setlocale(locale.LC_ALL, locale.getlocale())
translation = gettext.translation("prog", "po", fallback=True)
tolmach = gettext.translation("prog", "po", fallback=True)
ngettext, ngette = translation.gettext, tolmach.ngettext

words = input().split()
n = len(words)
print(ngettext("Entered {} word", "Entered {} words", n).format(n))
print(ngette("Entered {} word", "Entered {} words", n).format(n))

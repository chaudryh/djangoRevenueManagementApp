

class UString:

    @classmethod
    def str2float(cls, txt, ndigits=None):
        if txt:
            num = float(txt)
            if ndigits:
                num = round(num, ndigits=ndigits)
        else:
            num = None

        return num
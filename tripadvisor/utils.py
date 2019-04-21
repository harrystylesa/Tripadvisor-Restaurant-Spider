import re


class Util:
    def del_com(self, str):
        while 1:
            mm = re.search("\d,\d", str)
            if mm:
                mm = mm.group()
                str = str.replace(mm, mm.replace(",", ""))
                # print(review)
            else:
                break
        return str

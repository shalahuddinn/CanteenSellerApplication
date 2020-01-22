# Source:
# https://pemrograman-sederhana.blogspot.com/2014/09/membuat-format-rupiah-di-bahasa_33.html
# Accessed on March 4 2019
def formatRupiah(value):
    y = str(value)
    if len(y) <= 3:
        return 'Rp ' + y
    else:
        p = y[-3:]
        q = y[:-3]
        return formatRupiah(q) + '.' + p
        # print 'Rp ' + formatRupiah(q) + '.' + p


digits="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
logp_range="M500 M400 M300 M200 M100 M000 P000 P010 P020 P030 P040 P050 P060 P070 P080 P090 P100 P110 P120 P130 P140 P150 P160 P170 P180 P190 P200 P210 P220 P230 P240 P250 P260 P270 P280 P290 P300 P310 P320 P330 P340 P350 P360 P370 P380 P390 P400 P410 P420 P430 P440 P450 P460 P470 P480 P490 P500 P600 P700 P800 P900".split(" ")
#logp_range_rev={e:i for i, e in enumerate(logp_range)}
b62_table = [62**i for i in range(12)]
digits_map = { digit : i for i, digit in enumerate(digits) }
logp_range={e:i for i, e in enumerate(logp_range)}


def base62(n):
    b62_str=""
    while n >= 62:
        n, r = divmod(n, 62)
        b62_str += digits[r]
    b62_str += digits[n]
    return ''.join(reversed(b62_str))



import string
import sys

sub_id = sys.argv[1]
print(sub_id)
tranche = sys.argv[2]


b62_subid = base62(int(sub_id))
b62_h = base62(int(tranche[1:3]))
b62_p = base62(logp_range[tranche[3:]])
b62_subid = "0" * (10 - len(b62_subid)) + b62_subid
zinc_id = "ZINC"  + b62_h + b62_p + b62_subid


print(zinc_id)
import re

def correct_number_format(message):
    # This regular expression finds occurrences of a non-zero digit
    # followed by a dot and a digit sequence. It does not match if there
    # is already a zero before the dot.
    corrected_msg = re.sub(r'(?<!\d)(\.\d+)', r'0\1', message)
    return corrected_msg

msg = """SIGNAL ALERT

SELL NZDCAD 20223
🤑 TP1 .8190
🤑 TP2 .8163
🤑 TP3 .8124
🛑 SL .8240 (39 PIPS)"""

x= float(20223)
corrected_msg = correct_number_format(msg)
print(corrected_msg)
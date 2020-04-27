import sys
import json
import traceback
import random
#import pymurmur
import mmh3
from collections import defaultdict

'''
suffix notes
A: for train shitu log
B: statinfo
C: for train shitu instance
'''
class Item(object):
    def __init__(self):
        self.pv = 0
        self.click = 0

def newItem():
    return Item()

stat_info = defaultdict(newItem)
promotedapp_clktrans = defaultdict(newItem)
nowkey = ''
now_applist = ''
output_dict = {}
for line in sys.stdin:
    try:
        flds = line.strip().split('\t')
        key = flds[0].split('\002')[0]
        tag = flds[0].split('\002')[1]
        if tag in ['ins', 'applist']:
            if nowkey == '' or nowkey != key:
                nowkey = key
                now_applist = ''
                output_dict = {}
                if tag == 'applist':
                    now_applist = flds[1]
                    continue
            output_dict['fea'] = flds[1]
            output_dict['label'] = int(flds[2])
            output_dict['delay_time'] = flds[3] 
            if tag == 'ins':
                if now_applist != '':
                    output_dict['fea'] = "%s" % (' '.join([output_dict['fea'], now_applist]))
                #if random.random() > 0.1 and output_dict['label'] == 0:
                #    print "%s\t#C" % (json.dumps(output_dict))
                #else:
                #print "%s\t#A" % (json.dumps(output_dict))
                
                ins = [str(output_dict['label']), output_dict['delay_time']]
                for fea in output_dict['fea'].split():
                    fea_val = fea.split("\001")[1].strip()
                    ins.append(str(mmh3.hash(str(fea_val), signed=False)))
                print "%s" % (" ".join(ins))
    except Exception as e:
        sys.stderr.write("parse error:%s\n" % e)
        traceback.print_exc()
        pass

#for k,v in stat_info.iteritems():
#    if v.pv > 10:
#        print "%s\t%s\t%s\t%s#B" % (k, v.pv, v.click, (1.0*v.click)/v.pv)

#for k,v in promotedapp_clktrans.items():
#    if v.click > 100:
#        print "%s\t1.0#0.3#D" % (str(k).strip().lower())

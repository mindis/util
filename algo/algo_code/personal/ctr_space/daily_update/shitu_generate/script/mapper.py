import os
import sys
import json
import traceback
from collections import defaultdict
from datetime import datetime, date
sys.path.append('script')
import time

reload(sys)
sys.setdefaultencoding("utf-8")

UNK_FEA = 'unk'
EMPTY_FEA = ""
COMBINE_FEA_SEP = '_'
def get_hour(timestamp):
    try:
        return datetime.strptime(timestamp, "%Y%m%d%H%M%S").strftime("%H")
    except:
        return UNK_FEA 

def get_dayofweek(timestamp):
    try:
        return str(datetime.strptime(timestamp, "%Y%m%d%H%M%S").strftime("%w"))
    except:
        return UNK_FEA 

def get_isholiday(timestamp):
    try:
        wk = str(datetime.strptime(timestamp, "%Y%m%d%H%M%S").strftime("%w"))
        if wk in ['0', '6']:
            return '1'
        else:
            return '0'
    except:
        return UNK_FEA 

def get_iswifi(rawlog):
    if rawlog == '1':
        return '1'
    else:
        return '0'

def format_str(rawlog):
    if rawlog in ["", None]:
        rawlog = UNK_FEA
    return str(rawlog).strip().lower().replace(' ', '#')

def concat_str(str1, str2):
    return "%s_%s" % (str1, str2)

def parse_app_db(path):
    app_dict = {}
    for line in open(path).readlines():
        flds = line.strip().split('\t')
        if len(flds) != 2:
            continue
        pkg = flds[0]
        pkgsize = flds[1].split('#')[0]
        pkgtrade = '#'.join(flds[1].split('#')[1:])
        app_dict[flds[0]] = (pkgsize, pkgtrade)
    return app_dict

class Item(object):
    def __init__(self):
        self.pv = 0
        self.click = 0

def newItem():
    return Item()

def parse_ad_info(path):
    ad_dict = {}
    for line in open(path).readlines():
        flds = line.strip().split('\t')
        if len(flds) != 3:
            continue
        adid = format_str(flds[0])
        ad_level = flds[1]
        industry = flds[2]
        ad_dict[adid] = (ad_level, industry)
    return ad_dict
ad_dict = parse_ad_info('./script/ad_info')

stat_info = defaultdict(newItem)
fea_suffix_dict = {}
for line in open('./script/features.list').readlines():
    if line[0] == '#':
        continue
    flds = line.strip("\n\r ").split('\t')
    fea_name = flds[0]
    fea_code = flds[1]
    fea_suffix_dict[fea_name] = fea_code

#dict((line.strip().split('\t')[0], line.strip().split('\t')[1]) for line in open('./script/features.list').readlines())
app_dict = parse_app_db('./script/app_db.dat')
#if len(sys.argv) == 2:
#    tag = sys.argv[1]
#else:
#    input_hdfs = os.environ["mapreduce_map_input_file"]
#    if input_hdfs.split("/")[-3] == "applist":
#        tag = 'applist'
#    else:
#        tag = 'shitu'
tag = 'shitu'

for line in sys.stdin:
    try:
        line = line.strip('\r\n')
        ld = json.loads(line)
        
        """
        if tag == 'applist':
            gaid = ld['gaid']
            applist = ld['applist']
            applist_lst =[]
            for app in applist:
                val = "applist:%s:%s" % (fea_suffix_dict['applist'], app)
                applist_lst.append(str(hashstr(val)))
            #print "%s#applist\t%s" % (gaid, ' '.join(applist_lst))
            print "%s#applist\t%s" % (gaid, ' '.join("applist:%s:%s" % (fea_suffix_dict['applist'], iter) for iter in  applist))
            continue
        """
        fea_dict = defaultdict(lambda:'unk')
        try:
            if not isinstance(ld['ed_log'], dict):
                ed_log = json.loads(ld['ed_log'])
            else:
                ed_log = ld['ed_log']
        except Exception as e:
            print e
            continue
        plid = format_str(ed_log.get('plid', UNK_FEA))
       
        ad_style = ed_log.get("ad_style", "")
        if ad_style == "6" or ad_style == "%06" or ad_style == "8":
            continue
        if 'reqprt' not in ed_log:
            continue 
        timestamp = time.strftime('%Y%m%d%H%M%S', 
            time.localtime(float(str(ed_log['reqprt'])[:10])))
        fea_dict['date'] = timestamp[0:8]
        fea_dict['timestamp'] = timestamp 
        #user features
        if 'ifa' in ed_log:
            ifa = ed_log['ifa']
        else:
            ifa = UNK_FEA
        
        fea_dict['ifa'] = ifa
        fea_dict['did'] = format_str(ed_log.get('did', UNK_FEA))
        fea_dict['hour'] = get_hour(timestamp)
        fea_dict['wk'] = get_dayofweek(timestamp)
        fea_dict['daytp'] = get_isholiday(timestamp)
        fea_dict['operator'] = format_str(ed_log.get('operator', UNK_FEA))
        fea_dict['make'] = format_str(ed_log.get('make', UNK_FEA))
        fea_dict['model'] = format_str(ed_log.get('model', UNK_FEA))
        nt = ed_log.get('nt', UNK_FEA)
        fea_dict['nt'] = nt
        fea_dict['is_wifi'] = format_str(get_iswifi(nt))
        fea_dict['city'] = format_str(ed_log.get('city_id', UNK_FEA))
        fea_dict['dev_type'] = format_str(ed_log.get('dt', UNK_FEA))
        fea_dict['le'] = format_str(ed_log.get('le', UNK_FEA))
        fea_dict['osv'] = format_str(ed_log.get('osv', UNK_FEA))
        fea_dict['os'] = format_str(ed_log.get('os', UNK_FEA))
        #applist_len = ed_log.get('applist_len', UNK_FEA)
        #applist_len = UNK_FEA if applist_len == '0' else applist_len
        #if applist_len != UNK_FEA:
        #    applist_len = int(int(applist_len)/5)
        #fea_dict['applist_len'] = format_str(applist_len)

        #app feature
        fea_dict['plid'] = format_str(ed_log.get('plid', UNK_FEA)) 
        fea_dict['reqtype'] = format_str(ed_log.get('reqtype', UNK_FEA))
        fea_dict['appid'] = format_str(ed_log.get('appid', UNK_FEA))
        fea_dict['pw'] = format_str(ed_log.get('pw', UNK_FEA))
        fea_dict['ph'] = format_str(ed_log.get('ph', UNK_FEA))
        fea_dict['instl'] = format_str(ed_log.get('instl', UNK_FEA))
        fea_dict['traffic_source'] = format_str(ed_log.get('traffic_source', UNK_FEA))
        fea_dict['launch_type'] = format_str(ed_log.get('lan_t', UNK_FEA))

        #ad featyre
        fea_dict['adid'] = format_str(ed_log.get('adid', UNK_FEA)) 
        fea_dict['adstyle'] = format_str(ed_log.get('ad_style', UNK_FEA))
        pkg = format_str(ed_log.get('promoted_app', UNK_FEA))
        fea_dict['promoted_app'] = pkg
        if pkg in app_dict:
            pkg_size = app_dict[pkg][0]
            pkg_trade = app_dict[pkg][1]
            if pkg_trade not in ['unk', '-', None]:
                fea_dict['pkg_trade'] = pkg_trade
            if pkg_size not in ['unk', '-', None]:
                fea_dict['pkg_size'] = pkg_size
        else:
            fea_dict['pkg_trade'] = UNK_FEA
            fea_dict['pkg_size'] = UNK_FEA
        fea_dict['adw'] = format_str(ed_log.get('adw', UNK_FEA))
        fea_dict['adh'] = format_str(ed_log.get('adh', UNK_FEA))
        fea_dict['planid'] = format_str(ed_log.get('planid', UNK_FEA))
        fea_dict['cmpid'] = format_str(ed_log.get('campaignid', UNK_FEA))
        fea_dict['orgid'] = format_str(ed_log.get('orgid', UNK_FEA))
        
        #combined feature 
        fea_dict['adwh'] = concat_str(fea_dict['adw'], fea_dict['adh'])
        fea_dict['adwh_promotedapp'] = concat_str(fea_dict['adw'], concat_str(fea_dict['adh'], fea_dict['promoted_app']))
        fea_dict['adwh_pwh'] = concat_str(concat_str(fea_dict['adw'], fea_dict['adh']), concat_str(fea_dict['pw'], fea_dict['ph']))
        fea_dict['pwh'] = concat_str(fea_dict['pw'], fea_dict['ph'])
        fea_dict['pwh_appid'] = concat_str(concat_str(fea_dict['pw'], fea_dict['ph']), fea_dict['appid'])
        fea_dict['pwh_plid'] = concat_str(concat_str(fea_dict['pw'], fea_dict['ph']), fea_dict['plid'])
        fea_dict['pwh_promotedapp'] = concat_str(concat_str(fea_dict['pw'], fea_dict['ph']), fea_dict['promoted_app'])
 
        fea_dict['make_model'] = concat_str(fea_dict['make'], fea_dict['model'])
        fea_dict['make_model_appid'] = concat_str(concat_str(fea_dict['make'], fea_dict['model']), fea_dict['appid'])
        fea_dict['make_model_plid'] = concat_str(concat_str(fea_dict['make'], fea_dict['model']), fea_dict['plid'])
        fea_dict['make_model_promotedapp'] = concat_str(concat_str(fea_dict['make'], fea_dict['model']), fea_dict['promoted_app'])
        fea_dict['make_model_adid'] = concat_str(concat_str(fea_dict['make'], fea_dict['model']), fea_dict['adid'])
        
        fea_dict['make_appid'] = concat_str(fea_dict['make'], fea_dict['appid'])
        fea_dict['make_plid'] = concat_str(fea_dict['make'], fea_dict['plid'])
        fea_dict['make_adid'] = concat_str(fea_dict['make'], fea_dict['adid'])
        fea_dict['make_planid'] = concat_str(fea_dict['make'], fea_dict['planid'])
        fea_dict['make_cmpid'] = concat_str(fea_dict['make'], fea_dict['cmpid'])
        fea_dict['make_orgid'] = concat_str(fea_dict['make'], fea_dict['orgid'])

        fea_dict['plid_osv'] = concat_str(fea_dict['plid'], fea_dict['osv'])
        fea_dict['adid_osv'] = concat_str(fea_dict['adid'], fea_dict['osv'])
        fea_dict['appid_osv'] = concat_str(fea_dict['appid'], fea_dict['osv'])

        fea_dict['appid_promotedapp'] = concat_str(fea_dict['appid'], fea_dict['promoted_app'])
        fea_dict['appid_planid'] = concat_str(fea_dict['appid'], fea_dict['planid'])
        fea_dict['appid_cmpid'] = concat_str(fea_dict['appid'], fea_dict['cmpid'])
        fea_dict['appid_hour'] = concat_str(fea_dict['appid'], fea_dict['hour'])
        fea_dict['appid_wk'] = concat_str(fea_dict['appid'], fea_dict['wk'])
        fea_dict['appid_adid'] = concat_str(fea_dict['appid'], fea_dict['adid'])
        fea_dict['appid_orgid'] = concat_str(fea_dict['appid'], fea_dict['orgid'])

        fea_dict['plid_hour'] = concat_str(fea_dict['plid'], fea_dict['hour'])
        fea_dict['plid_wk'] = concat_str(fea_dict['plid'], fea_dict['wk'])
        fea_dict['plid_adid'] = concat_str(fea_dict['plid'], fea_dict['adid'])
        fea_dict['plid_planid'] = concat_str(fea_dict['plid'], fea_dict['planid'])
        fea_dict['plid_cmpid'] = concat_str(fea_dict['plid'], fea_dict['cmpid'])
        fea_dict['plid_promotedapp'] = concat_str(fea_dict['plid'], fea_dict['promoted_app'])
        
        fea_dict['wk_promotedapp'] = concat_str(fea_dict['wk'], fea_dict['promoted_app'])
        fea_dict['hour_promotedapp'] = concat_str(fea_dict['hour'], fea_dict['promoted_app'])
        fea_dict['hour_wk'] = concat_str(fea_dict['hour'], fea_dict['wk'])
        fea_dict['adid_wk'] = concat_str(fea_dict['adid'], fea_dict['wk'])
        fea_dict['adid_hour'] = concat_str(fea_dict['adid'], fea_dict['hour'])
        fea_dict['dt_adid'] = concat_str(fea_dict['dev_type'], fea_dict['adid'])
        fea_dict['city_adid'] = concat_str(fea_dict['city'], fea_dict['adid'])
        fea_dict['city_plid'] = concat_str(fea_dict['city'], fea_dict['plid'])
        fea_dict['city_appid'] = concat_str(fea_dict['city'], fea_dict['appid'])
        fea_dict['iswifi_adid'] = concat_str(fea_dict['is_wifi'], fea_dict['adid'])
        fea_dict['iswifi_promotedapp'] = concat_str(fea_dict['is_wifi'], fea_dict['promoted_app'])
        fea_dict['nt_adid'] = concat_str(fea_dict['nt'], fea_dict['adid'])
        fea_dict['nt_plid'] = concat_str(fea_dict['nt'], fea_dict['plid'])
        fea_dict['orgid_wk'] = concat_str(fea_dict['orgid'], fea_dict['wk'])
        fea_dict['orgid_plid'] = concat_str(fea_dict['orgid'], fea_dict['plid'])
        fea_dict['orgid_hour'] = concat_str(fea_dict['orgid'], fea_dict['hour'])
        fea_dict['orgid_iswifi'] = concat_str(fea_dict['orgid'], fea_dict['is_wifi'])

        if fea_dict['adid'] in ad_dict:
            (ad_level, industry) = ad_dict[fea_dict['adid']]
            fea_dict['ad_level'] = ad_level
            fea_dict['industry'] = industry
        fea_dict['app_series'] = format_str(ed_log.get('app_series', UNK_FEA))
        fea_dict['adstyle'] = format_str(ed_log.get('ad_style', UNK_FEA))
        user_frequency = ed_log.get('user_frequency', UNK_FEA)
        freq = user_frequency.strip().split('_')
        if len(freq) == 4:
            fea_dict['week_ed'] = concat_str(industry, freq[0])
            fea_dict['week_clk'] = concat_str(industry, freq[1])
            fea_dict['day_ed'] = concat_str(industry, freq[2])
            fea_dict['day_clk'] = concat_str(industry, freq[3])
        else:
            fea_dict['week_ed'] = concat_str(industry, '0')
            fea_dict['week_clk'] = concat_str(industry, '0')
            fea_dict['day_ed'] = concat_str(industry, '0')
            fea_dict['day_clk'] = concat_str(industry, '0')
            

        user_edclk = ed_log.get('user_edclk', '') 
        if user_edclk == '': 
            continue
        ed, clk = user_edclk.split('_')
        isnewuser = 1
        if int(ed) >= 10:
            isnewuser = 0 
        elif int(ed) == -1:
            isnewuser = -1
        fea_dict['isnewuser'] = str(isnewuser)
        
        user_adfreq = "-1"
        if int(ed) < 0 and int(clk) < 0:
            user_adfreq = "-1"
        elif int(ed) == 0 and int(clk) == 0:
            user_adfreq = "0"
        elif int(ed) > 0 and int(clk) == 0:
            user_adfreq = "1"
        elif int(ed) > 0 and int(clk) > 0 and int(clk) <= 5:
            user_adfreq = "2"
        elif int(ed) > 0 and int(clk) > 5:
            user_adfreq = "3"

        if int(ed) > 200:
            user_ctr = int(clk)*1.0 / int(ed)
            fea_dict['user_edclk'] = '%s_%s' % (int(user_ctr*200), 200)
        else:
            fea_dict['user_edclk'] = '%s_%s' % (int(clk), int(ed))

        fea_dict['user_adfreq'] = user_adfreq
        fea_dict['appseries_industry'] = concat_str(fea_dict['app_series'], fea_dict['industry'])

        if 'fac_ts' not in ed_log or 'reqprt' not in ed_log:
            continue
        if ed_log['fac_ts'] == '' or ed_log['reqprt'] == '': 
            continue 

        fac_ts = int(ed_log['fac_ts'])
        prt = int(int(ed_log['reqprt'])*1.0/1000)
        if fac_ts == 0:
            user_act = -1
        else:
            user_act = int((prt - fac_ts)*1.0/(60*60))
        if user_act > 48: 
            user_act = 48
        fea_dict['user_act_time'] = user_act
   
        #user_plan_edfreq = int(ed_log.get('user_plan_edfreq', "0"))
        #if user_plan_edfreq > 10: 
        #    user_plan_edfreq = 10
        #fea_dict['user_plan_edfreq'] = user_plan_edfreq

        fea_dict['useracttime_planid'] = concat_str(fea_dict['user_act_time'], fea_dict['planid'])
        fea_dict['useracttime_adstyle'] = concat_str(fea_dict['user_act_time'], fea_dict['adstyle'])

        click  = 1 if 'click_log' in ld else 0
        ins_encode_list = []

        for fea in fea_suffix_dict:
            if fea not in fea_dict:
                print "Warning: %s segment not in fea_dict" % fea
                continue
            suffix = fea_suffix_dict[fea]
            v = fea_dict[fea]
            value = "%s\001%s:%s" % (fea, suffix, v)
            ins_encode_list.append(value)
            item = stat_info[value]
            item.pv += 1
            item.click += click
        ins_encode_list.append("%s\001%s" % ('beta0', '9999:1'))
        print "%s\002ins\t%s\t%s" % (fea_dict['ifa'], ' '.join(str(x) for x in ins_encode_list), str(click))
    except Exception as e:
        sys.stderr.write("parse log failed, err_msg[%s]\n" % (e))
        traceback.print_exc()
        pass

for k,v in stat_info.iteritems():
    print "%s\002stat\t%s\t%s" % (k, v.pv, v.click)
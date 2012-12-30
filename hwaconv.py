# -*- coding: utf-8 -*-

import codecs
import collections


import re
import string
import struct
import sys

class Rec:
    def __init__(self, name, rtype, length= 0, len_idx=0, children=None):
        self.name = name
        self.rtype = rtype
        self.length = length
        self.children = ([] if children is None else children)

        self.bytes = None

    def read(self, f):
        print self.name
        if self.rtype == 'd':
            return f.read(self.length)
        elif self.rtype == 's':
            if [0xFF, 0xFE, 0xFF] != [ord(x) for x in f.read(3)]:
                raise Exception("invalid string")
            self.length = ord(f.read(1))
            if self.length == 0:
                return u""
            else:
                bytes = f.read(self.length * 2)
                return unicode(bytes, encoding='utf-16le')

        elif self.rtype == 'i':
            bytes = f.read(4)
            return str(struct.unpack('i', bytes)[0])

        elif self.rtype == 'bl':
            bytes = f.read(self.length)
            return str([ord(x) for x in bytes])

        elif self.rtype == 'bh':
            bytes = f.read(self.length)
            (rec_size,) = struct.unpack('i', bytes)
            print rec_size

            children_list = []
            for i in range(rec_size):
                myattr = collections.OrderedDict()
                for (ci, child) in enumerate(self.children):
                    myattr[child.name] = child.read(f)
                children_list.append(myattr)
            return children_list

        elif self.rtype == 'cu':    #special logic
            f.read(4)
            bit = ord(f.read(1))
            if bit == 0x00:
                f.read(69)
            elif bit == 0x07:
                f.read(73)
            elif bit == 0x09:
                f.read(5)
                self.length = struct.unpack('i', f.read(4))[0]
                text =  unicode(f.read(self.length), encoding='utf-16le')
                f.read(14)
                self.length = struct.unpack('i', f.read(4))[0]
                text = unicode(f.read(self.length), encoding='utf-16le')
                f.read(54)
            return None
        else:
            raise Exception("invalid read type" + str(self.rtype))



table = [
     Rec('header', 'd', 0x1e)
    ,Rec('unknown', 's')
    ,Rec('grp_header', 'bh', length = 4,  children=[
            Rec('group_index', 'i', length=4)
            ,Rec('group', 's')
        ]
    )
    ,Rec('from_header', 'bh', length = 4,   children=[
        Rec('from_index', 'i', length=4)
        ,Rec('from_title', 's')
        ,Rec('from_name', 's')
        ,Rec('unknown', 's')
        ,Rec('from_zip', 's')
        ,Rec('from_addr1', 's')
        ,Rec('from_addr2', 's')
        ,Rec('from_info_header', 'bh', length=4,  children=[
            Rec('from_info_title', 's')
            ,Rec('from_info_val', 's')
        ])
        ,Rec('from_family_header', 'bh', length=4, children=[
            Rec('from_family_name', 's')
            ,Rec('unknown', 's')
            ,Rec('unknown_bit', 'bl', length=4)
        ])
        ,Rec('unknown', 's')
        ,Rec('unknown', 's')
        ,Rec('unknown', 's')
        ,Rec('unknown', 'bl', length=4)
        ,Rec('tag_header', 'bh', length=4,  children=[
            Rec('tag_index', 'i', length=4)
            ,Rec('tag_name', 's')
            ,Rec('cond_unknown', 'cu')
        ])
    ])
    ,Rec('addr_header', 'bh', length = 4,   children=[
        Rec('name', 's')
        ,Rec('kana', 's')
        ,Rec('keishou', 's')
        ,Rec('unknown', 's')
        ,Rec('unknown', 'bl', length=44)
        ,Rec('zip', 's')
        ,Rec('addr1', 's')
        ,Rec('addr2', 's')
        ,Rec('unknown1', 's')
        ,Rec('unknown2', 's')
        ,Rec('unknown3', 's')
        ,Rec('unknown4', 's')
        ,Rec('unknown5', 's')
        ,Rec('unknown6', 's')
        ,Rec('unknown7', 's')
        ,Rec('unknown8', 's')
        ,Rec('unknown9', 's')
        ,Rec('unknown10', 's')
        ,Rec('unknown11', 's')
        ,Rec('unknown12', 's')
        ,Rec('unknown13', 's')
        ,Rec('unknown14', 's')
        ,Rec('unknown15', 's')
        ,Rec('unknown16', 's')
        ,Rec('unknown17', 's')
        ,Rec('unknown18', 's')
        ,Rec('unknown19', 's')
        ,Rec('unknown20', 's')
        ,Rec('to_family_header', 'bh', length=4, children=[
            Rec('fam_name', 's')
            ,Rec('fam_kana', 's')
            ,Rec('unknown', 's')
            ,Rec('fam_keishou', 's')
            ,Rec('unknown', 'i')
            ,Rec('unknown', 'bl', length=4)
            ,Rec('unknown', 's')
            ,Rec('unknown', 'bl', length=16)
            ,Rec('unknown', 's')
            ,Rec('unknown', 's')
        ])
        ,Rec('unknown21', 'bl', length=24)
    ])
]



def create_output_dict(addr):
    ret = dict(addr)

    ret['pref'] = get_pref(addr['addr1'])
    if ret['pref']!= u'':
        ret['addr1'] = ret['addr1'][len(ret['pref']):]

    match = re.search(u'^(.*?[区市])(.*)$', ret['addr1'])
    ret['shichou'] = u""
    if match:
        ret['shichou'] = match.group(1)
        ret['addr1'] = match.group(2)

    names = re.split(u' |\u3000', ret['name'])
    names = names + [u'' for x in range(2-len(names))]
    kanas = re.split(u' |\u3000', ret['kana'])
    kanas = kanas + [u'' for x in range(2-len(kanas))]

    ret['sei'] = names[0]
    ret['mei'] = names[1]
    ret['kana_sei'] = kanas[0]
    ret['kana_mei'] = kanas[1]

    return ret


def get_pref(s):
    prefs = [u"北海道",u"青森県",u"岩手県",u"宮城県",u"秋田県",u"山形県",u"福島県",u"茨城県",u"栃木県",u"群馬県",u"埼玉県",
             u"千葉県",u"東京都",u"神奈川県",u"新潟県",u"富山県",u"石川県",u"福井県",u"山梨県",u"長野県",u"岐阜県",u"静岡県",
             u"愛知県",u"三重県",u"滋賀県",u"京都府",u"大阪府",u"兵庫県",u"奈良県",u"和歌山県",u"鳥取県",u"島根県",u"岡山県",
             u"広島県",u"山口県",u"徳島県",u"香川県",u"愛媛県",u"高知県",u"福岡県",u"佐賀県",u"長崎県",u"熊本県",u"大分県",
             u"宮崎県",u"鹿児島県",u"沖縄県"]

    for p in prefs:
        if s.find(p) == 0:
            return p

    return u''


def main():
    if len(sys.argv) < 2:
        print "please set hwa file parameter"
        exit(-1)
        return

    data = collections.OrderedDict()
    with open(sys.argv[1], 'rb') as f:
        for rec in table:
            data[rec.name] = rec.read(f)


    encoding = "cp932"

    with codecs.open('output.csv', 'w', encoding) as out:
        tmpl = string.Template(
            '${sei}\t${mei}\t${kana_sei}\t${kana_mei}\t${name}\t${kana}'    #名前系
            + '\t${zip}\t${pref}\t${shichou}\t${addr1}\t${addr2}'           #住所系
            + '\t\t\t\t\t\t\t\t\t${keishou}'    #会社系
        )
        fam_tmpl = string.Template('\t${fam_name}\t${fam_keishou}')

        for addr in data['addr_header']:
            out.write(tmpl.substitute(create_output_dict(addr)))

            for frec in addr['to_family_header']:
                out.write(fam_tmpl.substitute(frec))
                for x in range(3-len(addr['to_family_header'])):
                    out.write("\t\t")    #足りない分を埋める

            out.write('\r\n')

if __name__ == '__main__':
    main()
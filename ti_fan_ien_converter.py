import re
from collections import defaultdict
import tae_rv_ipa

def parse_pien_ien(ien):
  m_match = re.match(r"^m(\d|)$", ien)
  if m_match:
    return ['m', '', '', m_match.group(1)]
  match = re.match(r"^([bpmfvdtnlzcsjqxrgkh]|zh|ch|sh|ng|)(i|u|y|)([aeiouvyzr][a-z]*)(\d|)$", ien)
  if match is None:
    raise Exception(f"Unrecogonized ien: {ien}")
  g = match.groups()
  if g[1] == 'i' and g[2] == 'i':
    return [g[0], '', 'ii', g[3]]
  return g

class keydefaultdict(defaultdict):
  def __missing__(self, key):
    if self.default_factory is None:
      raise KeyError(key)
    else:
      ret = self[key] = self.default_factory(key)
      return ret

pien_shih = keydefaultdict(lambda k: k)
pien_shih['zh'] = 'z'
pien_shih['ch'] = 'c'
pien_shih['sh'] = 's'

ngah_hua = keydefaultdict(lambda k: k)
ngah_hua['z'] = 'j'
ngah_hua['c'] = 'q'
ngah_hua['s'] = 'x'
ngah_hua['zh'] = 'j'
ngah_hua['ch'] = 'q'
ngah_hua['sh'] = 'x'
ngah_hua['d'] = 'j'
ngah_hua['t'] = 'q'

shih_jin_hua = keydefaultdict(lambda k: k)
shih_jin_hua['j'] = 'z'
shih_jin_hua['q'] = 'c'
shih_jin_hua['x'] = 's'

def 泰兴(cz, pien_ien):
  ien = parse_pien_ien(pien_ien)
  shen, gae, yen, tio = tae_xien_pien_ien(cz, ien)

  if shen in ['', 'f'] and yen == 'v':
    result = shen + 'ʋ'
  elif gae == 'i' and yen == 'en':
    result = tae_rv_ipa.tae_rv_ipa_shen[shen] + 'iŋ'
  else:
    ipa_yen = tae_rv_ipa.tae_rv_ipa_yen.copy()
    ipa_yen['an'] = 'ɑŋ'
    ipa_yen['v'] = 'u'
    result = tae_rv_ipa.tae_rv_ipa_shen[shen] + tae_rv_ipa.tae_rv_ipa_gae[gae] + ipa_yen[yen]

  result = result + tio
  return result

def tae_xien_pien_ien(cz, ien, for_qio_shih = False):
  shen, gae, yen, tio = ien
  if tio == '6': # 阳去并入阴平
    tio = '1'
  if cz in '蛆取趣娶趋聚徐咀' and shen in ['j', 'q', 'x'] and yen == 'y': # 遇摄分尖团
    shen = shih_jin_hua[shen]
    gae = 'u'
    yen = 'ei'
  elif cz in '皱邹绉诌骤瘦愁': # 流摄庄三归精组。泰兴城部分人或部分词“愁”读qiou，顾黔亦有记录。从音系整齐度出发，不采纳。
    shen = pien_shih[shen]
    yen = 'ou'
  elif shen in ['zh', 'ch', 'sh'] and yen == 'eu': # 流摄翘舌转舌面
    shen = ngah_hua[shen]
    gae = 'i'
    yen = 'ou'
  elif shen in ['d', 't', 'n', 'l', 'g', 'k', 'h', 'ng'] and yen == 'eu': # 流摄转ei
    gae = ''
    yen = 'ei'
  elif yen == 'u': # 果摄转ou
    yen = 'ou'
  elif yen == 'eu': # 未转ei的eu，也书写为ou。韵母格局与普通泰如不同，区别书写。
    yen = 'ou'
  elif shen == 'n' and yen == 'v': # nv -> nu
    yen = 'ou'
  elif shen == 'l' and yen == 'i' and for_qio_shih: # 翘舌话 li -> i
    shen = ''
  elif gae == 'i' and yen == 'eh' and cz not in '吃七漆' and not for_qio_shih: # 平舌话 ieh 混入 ih
    gae = ''
    yen = 'ih'
  elif shen == '' and yen == 'ieh': # 零声母 ieh 混入 ih
    yen = 'ih'
  elif shen in ['z', 'c', 's', 'zh', 'ch', 'sh'] and yen in ['in', 'ih', 'ae', 'aen', 'aeh']: # 咸山摄腭化
    shen = ngah_hua[shen]
    if gae == 'u':
      gae = 'y'
    elif yen[0] != 'i':
      gae = 'i'
  elif shen == 'v' and yen in ['a', 'an', 'ah']: # v、u之别
    shen = ''
    gae = 'u'
  elif cz == '你' and shen == 'n' and yen == 'ii': # “你”训读nen3
    yen = 'en'
  elif yen == 'ii': # ii裂化
    yen = 'ei'
  elif shen == 'h' and yen == 'v': # 呼夫不分
    shen = 'f'
  elif shen == 'r' and yen in ['in', 'ih']: # 日母脱落
    shen = ''
  elif shen in ['d', 't'] and yen == 'i': # di->ji、ti->qi
    shen = ngah_hua[shen]
  elif shen in ['d', 't', 'n', 'l'] and gae == 'u' and yen == 'ei': # 合口脱落
    gae = ''
  elif shen == 'l' and yen == 'y': # ly -> lei
    yen = 'ei'

  shen = pien_shih[shen] # 平翘舌不分
  if shen == '' and yen == 'r': # 独立音节儿缀
    yen = 'er'
  elif yen == 'r':
    yen = 'z'
  return (shen, gae, yen, tio)

def 如皋(cz, pien_ien):
  if pien_ien == 'r': # 儿化
    return '˞'

  shen, gae, yen, tio = parse_pien_ien(pien_ien)
  if tio == '6': # 阳去并入阴平
    tio = '1'

  shen = pien_shih[shen] # 平翘舌不分
  if yen == 'r':
    yen = 'z'

  if shen == 'h' and yen == 'v': # 呼夫不分
    shen = 'f'
  elif shen == 'n' and yen == 'v': # nv -> nu
    yen = 'u'
  elif gae == '' and yen == 'eu': # eu -> ei
    yen = 'ei'
  elif gae == 'i' and yen == 'eu': # ieu -> iu
    gae = 'y'
    yen = 'u'
  elif gae == 'i' and yen in ['un', 'uh']: # 撮口介音
    gae = 'y'
  elif cz == '里' and shen == 'l' and yen == 'ii': # “里lii”混入“的”
    shen = 'd'
    yen = 'ei'
  elif yen == 'ii': # ii裂化
    yen = 'ei'

  if shen == '' and yen == 'v':
    result = 'ʋu'
  else:
    ipa_yen = tae_rv_ipa.tae_rv_ipa_yen.copy()
    ipa_yen['v'] = 'u'
    ipa_yen['ei'] = 'ei'
    ipa_yen['aen'] = 'e\u0303'
    ipa_yen['aeh'] = 'eʔ'
    ipa_yen['on'] = 'ɔŋ'
    ipa_yen['en'] = 'əŋ'
    result = tae_rv_ipa.tae_rv_ipa_shen[shen] + tae_rv_ipa.tae_rv_ipa_gae[gae] + ipa_yen[yen]

  result = result + tio
  return result

def 泰县(cz, pien_ien):
  shen, gae, yen, tio = parse_pien_ien(pien_ien)
  if tio == '6': # 阳去并入阴平
    tio = '1'

  shen = pien_shih[shen] # 平翘舌不分
  if shen == '' and yen == 'r': # 独立音节儿缀
    yen = 'er'
  elif yen == 'r':
    yen = 'z'

  if shen == 'n' and yen == 'v': # nv -> nu
    yen = 'u'

  if shen == 'l': # NL不分
    shen = 'n'

  if yen == 'i': # 舌尖化
    yen = 'z'
    if shen in ['j', 'q', 'x']:
      shen = shih_jin_hua[shen]

  if shen == 'ng' and cz not in ['吖']: # ng脱落
    shen = ''

  if cz == '子' and tio == '':
    yen = 'ae'
  elif cz == '的' and shen + gae + yen + tio == 'dii':
    yen = 'ih'
  elif shen == 'h' and yen == 'v': # 呼夫不分
    shen = 'f'
  elif shen == 'm' and yen == 'eu': # meu -> mu
    yen = 'u'
  elif shen in ['z', 'c', 's'] and gae == 'u' and yen in ['a', 'ae', 'aeh', 'aen', 'ah', 'an', 'ei', 'eh', 'en']: # 合口混入撮口
    shen = ngah_hua[shen]
    gae = 'y'
  elif shen == 'v' and yen in ['a', 'an', 'ah']: # v、u之别
    shen = ''
    gae = 'u'
  elif shen == '' and gae + yen in ['y', 'yeh', 'yen']: # 增生r
    shen = 'r'
  elif shen + gae + yen == 'ruei': # ruei -> ryei
    gae = 'y'
  elif shen in ['z', 'c', 's'] and yen in ['in', 'ih']: # 咸山摄腭化
    shen = ngah_hua[shen]
  elif shen == 'r' and yen in ['in', 'ih']: # 日母脱落
    shen = ''
  elif shen == 'r' and yen == 'eh': # reh -> ryeh
    gae = 'y'
  elif gae == 'i' and yen in ['un', 'uh']: # 撮口介音
    gae = 'y'
  elif gae == 'i' and yen == 'eh' and cz not in '吃': # ieh 混入 ih
    gae = ''
    yen = 'ih'

  if gae == 'i' and yen == 'en':
    result = tae_rv_ipa.tae_rv_ipa_shen[shen] + 'iŋ'
  else:
    ipa_yen = tae_rv_ipa.tae_rv_ipa_yen.copy()
    ipa_yen['ah'] = 'ɑʔ'
    ipa_yen['an'] = 'ɑŋ'
    ipa_yen['ae'] = 'e'
    ipa_yen['aeh'] = 'æʔ'
    ipa_yen['en'] = 'əŋ'
    ipa_yen['ih'] = 'iɪʔ'
    ipa_yen['in'] = 'iɪ\u0303'
    ipa_yen['on'] = 'oŋ'
    ipa_yen['u'] = 'o'
    ipa_yen['un'] = 'o\u0303'
    ipa_yen['v'] = 'u'
    result = tae_rv_ipa.tae_rv_ipa_shen[shen] + tae_rv_ipa.tae_rv_ipa_gae[gae] + ipa_yen[yen]

  result = result + tio
  return result

def 兴化(cz, pien_ien):
  shen, gae, yen, tio = parse_pien_ien(pien_ien)

  shen = pien_shih[shen] # 平翘舌不分
  if shen == '' and yen == 'r': # 独立音节儿缀
    yen = 'er'
  elif yen == 'r':
    yen = 'z'

  if shen == 'n' and yen == 'v': # nv -> nu
    yen = 'u'

  if shen in ['n', 'r']: # NLR不分
    shen = 'l'

  if shen == 'ng' and cz not in ['吖']: # ng脱落
    shen = ''

  if shen not in ['j', 'q', 'x', ''] and gae + yen in ['ien', 'ieh']: # ien->in，ieh->ih
    gae = ''
    yen = 'i' + yen[1:]
  elif gae == 'i' and yen in ['un', 'uh', 'oh']: # 撮口介音
    gae = 'y'
  elif shen in ['d', 't', 'l'] and yen in ['i', 'ii']: # i裂化
    yen = 'ei'
  elif shen == 'v': # v、u之别
    assert(gae == '')
    shen = ''
    gae = 'u'

  if gae == 'i' and yen == 'en':
    result = tae_rv_ipa.tae_rv_ipa_shen[shen] + 'in'
  elif gae == 'y' and yen == 'en':
    result = tae_rv_ipa.tae_rv_ipa_shen[shen] + 'yn'
  else:
    ipa_yen = tae_rv_ipa.tae_rv_ipa_yen.copy()
    ipa_yen['an'] = 'aŋ'
    ipa_yen['aeh'] = 'æʔ'
    ipa_yen['ei'] = 'əi'
    ipa_yen['en'] = 'ən'
    ipa_yen['eu'] = 'ɤ'
    ipa_yen['i'] = 'i'
    ipa_yen['ih'] = 'iɪʔ'
    ipa_yen['in'] = 'iɪ\u0303'
    ipa_yen['on'] = 'oŋ'
    ipa_yen['u'] = 'o'
    ipa_yen['uh'] = 'uʔ'
    ipa_yen['un'] = 'u\u0303'
    ipa_yen['v'] = 'u'
    result = tae_rv_ipa.tae_rv_ipa_shen[shen] + tae_rv_ipa.tae_rv_ipa_gae[gae] + ipa_yen[yen]

  result = result + tio
  return result

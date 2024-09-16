import re
from collections import defaultdict
import tae_rv_ipa

def parse_pien_ien(ien):
  match = re.match(r"^([bpmfvdtnlzcsjqxrgkh]|zh|ch|sh|ng|)(i|u|y|)([aeiouvyzr][a-z]*)(\d|)$", ien)
  if match is None:
    raise Exception(f"Unrecogonized ien: {ien}")
  return match.groups()

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
  if cz == '儿' and shen + gae + yen + tio == 'r':
    return '˞'

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
  elif cz in '皱邹绉诌骤瘦': # 流摄庄三归精组，平舌话不辖“愁”字，翘舌话辖“愁”字
    shen = pien_shih[shen]
    yen = 'ou'
  elif cz == '愁' and for_qio_shih:
    shen = 'c'
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
  elif shen == 'n' and yen == 'v': # 怒懦不分
    yen = 'ou'
  elif shen == 'l' and yen == 'i' and for_qio_shih: # 翘舌话 li -> i
    shen = ''
  elif yen == 'ieh' and not for_qio_shih: # 平舌话 ieh 混入 ih
    yen = 'ih'
  elif shen == '' and yen == 'ieh': # 零声母 ieh 混入 ih
    yen = 'ih'
  elif shen in ['z', 'c', 's', 'zh', 'ch', 'sh'] and yen in ['in', 'ih', 'ae', 'aen', 'aeh']: # 山摄腭化
    shen = ngah_hua[shen]
    if yen[0] != 'i':
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
  elif shen in ['d', 't'] and yen == 'i':
    shen = ngah_hua[shen]
  shen = pien_shih[shen]
  if shen == '' and yen == 'r':
    yen = 'er'
  if yen == 'r':
    yen = 'z'
  return (shen, gae, yen, tio)

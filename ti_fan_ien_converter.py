import re
from collections import defaultdict

def parse(ien):
  match = re.match(r"^([bpmfvdtnlzcsjqxrgkh]|zh|ch|sh|ng|)([aeiouvyzr][a-z]*)(\d)?$", ien)
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

shih_jin_hua = keydefaultdict(lambda k: k)
shih_jin_hua['j'] = 'z'
shih_jin_hua['q'] = 'c'
shih_jin_hua['x'] = 's'

ien_ipa = {
  'b': 'p',
  'p': 'pʰ',
  'm': 'm',
  'f': 'f',
  'v': 'ʋ',
  'd': 't',
  't': 'tʰ',
  'n': 'n',
  'l': 'l',
  'z': 't͡s',
  'c': 't͡sʰ',
  's': 's',
  'j': 't͡ɕ',
  'q': 't͡ɕʰ',
  'x': 'ɕ',
  'zh': 'ʈ͡ʂ',
  'ch': 'ʈ͡ʂʰ',
  'sh': 'ʂ',
  'r': 'ɻ',
  'g': 'k',
  'k': 'kʰ',
  'h': 'x',
  'ng': 'ŋ',
}
yen_teu_ipa = {
  'i': 'i',
  'u': 'u',
  'y': 'y',
}
yen_heh_ipa = {
  'a': 'a',
  'ae': 'ɛ',
}

def 泰兴(cz, ien, for_qio_shih = False):
  shen, yen, tio = parse(ien)
  # print(ien)
  # print(shen, yen, tio)
  if tio == '6': # 阳去并入阴平
    tio = '1'
  if cz in '蛆取趣娶趋聚徐咀' and shen in ['j', 'q', 'x'] and yen == 'y': # 遇摄分尖团
    shen = shih_jin_hua[shen]
    yen = 'uei'
  elif cz in '皱邹绉诌骤瘦': # 流摄庄三归精组，平舌话不辖“愁”字，翘舌话辖“愁”字
    shen = pien_shih[shen]
    yen = 'ou'
  elif cz == '愁' and for_qio_shih:
    shen = 'c'
    yen = 'ou'
  elif shen in ['zh', 'ch', 'sh'] and yen == 'eu': # 流摄翘舌转舌面
    shen = ngah_hua[shen]
    yen = 'iou'
  elif shen in ['d', 't', 'n', 'l', 'g', 'k', 'h', 'ng'] and yen == 'eu': # 流摄转ei
    yen = 'ei'
  elif yen == 'u': # 果摄转ou
    yen = 'ou'
  elif yen == 'eu': # 未转ei的eu，也书写为ou。韵母格局与普通泰如不同，区别书写。
    yen = 'ou'
  elif shen == 'n' and yen == 'v': # 怒懦不分
    yen = 'ou'
  elif shen == 'l' and yen == 'i': # 利义不分
    shen = ''
  elif yen == 'ieh' and not for_qio_shih: # 平舌话 ieh 混入 ih
    yen = 'ih'
  elif shen == '' and yen == 'ieh': # 零声母 ieh 混入 ih
    yen = 'ih'
  elif shen in ['z', 'c', 's', 'zh', 'ch', 'sh'] and yen in ['in', 'ih', 'ae', 'aen', 'aeh']: # 山摄腭化
    shen = ngah_hua[shen]
    yen = 'i' + yen
  elif shen == 'v' and yen in ['a', 'an', 'ah']: # v、u之别
    shen = ''
    yen = 'u' + yen
  elif cz == '你' and shen == 'n' and yen == 'ii': # “你”训读nen3
    yen = 'en'
  elif yen == 'ii': # ii裂化
    yen = 'ei'
  elif shen == 'h' and yen == 'v': # 呼夫不分
    shen = 'f'
  shen = pien_shih[shen]
  if yen == 'r':
    yen = 'z'
  # print(shen, yen, tio)
  if tio:
    return shen + yen + tio
  else:
    return shen + yen

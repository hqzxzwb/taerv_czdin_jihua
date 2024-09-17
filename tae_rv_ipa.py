tae_rv_ipa_shen = {
  '': '',
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

tae_rv_ipa_gae = {
  '': '',
  'i': 'i',
  'u': 'u',
  'y': 'y',
}

tae_rv_ipa_yen = {
  '': '',
  'i': 'ʝ',
  'y': 'y',
  'a': 'a',
  'ii': 'iɪ',
  'in': 'i\u0303',
  'ih': 'iʔ',
  'er': 'ɚ',
  'r': 'ʅ',
  'z': 'ɿ',
  'v': 'ʋ',
}

__yen_heh = {
  'a': 'a',
  'ae': 'ɛ',
  'e': 'ə',
  'o': 'ɔ',
  'eu': 'ɤɯ',
  'ou': 'ɤɯ',
  'u': 'ʊ',
  'ei': 'əɪ',
}
__yen_vei = {
  '': '',
  'n': '\u0303',
  'h': 'ʔ',
}

for yen_heh in __yen_heh.items():
  for yen_vei in __yen_vei.items():
    tae_rv_ipa_yen[yen_heh[0] + yen_vei[0]] = yen_heh[1] + yen_vei[1]

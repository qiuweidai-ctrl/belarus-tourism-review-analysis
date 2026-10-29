const placeReplacements = [
  ['Mahilioŭ', 'Mogilev'],
  ['Mahiloŭ', 'Mogilev'],
  ['Viciebsk', 'Vitebsk'],
  ['Hrodna', 'Grodno'],
  ['Homiel', 'Gomel'],
  ['Navahrudak', 'Novogrudok'],
  ['Niasviž', 'Nesvizh'],
  ['Polack', 'Polotsk'],
  ['Pružany', 'Pruzhany'],
  ['Dubroŭna', 'Dubrovno'],
  ['Ivianiec', 'Ivenets'],
  ['Iškaldź', 'Ishkald'],
  ['Ikaźń', 'Ikazn'],
  ['Synkavičy', 'Synkovichy'],
  ['Lahojsk', 'Logoisk'],
  ['Brasłaŭ', 'Braslav'],
  ['Čašniki', 'Chashniki'],
  ['Čamjary', 'Chamjary'],
  ['sieĺsaviet', 'Village Council'],
  ['rajon', 'District'],
  ['voblast', 'Region']
]

export const formatPlace = (value) => {
  if (!value) return ''
  return placeReplacements.reduce(
    (text, [source, target]) => text.replaceAll(source, target),
    String(value)
  )
}

export const formatCategory = (value) => {
  const text = String(value || 'other').replaceAll('_', ' ')
  return text.replace(/\b\w/g, (letter) => letter.toUpperCase())
}

export const attractionName = (attraction) => attraction?.name_en || attraction?.name || ''

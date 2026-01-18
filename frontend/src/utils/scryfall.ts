export async function fetchScryfallCard(cardId: string): Promise<any> {
  const res = await fetch(`https://api.scryfall.com/cards/${cardId}`)
  if (!res.ok) throw new Error(`Card fetch failed: ${res.status}`)
  return await res.json()
}

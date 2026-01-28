import { Box, Tooltip, Typography } from '@mui/material'

type Props = {
  cardId?: string | null
  cardName?: string | null
  isImportant?: boolean
  thumbHeight?: number | string
  thumbBorderRadius?: number | string
  thumbOpacity?: number
}

export default function CardImageTooltip(props: Props) {
  const { cardId, cardName, isImportant = false, thumbHeight = 80, thumbBorderRadius = 1, thumbOpacity = 0.6 } = props

  const imgSrcThumb = cardId
    ? `https://cards.scryfall.io/art_crop/front/${cardId.charAt(0)}/${cardId.charAt(1)}/${cardId}.jpg`
    : `https://svgs.scryfall.io/card-symbols/mana.svg`

  const imgSrcNormal = cardId
    ? `https://cards.scryfall.io/normal/front/${cardId.charAt(0)}/${cardId.charAt(1)}/${cardId}.jpg`
    : null

  return (
    <Tooltip
      title={
        <Box>
          {imgSrcNormal ? (
            <Box
              component="img"
              src={imgSrcNormal}
              sx={{ width: 260, height: 'auto', display: 'block', borderRadius: 1 }}
              loading="lazy"
              onError={(e: any) => {
                e.currentTarget.onerror = null
                e.currentTarget.src = `https://svgs.scryfall.io/card-symbols/mana.svg`
              }}
            />
          ) : null}
          <Typography variant="caption" sx={{ display: 'block', mt: 0.5 }}>{cardName ?? cardId}</Typography>
        </Box>
      }
      placement="top"
      arrow
      PopperProps={{ modifiers: [{ name: 'flip', enabled: false }] }}
    >
      {isImportant ? (
        <Box className="rainbow-border" sx={{ display: 'inline-block' }}>
          <Box className="rainbow-inner">
            <Box
              component="img"
              src={imgSrcThumb}
              alt={cardName ?? cardId ?? ''}
              sx={{ height: thumbHeight, width: 'auto', borderRadius: thumbBorderRadius, display: 'block', opacity: thumbOpacity }}
              loading="lazy"
              onError={(e: any) => {
                e.currentTarget.onerror = null
                e.currentTarget.src = `https://svgs.scryfall.io/card-symbols/mana.svg`
              }}
            />
          </Box>
        </Box>
      ) : (
        <Box
          component="img"
          src={imgSrcThumb}
          alt={cardName ?? cardId ?? ''}
          sx={{ height: thumbHeight, width: 'auto', borderRadius: thumbBorderRadius, opacity: thumbOpacity }}
          loading="lazy"
          onError={(e: any) => {
            e.currentTarget.onerror = null
            e.currentTarget.src = `https://svgs.scryfall.io/card-symbols/mana.svg`
          }}
        />
      )}
    </Tooltip>
  )
}

import { defineCollection, defineContentConfig, z } from '@nuxt/content'

export default defineContentConfig({
  collections: {
    landing: defineCollection({
      type: 'page',
      source: 'index.md',
    }),
    docs: defineCollection({
      type: 'page',
      source: { include: '**', exclude: ['index.md'] },
      schema: z.object({
        navigation: z.union([z.boolean(), z.object({ title: z.string().optional(), order: z.number().optional() })]).optional(),
      }),
    }),
  },
})

import type { ContentNavigationItem } from '@nuxt/content'

type Ordered = ContentNavigationItem & { order?: number }

/**
 * Sidebar and search data, loaded once by `app.vue` (and `error.vue`, which replaces it) and provided
 * as `navigation`. The landing page is listed first; the rest follow `navigation.order` in frontmatter.
 */
export async function useDocsNavigation() {
  // No `await` before `provide`: an awaited call drops the component instance that `provide` needs.
  const nav = useAsyncData(
    'navigation',
    async () => {
      const pages = (await queryCollectionNavigation('docs')) as Ordered[]
      pages.sort((a, b) => (a.order ?? 99) - (b.order ?? 99))
      return [{ title: 'Getting started', path: '/', stem: 'index' }, ...pages] as ContentNavigationItem[]
    },
    { default: () => [] },
  )
  const search = useLazyAsyncData('search', () => queryCollectionSearchSections('docs'), { server: false })
  provide('navigation', nav.data)
  await nav
  return { navigation: nav.data, searchFiles: search.data }
}

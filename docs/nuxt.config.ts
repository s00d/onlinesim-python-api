import { readdirSync } from 'node:fs'

const repo = 'onlinesim-python-api'
const docsBase = process.env.NUXT_APP_BASE_URL || (process.env.NODE_ENV === 'production' ? `/${repo}/` : '/')

/** Every content page, so prerender does not depend on link crawling alone. */
const pageRoutes = readdirSync(new URL('./content', import.meta.url))
  .filter((file) => file.endsWith('.md'))
  .map((file) => (file === 'index.md' ? '/' : `/${file.slice(0, -'.md'.length)}`))

export default defineNuxtConfig({
  modules: ['@nuxt/ui', '@nuxt/content', 'nuxt-llms'],

  css: ['~/assets/css/main.css'],

  app: {
    baseURL: docsBase,
    head: {
      htmlAttrs: { lang: 'en' },
      link: [{ rel: 'icon', type: 'image/svg+xml', href: `${docsBase}favicon.svg` }],
    },
  },

  icon: {
    // Bundle every rendered icon: the static host never falls back to the Iconify API.
    clientBundle: {
      scan: true,
      icons: ['simple-icons:pypi', 'simple-icons:python', 'lucide:terminal'],
      sizeLimitKb: 256,
    },
  },

  colorMode: {
    preference: 'system',
  },

  content: {
    build: {
      markdown: {
        toc: { searchDepth: 2 },
        highlight: { langs: ['python', 'bash', 'json'] },
      },
    },
    experimental: {
      sqliteConnector: 'native',
    },
  },

  nitro: {
    prerender: {
      // `numbers.html`, not `numbers/index.html`: GitHub Pages serves `/numbers` without a redirect.
      autoSubfolderIndex: false,
      crawlLinks: true,
      failOnError: true,
      routes: pageRoutes,
    },
  },

  llms: {
    domain: `https://s00d.github.io/${repo}`,
    title: 'onlinesim-python-api',
    description: 'Typed, zero-dependency Python client for the OnlineSim API.',
    sections: [
      {
        title: 'Documentation',
        contentCollection: 'docs',
        contentFilters: [{ field: 'extension', operator: '=', value: 'md' }],
      },
    ],
    full: {
      title: 'onlinesim-python-api — full docs',
      description: 'Complete documentation of the onlinesim-python-api SDK (PyPI: onlinesimru).',
    },
  },

  compatibilityDate: '2025-11-03',
})

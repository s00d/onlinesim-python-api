export default defineAppConfig({
  ui: {
    colors: {
      primary: 'green',
      neutral: 'zinc',
    },
    contentNavigation: {
      slots: { linkTitle: 'text-clip whitespace-normal text-pretty text-start' },
    },
    contentToc: {
      slots: { linkText: 'text-clip whitespace-normal text-pretty' },
    },
    prose: {
      codeIcon: {
        pip: 'i-simple-icons-pypi',
        uv: 'i-lucide-terminal',
        python: 'i-simple-icons-python',
        py: 'i-simple-icons-python',
      },
      // Inline code as a light tint that stays on the text baseline and wraps.
      code: {
        base: 'inline px-1 py-px text-[0.875em] font-medium rounded box-decoration-clone wrap-break-word',
        variants: { color: { neutral: 'border-0 bg-elevated text-highlighted' } },
      },
      a: { base: '[&>code]:text-primary' },
      h2: { slots: { base: 'mt-12 mb-4' } },
      h3: { slots: { base: 'mt-8 mb-2' } },
      table: { slots: { root: 'my-6 rounded-lg border border-default', base: 'border-collapse' } },
      thead: { base: 'bg-elevated/60' },
      th: { base: 'py-2 px-3 align-bottom text-highlighted border-0 border-b first:border-s-0 border-default whitespace-nowrap' },
      td: { base: 'py-2 px-3 align-top leading-6 border-0 border-b first:border-s-0 border-default [&_code]:text-[0.8125rem]' },
      tr: { base: '[&:last-child>td]:border-b-0' },
    },
  },
  site: {
    name: 'onlinesim-python-api',
    github: 'https://github.com/s00d/onlinesim-python-api',
    pypi: 'https://pypi.org/project/onlinesimru/',
    edit: 'https://github.com/s00d/onlinesim-python-api/edit/master/docs/content',
  },
})

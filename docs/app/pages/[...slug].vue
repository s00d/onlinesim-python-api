<script setup lang="ts">
definePageMeta({ layout: 'docs' })

const route = useRoute()
const { site } = useAppConfig()
const path = computed(() => route.path.replace(/(.)\/$/, '$1'))

const { data: page } = await useAsyncData(path.value, () => queryCollection('docs').path(path.value).first())
if (!page.value) {
  throw createError({ statusCode: 404, statusMessage: 'Page not found', fatal: true })
}

const { data: surround } = await useAsyncData(`${path.value}-surround`, () =>
  queryCollectionItemSurroundings('docs', path.value, { fields: ['description'] }),
)

useSeoMeta({
  title: page.value.title,
  description: page.value.description,
  ogTitle: page.value.title,
  ogDescription: page.value.description,
})

const editUrl = computed(() => `${site.edit}/${page.value?.stem}.${page.value?.extension}`)
</script>

<template>
  <UPage v-if="page">
    <UPageHeader :title="page.title" :description="page.description" />

    <UPageBody>
      <ContentRenderer :value="page" />

      <footer class="border-t border-default pt-6 text-sm text-muted">
        <ULink :to="editUrl" target="_blank" class="inline-flex items-center gap-1.5 hover:text-highlighted">
          <UIcon name="i-lucide-square-pen" aria-hidden="true" />
          Edit this page on GitHub
        </ULink>
      </footer>

      <UContentSurround v-if="surround?.some(Boolean)" :surround="surround" />
    </UPageBody>

    <template v-if="page.body?.toc?.links?.length" #right>
      <UContentToc title="On this page" :links="page.body.toc.links" highlight />
    </template>
  </UPage>
</template>

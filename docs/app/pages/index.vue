<script setup lang="ts">
import type { ButtonProps } from '@nuxt/ui'

definePageMeta({ layout: 'docs' })

const { site } = useAppConfig()
const { data: page } = await useAsyncData('landing', () => queryCollection('landing').path('/').first())
if (!page.value) {
  throw createError({ statusCode: 404, statusMessage: 'Page not found', fatal: true })
}

useSeoMeta({
  title: site.name,
  description: page.value.description,
  ogTitle: site.name,
  ogDescription: page.value.description,
})

const links: ButtonProps[] = [
  { label: 'Numbers API', to: '/numbers', trailingIcon: 'i-lucide-arrow-right' },
  { label: 'GitHub', to: site.github, target: '_blank', color: 'neutral', variant: 'outline', icon: 'i-simple-icons-github' },
]
</script>

<template>
  <UPage v-if="page">
    <UPageHeader :title="page.title" :description="page.description" :links="links" />

    <UPageBody>
      <ContentRenderer :value="page" />
    </UPageBody>

    <template v-if="page.body?.toc?.links?.length" #right>
      <UContentToc title="On this page" :links="page.body.toc.links" highlight />
    </template>
  </UPage>
</template>

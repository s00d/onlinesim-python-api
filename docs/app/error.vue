<script setup lang="ts">
import type { NuxtError } from '#app'
import type { ButtonProps } from '@nuxt/ui'

const props = defineProps<{ error: NuxtError }>()

// The error page replaces app.vue: it loads the same navigation for the header and search.
const { navigation, searchFiles } = await useDocsNavigation()

const notFound = computed(() => props.error.statusCode === 404)
useSeoMeta({ title: () => (notFound.value ? 'Page not found' : 'Error'), robots: 'noindex' })

const links: ButtonProps[] = [
  { label: 'Getting started', to: '/', trailingIcon: 'i-lucide-arrow-right' },
  { label: 'Numbers API', to: '/numbers', color: 'neutral', variant: 'outline' },
]
</script>

<template>
  <UApp>
    <AppHeader />
    <UMain>
      <UContainer>
        <UPageHero
          :headline="String(error.statusCode || 500)"
          :title="notFound ? 'Page not found' : 'Something went wrong'"
          :description="notFound ? 'This page does not exist or has moved.' : error.message || 'An unexpected error occurred.'"
          :links="links"
        />
      </UContainer>
    </UMain>
    <ClientOnly>
      <LazyUContentSearch :files="searchFiles" :navigation="navigation" />
    </ClientOnly>
  </UApp>
</template>

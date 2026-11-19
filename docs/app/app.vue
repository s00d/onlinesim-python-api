<script setup lang="ts">
const { site } = useAppConfig()
const { navigation, searchFiles } = await useDocsNavigation()

useHead({
  meta: [{ name: 'viewport', content: 'width=device-width, initial-scale=1' }],
  titleTemplate: (title?: string) => (!title || title === site.name ? site.name : `${title} · ${site.name}`),
})
useSeoMeta({ ogSiteName: site.name, ogType: 'website' })
</script>

<template>
  <UApp>
    <NuxtLoadingIndicator color="var(--ui-primary)" />
    <AppHeader />
    <UMain>
      <NuxtLayout>
        <NuxtPage />
      </NuxtLayout>
    </UMain>
    <ClientOnly>
      <LazyUContentSearch :files="searchFiles" :navigation="navigation" />
    </ClientOnly>
  </UApp>
</template>

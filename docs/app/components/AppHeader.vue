<script setup lang="ts">
import type { ContentNavigationItem } from '@nuxt/content'

const { site } = useAppConfig()
const navigation = inject<Ref<ContentNavigationItem[]>>('navigation')
</script>

<template>
  <UHeader>
    <template #left>
      <NuxtLink to="/" class="flex items-center gap-2 rounded-md p-1 -ms-1" :aria-label="`${site.name} home`">
        <img src="/logo.svg" alt="" width="24" height="24" class="size-6 shrink-0" />
        <span class="font-semibold">{{ site.name }}</span>
      </NuxtLink>
    </template>

    <template #right>
      <UContentSearchButton class="lg:hidden" />
      <UContentSearchButton :collapsed="false" class="hidden lg:flex" />
      <UColorModeButton />
      <UButton
        class="hidden sm:inline-flex"
        icon="i-simple-icons-pypi"
        color="neutral"
        variant="ghost"
        square
        :to="site.pypi"
        target="_blank"
        aria-label="onlinesimru on PyPI"
      />
      <UButton
        icon="i-simple-icons-github"
        color="neutral"
        variant="ghost"
        square
        :to="site.github"
        target="_blank"
        aria-label="onlinesim-python-api on GitHub"
      />
    </template>

    <template #body>
      <UContentNavigation highlight :navigation="navigation" />
    </template>
  </UHeader>
</template>

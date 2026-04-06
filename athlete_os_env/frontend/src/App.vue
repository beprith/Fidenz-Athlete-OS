<template>
  <div class="min-h-screen flex flex-col">
    <header class="border-b border-surface-600 bg-surface-800/80 backdrop-blur-sm sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <router-link to="/" class="flex items-center gap-3 group">
          <img
            src="/fidenz-labs-logo.png"
            alt="Fidenz Labs"
            class="logo-header"
            width="36"
            height="36"
            decoding="async"
          />
          <span class="text-lg font-bold tracking-tight group-hover:text-accent-cyan transition-colors">
            Fidenz Athlete OS
          </span>
        </router-link>
        <nav class="flex items-center gap-6 text-sm">
          <router-link to="/" class="hover:text-accent-cyan transition-colors">Home</router-link>
          <router-link to="/workspace" class="hover:text-accent-cyan transition-colors">Workspace</router-link>
          <router-link to="/squad" class="hover:text-accent-cyan transition-colors">Squad</router-link>
          <div class="pl-4 border-l border-surface-600">
            <SwarmStatusBar />
          </div>
        </nav>
      </div>
    </header>
    <main class="flex-1">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import SwarmStatusBar from './components/SwarmStatusBar.vue'
</script>

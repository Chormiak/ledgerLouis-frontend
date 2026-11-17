<script setup lang="ts">
import { gsap } from 'gsap'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

/** Número que sobe até o valor ao aparecer e pisca verde/vermelho quando muda. Sem animação com "reduzir movimento". */
const props = defineProps<{ value: number | null | undefined; format: (n: number | null | undefined) => string }>()

const el = ref<HTMLElement>()
const text = ref(props.format(props.value))
const shown = { v: 0 }
const still = window.matchMedia('(prefers-reduced-motion: reduce)').matches

function tweenTo(to: number, duration: number) {
  gsap.to(shown, { v: to, duration, ease: 'power2.out', overwrite: true, onUpdate: () => (text.value = props.format(shown.v)) })
}

function flash(up: boolean) {
  const hex = getComputedStyle(document.documentElement).getPropertyValue(up ? '--up' : '--down').trim()
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16))
  gsap.fromTo(el.value!, { backgroundColor: `rgba(${r},${g},${b},0.35)` }, { backgroundColor: `rgba(${r},${g},${b},0)`, duration: 1.2, ease: 'power1.out' })
}

onMounted(() => {
  if (still || props.value == null) return
  tweenTo(props.value, 0.8)
})

watch(() => props.value, (now, before) => {
  if (now == null || before == null || still) {
    gsap.killTweensOf(shown)
    text.value = props.format(now)
    if (now != null) shown.v = now
    return
  }
  if (now === before) return
  tweenTo(now, 0.4)
  flash(now > before)
})

onBeforeUnmount(() => gsap.killTweensOf([shown, el.value]))
</script>

<template>
  <span ref="el" class="rounded px-0.5 -mx-0.5">{{ text }}</span>
</template>
